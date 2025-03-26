import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from database import engine, metadata, database, async_session, init_db
from models import movies, users, ratings
from datetime import datetime
from sqlalchemy import select, desc, func 
from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from fastapi import HTTPException
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Load LLM model
# Gemini API Key  
API_KEY = os.getenv("GEMINI_API_KEY")

# Credentials 관련 조치
credentials_path = os.getenv("GEMINI_CREDENTIAL_PATH")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

model_name = "gemini-1.5-pro"
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
        ("system", "당신은 영화 추천 시스템 AI 어시스턴트 입니다. 유저가 좋아할 만한 영화들을 10개 추천하고 그 이유를 간략하게 설명하세요."),
        ("user", "#Format: {format_instructions}\n\n#Question: {question}"),
    ]
)

prompt = prompt.partial(format_instructions=parser.get_format_instructions())

chain = prompt | model | parser  # 체인을 구성합니다.

# APIs of LLM
target_template = {'introduction': '사용자가 높은 평점을 준 영화들은 다음과 같아.',
                   'rating_template': '\n{item}: {rating}'}

Base = declarative_base()

# 특정 유저의 rating history를 불러온다 
async def get_rating_history(userId):
    try:
        '''
        # 평점이 높은 10개만 리턴하고 영화 정보도 가져온다. 
        '''
        query = (
            select(ratings.c.userId, 
                   ratings.c.movieId,
                   ratings.c.rating,
                   movies.c.title,
                   movies.c.genre,
                   ratings.c.timestamp
                   )
            .select_from(ratings.join(movies, ratings.c.movieId == movies.c.movieId))
            .where(ratings.c.userId == userId)
            .order_by(desc(ratings.c.rating))
            .limit(10)
        )
  
        results = await database.fetch_all(query)

        print(f"results: {results}")
        results_as_dict = [dict(row) for row in results]
        
        if not results_as_dict:
            return {"message": "No Rating history.",
                'rating_history': []} # 없으면 빈칸 리턴 
        return {"message": "Rating history loaded successfully.",
                'rating_history': results_as_dict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 영화 리스트에 있는 영화들의 정보들을 가져온다 
async def get_movie_info(movieList: list):
    try:
        # 영화의 평균 rating을 구하는 서브쿼리
        avg_rating_subquery = (
            select(ratings.c.movieId, func.round(func.avg(ratings.c.rating), 1).label("meanRating"))
            .group_by(ratings.c.movieId)
            .subquery()
        )

        query = (
            select(
                   movies.c.movieId,
                   movies.c.title,
                   movies.c.genre,
                   avg_rating_subquery.c.meanRating # 평균 평점 컬럼 추가 
                   )
            .select_from(movies)
            .join(avg_rating_subquery, movies.c.movieId == avg_rating_subquery.c.movieId, isouter=True)
            .where(movies.c.title.in_(movieList))
        )
  
        results = await database.fetch_all(query)

        print(f"results: {results}")
        results_as_dict = [dict(row) for row in results]
        
        if not results_as_dict:
            return {"message": "No Informations in DB.",
                'movieInfo': []} # 없으면 빈칸 리턴 
        return {"message": "Movie info loaded successfully.",
                'movieInfo': results_as_dict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

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


async def insert_recommend(recommendations, userId):
    try:
        # with으로 session을 열기 때문에 자동으로 session이 종료된다 
        async with async_session() as session:
            async with session.begin(): # 세션 시작 
                recommenderId = 2
                recommenderName = 'LLM-Gemini-Prompt-v1'
                timestamp = datetime.now().isoformat()

                for movie in recommendations['movieInfo']:
                    recommended_movie = RecommendedInfo(
                        userId=userId,
                        movieId=movie['movieId'],
                        meanRating=movie['meanRating'],
                        timestamp=datetime.now(),
                        recommenderId=recommenderId,
                        recommenderName=recommenderName
                    )
                    session.add(recommended_movie)  # 세션에 모델 인스턴스 추가

                await session.commit()  # 변경 사항 커밋
        #session.close()
        return {"message": "Recommendations added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



async def recommend_func(userId):
    userId = int(userId.userId)
    rating_history = await get_rating_history(userId)
    print(f"rating_history: {rating_history['message']}")
    filled_template = fill_template(target_template, rating_history)
    recommended = chain.invoke({"question": filled_template})
    movieList = recommended['items']
    recommendations = await get_movie_info(movieList)
    message = await insert_recommend(recommendations, userId)
    return recommendations

