# LLM-based Movie Recommender System  

+ LLM을 활용한 영화 추천이 포함된 별점 사이트 구현  
+ 디자인은 배제  
+ FastAPI를 사용해 여러가지 GET과 POST 구현  
+ ORM style SQLAlchemy 적용 

## 기술  

**Frontend**  
+ Typescript   
+ React   
+ Vite  

**Backend**  
+ FastAPI   


**Database**  
+ SQLAlchemy  
+ Sqlite  

**LLM**  
+ Gemini API  

## 기능  

**GET**  
+ 영화 이름으로 검색  
+ 특정 유저에 대한 추천 영화 불러오기  

**POST**  
+ 현재 유저가 인기영화나 추천 영화에 별점을 등록하면 DB에 저장  
+ 특정 유저의 ratings 히스토리를 기반으로 LLM이 영화 추천하여 DB에 저장 (현재 DB에 있는 일부 영화만 대상으로 추천)  


