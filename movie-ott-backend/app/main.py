# FastAPI로 엔드포인트 작성  

from typing import List, Dict
from datetime import datetime
from pydantic import BaseModel, Field
from sqlalchemy import select, desc, func, insert, delete
from sqlalchemy.orm import aliased, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import async_session_maker
from models import Users, Movies, Ratings, Recommendations
from schemas import RatingBase
import schemas
from llm_recommend import recommend_func, manager


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



# 비동기 데이터베이스 의존성
async def get_async_db():
    async with async_session_maker() as session:
        yield session

'''
@app.on_event("startup")
async def startup_event():
    try:
        async with async_session_maker() as db:
            await manager.initialize_candidates(db)
        print("Database connection established and movie candidates initialized")
    except Exception as e:
        print(f"Startup error: {str(e)}")
        raise e
'''

    
@app.get("/")
def read_root():
    return {"message": "Welcome to the LLM-based Movie Recommendation System\ndata is movielens-1m"}


@app.get("/api/search", response_model=List[dict])
async def search_movies(query: str, db: AsyncSession = Depends(get_async_db)):
    if not query:
        raise HTTPException(status_code=400, detail="검색어를 입력해주세요")
    
    try:
        # ILIKE를 사용하여 대소문자 구분 없이 검색
        search_term = f"%{query}%"
        query = select(Movies).select_from(Movies).where(
            Movies.title.ilike(search_term) |  # 제목 검색
            Movies.genre.ilike(search_term)    # 장르 검색
        )
        
        results = await db.execute(query)
        movies = results.scalars().all()
        print(f"movies: {movies}")
        # Record 객체를 딕셔너리로 변환
        results_as_dict = []
        for movie in movies:
            movie_dict = {
                "movieId": movie.movieId,
                "title": movie.title,
                "genre": movie.genre
            }
            results_as_dict.append(movie_dict)
        
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
async def rate_history(user_id: UserId, db: AsyncSession = Depends(get_async_db)):
    return await get_rating_history(user_id.userId)


@app.post('/api/recommend')
async def create_recommend(user_id: UserId, db: AsyncSession = Depends(get_async_db)):
    return await recommend_func(user_id, db)


@app.get('/api/recommended', response_model=List[dict])
async def get_recommend(userId: str, db: AsyncSession = Depends(get_async_db)):
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
        rating_alias = Recommendations.meanRating.label("rating")

        # CTE 정의
        recommended_movies_cte = (
            select(Recommendations.movieId, Recommendations.meanRating.label("rating"))
            .select_from(Recommendations)
            .where(Recommendations.userId == userId) # userId로 필터링
            .cte("recommended_movies")
        )

        query = (select(
                   Movies.movieId,
                   Movies.title,
                   rating_alias, # 평균 평점 컬럼 추가 
                   Movies.genre
                   )
            .select_from(Movies)
            .join(recommended_movies_cte, Movies.movieId == recommended_movies_cte.c.movieId, isouter=False)
        )
        
        results = await db.execute(query)
        movies = results.all()
        '''
        쿼리 결과를 가져올 때 results.scalars().all()을 사용하면 
        선택한 컬럼 중 첫 번째 컬럼의 값들만 스칼라 형태로 리스트에 담기게 됩니다. 
        현재 select 절의 순서는 Movies.movieId, Movies.title, rating_alias, Movies.genre 이므로, 
        results.scalars().all()은 Movies.movieId의 리스트를 반환할 가능성이 높습니다.
        '''
        #print(f"movies: {movies}")
        # Record 객체를 딕셔너리로 변환
        results_as_dict = []
        for movie in movies:
            movie_dict = {
                "movieId": movie.movieId,
                "title": movie.title,
                "genre": movie.genre
            }
            results_as_dict.append(movie_dict)
        print(f"recommended movies result dict shaped: {results_as_dict}")
        
        if not results_as_dict:
            return [] # 없으면 빈칸 리턴 
            
        return results_as_dict
        
    except Exception as e:
        print(f"Search error: {str(e)}")  # 서버 로그에 에러 출력
        raise HTTPException(status_code=500, detail="검색 중 오류가 발생했습니다")
    


@app.post('/api/test')
async def crate_multiple(rating: RatingBase):
    try:
        result = rating.rating * 2
        return {'message': 'multiplication successfully',
                'status_code': 201,
                'result': result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/api/ratings")
async def create_rating(rating: RatingBase, db: AsyncSession = Depends(get_async_db)):
    '''
    if not rating:
        raise HTTPException(status_code=404, detail='No rating object')
    else:
        raise HTTPException(status_code=200, detail='Right object')
    '''
    try:
        query = insert(Ratings).values(
            userId=rating.userId,
            movieId=rating.movieId,
            rating=rating.rating,
            timestamp=rating.timestamp
        )
        await db.execute(query)
        await db.commit()
        return {"message": "Rating added successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

