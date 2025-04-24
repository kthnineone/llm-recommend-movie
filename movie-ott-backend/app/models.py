# ratings, user, movie 등등의 테이블 정의  
'''
databases는 비동기를 지원하는 라이브러리다.  
async와 await가 가능하다.  
반면에 database는 비동기식이다. 
'''

from sqlalchemy import ForeignKey
from sqlalchemy.orm import (
    DeclarativeBase,
    mapped_column,
    Mapped
)

class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = "users"

    userId: Mapped[int] = mapped_column(primary_key=True)
    gender: Mapped[str]
    age: Mapped[int]
    occupation: Mapped[str]
    zipCode: Mapped[str]

class Movies(Base):
    __tablename__ = "movies"

    movieId: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    genre: Mapped[str]

class Ratings(Base):
    __tablename__ = "ratings"

    userId: Mapped[int] = mapped_column(ForeignKey("users.userId"), primary_key=True)
    movieId: Mapped[int] = mapped_column(ForeignKey("movies.movieId"), primary_key=True)
    rating: Mapped[float]
    timestamp: Mapped[int]


class Recommendations(Base):
    __tablename__ = "recommendations"

    userId: Mapped[int] = mapped_column(ForeignKey("users.userId"), primary_key=True)
    movieId: Mapped[int] = mapped_column(ForeignKey("movies.movieId"), primary_key=True)
    meanRating: Mapped[float]
    timestamp: Mapped[str]
    recommenderId: Mapped[int] = mapped_column(ForeignKey("recommenders.id"))
    recommenderName: Mapped[str] = mapped_column(ForeignKey("recommenders.model_name"))
    feedback: Mapped[str] = mapped_column(nullable=True)  # feedback은 선택 사항이므로 nullable=True 설정




'''
# Core 방식 테이블 선언 
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

'''
