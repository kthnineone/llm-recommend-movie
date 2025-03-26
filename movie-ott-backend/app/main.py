# FastAPI로 엔드포인트 작성  

from typing import List, Dict
from datetime import datetime
from pydantic import BaseModel, Field
#from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.declarative import declarative_base
#from app.database import database, engine, metadata
#from app.models import movies, users, ratings
from database import engine, metadata, database, async_session, init_db
from models import movies, users, ratings, recommendations
import schemas
from llm_recommend import recommend_func
from sqlalchemy.orm import aliased


'''SQLAlchemy의 ORM 방식 사용  
SELECT * FROM table1 WHERE userId == 1;
대신 query.select().where(table1.userId == 1) 방식으로 사용  
'''

# FastAPI 시작  
app = FastAPI()

origins = [
    "http://localhost:5173",  # Vite 개발 서버
    "http://127.0.0.1:5173",  # 다른 로컬 주소
    "https://your-production-frontend.com"  # 배포 환경에서는 실제 도메인
]


app.add_middleware(
    CORSMiddleware,
    #allow_origins=["*"],  # 모든 도메인 허용
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # 모든 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)



@app.on_event("startup")
async def startup_event():
    try:
        await init_db()  # 데이터베이스 초기화
        await database.connect()  # 데이터베이스 연결
        print("Database connection established")
    except Exception as e:
        print(f"Startup error: {str(e)}")
        raise e

# 종료 시 연결 해제
@app.on_event("shutdown")
async def shutdown_event():
    await database.disconnect()
    
@app.get("/")
def read_root():
    return {"message": "Welcome to the LLM-based Movie Recommendation System\ndata is movielens-1m"}


@app.get("/api/search", response_model=List[dict])
async def search_movies(query: str):
    if not query:
        raise HTTPException(status_code=400, detail="검색어를 입력해주세요")
    
    try:
        # ILIKE를 사용하여 대소문자 구분 없이 검색
        search_term = f"%{query}%"
        query = movies.select().where(
            movies.c.title.ilike(search_term) |  # 제목 검색
            movies.c.genre.ilike(search_term)    # 장르 검색
        )
        
        results = await database.fetch_all(query)
        # Record 객체를 딕셔너리로 변환
        results_as_dict = [dict(row) for row in results]
        
        if not results_as_dict:
            return [] # 없으면 빈칸 리턴 
            
        return results_as_dict
        
    except Exception as e:
        print(f"Search error: {str(e)}")  # 서버 로그에 에러 출력
        raise HTTPException(status_code=500, detail="검색 중 오류가 발생했습니다")


class UserId(BaseModel):
    userId: str

from llm_recommend import get_rating_history, fill_template, chain, get_movie_info, insert_recommend

@app.post('/api/rating_history')
async def rate_history(user_id: UserId):
    return await get_rating_history(user_id.userId)


@app.post('/api/recommend')
async def create_recommend(user_id: UserId):
    return await recommend_func(user_id)


@app.get('/api/recommended')
async def get_recommend(userId: str):
    if not userId:
        raise HTTPException(status_code=400, detail="검색어를 입력해주세요")
    
    try:
        userId = int(userId)
        # recommendations 테이블의 meanRating 컬럼에 대한 별칭 생성, AS 역할 
        '''rating_alias = aliased(recommendations.c.meanRating, name='rating')
        위와 같이 aliased를 Column 객체에 씌우면 
        아래 에러가 발생한다.
        Search error: Neither 'Column' object nor 'Comparator' object has an attribute 'mapper'
        아래 코드가 올바른 코드 '''
        rating_alias = recommendations.c.meanRating.label("rating")

        query = (select(
                   movies.c.movieId,
                   movies.c.title,
                   rating_alias, # 평균 평점 컬럼 추가 
                   movies.c.genre
                   )
            .select_from(recommendations)
            .join(movies, recommendations.c.movieId == movies.c.movieId, isouter=True)
            .where(recommendations.c.userId == userId)  # 필터링 조건 추가
        )
        
        results = await database.fetch_all(query)
        # Record 객체를 딕셔너리로 변환
        results_as_dict = [dict(row) for row in results]
        
        if not results_as_dict:
            return [] # 없으면 빈칸 리턴 
            
        return results_as_dict
        
    except Exception as e:
        print(f"Search error: {str(e)}")  # 서버 로그에 에러 출력
        raise HTTPException(status_code=500, detail="검색 중 오류가 발생했습니다")
    



class Rating(BaseModel):
    userId: int
    movieId: int
    rating: float #int
    #timestamp: datetime = Field(default_factory=datetime.now) #기본값 설정 
    timestamp: str


@app.post('/api/test')
async def crate_multiple(rating: Rating):
    try:
        result = rating.rating * 2
        return {'message': 'multiplication successfully',
                'status_code': 201,
                'result': result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/api/ratings")
async def create_rating(rating: Rating):
    '''
    if not rating:
        raise HTTPException(status_code=404, detail='No rating object')
    else:
        raise HTTPException(status_code=200, detail='Right object')
    '''
    try:
        query = ratings.insert().values(
            userId=rating.userId,
            movieId=rating.movieId,
            rating=rating.rating,
            timestamp=rating.timestamp
        )
        await database.execute(query)
        return {"message": "Rating added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

