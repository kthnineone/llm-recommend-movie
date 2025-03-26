from pydantic import BaseModel
from typing import Optional  

class RatingBase(BaseModel):
    userId: int
    movieId: int
    rating: float
    timestamp: int

class RatingCreate(RatingBase):
    pass # 새 평점 추가 시 모든 필드를 받는다.  

class RatingResponse(RatingBase):
    id: int # DB에 저장된 후 반환될 ID  

    class Config:
        orm_mode = True # SQLAlchemy 모델을 Pydantic 모델과 호환되도록 변환  
