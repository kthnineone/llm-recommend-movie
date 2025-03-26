# ratings, user, movie 등등의 테이블 정의  
'''
databases는 비동기를 지원하는 라이브러리다.  
async와 await가 가능하다.  
반면에 database는 비동기식이다. 
'''

from sqlalchemy import Table, Column, Integer, String, Float, ForeignKey
#from app.database import metadata
from database import metadata

movies = Table(
    "movies",
    metadata,
    Column("movieId", Integer, primary_key=True),
    Column("title", String),
    Column("genre", String),
)

users = Table(
    "users",
    metadata,
    Column("userId", Integer, primary_key=True),
    Column("gender", String),
    Column("age", Integer),
    Column("occupation", String),
    Column("zipCode", String),
)

ratings = Table(
    "ratings",
    metadata,
    Column("userId", Integer, ForeignKey("users.userId")),
    Column("movieId", Integer, ForeignKey("movies.movieId")),
    Column("rating", Float),
    Column("timestamp", Integer),
)

recommenders = Table(
    "recommender",
    metadata,
    Column("id", Integer, ForeignKey("users.userId")),
    Column("model_name", String),
    Column("is_active", Integer),
    Column("start_date", String),
    Column("end_date", String),
    Column("description", String)
)

recommendations = Table(
    "recommendations",
    metadata,
    Column("userId", Integer, ForeignKey("users.userId")),
    Column("movieId", Integer, ForeignKey("movies.movieId")),
    Column("meanRating", Float),
    Column("timestamp", String),
    Column("recommenderId", String, ForeignKey("recommenders.id")),
    Column("recommenderName", String, ForeignKey("recommenders.model_name")),
)

