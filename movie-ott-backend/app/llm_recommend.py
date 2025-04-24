import os
import time
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
#from database import engine, metadata, database, async_session, init_db
from typing import List, Dict
from database import database, async_session_maker
from models import Users, Movies, Ratings, Recommendations
from datetime import datetime
from sqlalchemy import select, desc, func, insert
from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Depends
from dotenv import load_dotenv


# .env 파일 로드
load_dotenv()

# Load LLM model
# Gemini API Key  
API_KEY = os.getenv("GEMINI_API_KEY")

# Credentials 관련 조치
credentials_path = os.getenv("GEMINI_CREDENTIAL_PATH")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

model_name = "gemini-1.5-flash"
model = ChatGoogleGenerativeAI(model=model_name)

# 원하는 데이터 구조를 정의합니다.
class RecommendationJson(BaseModel):
    items: str = Field(description="유저에 추천할 만한 영화들 목록")
    explanation: str = Field(description="추천의 이유")


# 파서를 설정하고 프롬프트 템플릿에 지시사항을 주입합니다.
# 그러면 Topic 클래스의 템플릿에 맞는 형태로 JSON으로 반환.  
parser = JsonOutputParser(pydantic_object=RecommendationJson)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "당신은 영화 추천 시스템 AI 어시스턴트 입니다. 주어진 영화 리스트 중에서 유저가 좋아할 만한 영화들을 10개 추천하고 그 이유를 간략하게 설명하세요."),
        ("user", "#Format: {format_instructions}\n\n#Movie List: {movie_candidates}\n\n#Question: {question}"),
    ]
)

prompt = prompt.partial(format_instructions=parser.get_format_instructions())

chain = prompt | model | parser  # 체인을 구성합니다.

# APIs of LLM


# 비동기 데이터베이스 의존성
async def get_async_db():
    async with async_session_maker() as session:
        yield session

# 추천 가능한 영화 리스트 가져오기

