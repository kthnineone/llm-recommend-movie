from database import database
from models import movies

async def init_test_data():
    await database.connect()
    
    # 테스트 데이터 추가
    query = movies.insert().values([
        {"title": "Toy Story", "genre": "Animation"},
        {"title": "Matrix", "genre": "Action"},
        {"title": "Inception", "genre": "Sci-Fi"}
    ])
    
    await database.execute(query)
    await database.disconnect()

# 스크립트 실행
if __name__ == "__main__":
    import asyncio
    asyncio.run(init_test_data()) 