async def get_all_movie_list(db:  AsyncSession = Depends(get_async_db)):
    try:
        query = (
            select(Movies.movieId, Movies.title, Movies.genre)
            .select_from(Movies)
        )
  
        results = await db.execute(query)
        results = results.all()

        #print(f"results: {results}")
        results_as_dict = []
        for row in results:
            rating_dict = {
                "movieId": row.movieId,
                "title": row.title,
                'genre': row.genre
            }
            results_as_dict.append(rating_dict)

        #print(f"results: {results_as_dict}")
        
        if not results_as_dict:
            return {"message": "No Movie list.",
                'movieList': []} # 없으면 빈칸 리턴 
        return {"message": "Movie list loaded successfully.",
                'movieList': results_as_dict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#all_movie_list = await get_all_movie_list()
#movie_candidates = all_movie_list['movieList'][0:100]
#movie_candidates = [movie['title'] for movie in movie_candidates]
#movie_candidates = ', '.join(movie_candidates)

class MovieCandidateManager:
    def __init__(self):
        self.movie_candidates = None

    async def initialize_candidates(self):
        all_movie_list = await get_all_movie_list(next(get_async_db()))
        if 'movieList' in all_movie_list and all_movie_list['movieList']:
            self.movie_candidates = [movie['title'] for movie in all_movie_list['movieList'][0:100]]
            print(f"Initialized Movie Candidates: {', '.join(self.movie_candidates)}")
        else:
            self.movie_candidates = []
            print("No movies found to initialize candidates.")

    def get_candidates(self):
        if self.movie_candidates is not None:
            print(f"Using existing Movie Candidates: {', '.join(self.movie_candidates)}")
            return self.movie_candidates
        else:
            print("Movie candidates have not been initialized yet.")
            return []

manager = MovieCandidateManager()


# 유저의 rating history 정보 입력 
target_template = {'introduction': '사용자가 높은 평점을 준 영화들은 다음과 같습니다.',
                   'rating_template': '\n{item}: {rating}'}

Base = declarative_base()


# 특정 유저의 rating history를 불러온다 
async def get_rating_history(userId: int, db:  AsyncSession = Depends(get_async_db)):
    try:
        '''
        # 평점이 높은 10개만 리턴하고 영화 정보도 가져온다. 
        '''
        query = (
            select(Ratings.userId, 
                   Ratings.movieId,
                   Ratings.rating,
                   Movies.title,
                   Movies.genre,
                   Ratings.timestamp
                   )
            .select_from(Ratings)
            .join(Movies, Ratings.movieId == Movies.movieId)
            .where(Ratings.userId == userId)
            .order_by(desc(Ratings.rating))
            .limit(10)
        )
  
        results = await db.execute(query)
        rating_history = results.all()

        results_as_dict = []
        for row in rating_history:
            rating_dict = {
                "userId": row.userId,
                "movieId": row.movieId,
                "rating": row.rating,
                "title": row.title,
                "genre": row.genre,
                "timestamp": row.timestamp
            }
            results_as_dict.append(rating_dict)

        #print(f"results: {results}")
        
        if not results_as_dict:
            return {"message": "No Rating history.",
                'rating_history': []} # 없으면 빈칸 리턴 
        return {"message": "Rating history loaded successfully.",
                'rating_history': results_as_dict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 영화 리스트에 있는 영화들의 정보들을 가져온다 
async def get_movie_info(movieList: list, db:  AsyncSession = Depends(get_async_db)):
    try:
        # 영화의 평균 rating을 구하는 서브쿼리
        avg_rating_subquery = (
            select(Ratings.movieId, func.round(func.avg(Ratings.rating), 1).label("meanRating"))
            .group_by(Ratings.movieId)
            .subquery()
        )

        query = (
            select(
                   Movies.movieId,
                   Movies.title,
                   Movies.genre,
                   avg_rating_subquery.c.meanRating # 평균 평점 컬럼 추가 
                   )
            .select_from(Movies)
            .join(avg_rating_subquery, Movies.movieId == avg_rating_subquery.c.movieId, isouter=True)
            .where(Movies.title.in_(movieList))
        )
  
        results = await db.execute(query)
        results = results.all()

        #print(f"results: {results}")
        timestamp_unix = time.time()
        results_as_dict = []
        for row in results:
            rating_dict = {
                "movieId": row.movieId,
                "rating": row.meanRating,
                "title": row.title,
                "genre": row.genre,
                "timestamp": timestamp_unix
            }
            results_as_dict.append(rating_dict)
        print(f'movide info result: {results_as_dict}')
        
        if not results_as_dict:
            return {"message": "No Informations in DB.",
                'movieInfo': []} # 없으면 빈칸 리턴 
        return {"message": "Movie info loaded successfully.",
                'movieInfo': results_as_dict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def convert_movie_list_to_string(movie_list: List[dict]) -> str:
    """
    Convert a list of movie titles to a comma-separated string.
    """
    movie_string = ', '.join([movie['title'] for movie in movie_list])
    return movie_string


def fill_template(target_template, source_data):
    rating_history = source_data['rating_history']
    intro = target_template['introduction']
    rating_template = target_template['rating_template']
    filled_template = intro

    for rating_row in rating_history:
        item = rating_row['title']
        genre = rating_row['genre']
        rating = rating_row['rating']
        filled_rating_template = rating_template.format(item=item, rating=rating)
        filled_template += filled_rating_template
    return filled_template

'''
# Core 방식 
class RecommendedInfo(Base):
    __tablename__ = 'recommendations'

    userId = Column(Integer)
    movieId = Column(Integer)
    meanRating = Column(Float)
    timestamp = Column(String)
    recommenderId = Column(Integer)
    recommenderName = Column(String)
    feedback = Column(String, nullable=True)  # feedback은 선택 사항이므로 nullable=True 설정

    # Primary Key가 될 ID가 별도로 없는 경우 아래와 같은 복합키로 제한하면 된다. 
    __table_args__ = (UniqueConstraint('userId', 'movieId', 'timestamp', name='unique_user_movie_recommend_timestamp'),)

    __mapper_args__ = {
        "primary_key": [userId, movieId, timestamp]
    }

async def insert_recommend(recommendations, userId, db: AsyncSession):
    try:
        recommenderId = 2
        recommenderName = 'LLM-Gemini-Prompt-v1'
        timestamp = datetime.now()

        for movie in recommendations['movieInfo']:
            recommended_movie = RecommendedInfo(
                userId=userId,
                movieId=movie['movieId'],
                meanRating=movie['meanRating'],
                timestamp=timestamp,
                recommenderId=recommenderId,
                recommenderName=recommenderName
            )
            db.add(recommended_movie)  # 세션에 모델 인스턴스 추가

        await db.commit()  # 변경 사항 커밋
        return {"message": "Recommendations added successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
'''

# ORM 방식
async def insert_recommend(recommendations: List[dict], 
                           userId: int, 
                           db: AsyncSession = Depends(get_async_db)):
    try:
        # 사전에 정의된 추천 모델 정보 
        recommenderId = 2
        recommenderName = 'LLM-Gemini-Prompt-v1'

        bulk_insert_data = []
        print(f"recommendations in insert rec: {recommendations}")
        for movie in recommendations:
            recommended_movie = {
                "userId": userId,
                "movieId": movie['movieId'],
                "meanRating": movie['rating'],
                "timestamp": movie['timestamp'],
                "recommenderId": recommenderId,
                "recommenderName": recommenderName
            }
            bulk_insert_data.append(recommended_movie)

        insert_stmt = insert(Recommendations).values(bulk_insert_data)
        await db.execute(insert_stmt)  # 세션에 모델 인스턴스 추가
        await db.commit()  # 변경 사항 커밋

        return {"message": "Recommendations added successfully"}
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))





async def recommend_func(userId: int, db: AsyncSession = Depends(get_async_db)):
    userId = int(userId.userId)
    #print(f"userId: {userId}")
    rating_history = await get_rating_history(userId, db)
    #print(f"rating_history: {rating_history['message']}")
    filled_template = fill_template(target_template, rating_history)
    #print(f'filled_template: {filled_template}')

    #movie_candidates = manager.get_candidates()
    movie_candidates = await get_all_movie_list(db)
    if movie_candidates['movieList'] is None:
        return {"message": "Movie candidates have not been initialized."}
    else:
        movie_candidates = movie_candidates['movieList']
        #print(f"movie_candidates: {movie_candidates}")

    recommended = chain.invoke({"movie_candidates": movie_candidates,
                                "question": filled_template})
    
    print(f"recommended: {recommended}")
    movieList = recommended['items']
    recommendations = await get_movie_info(movieList, db)
    print(f"recommendations with info added: {recommendations['message']}")
    message = await insert_recommend(recommendations['movieInfo'], userId, db)
    return recommendations

