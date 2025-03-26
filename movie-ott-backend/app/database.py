import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, MetaData, create_engine
from sqlalchemy.orm import sessionmaker
from databases import Database
import logging
import os


'''
databases는 비동기를 지원하는 라이브러리다.  
async와 await가 가능하다.  
반면에 database는 동기식이다. 
'''
# 상대 경로로 변경
DATABASE_URL = "sqlite+aiosqlite:///./ott.db"  # 현재 디렉토리에 생성되도록 수정

# 또는 절대 경로 사용
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(f"backend base_dir: {BASE_DIR}")
DATABASE_URL = f"sqlite+aiosqlite:///{os.path.join(BASE_DIR, 'ott.db')}"

database = Database(DATABASE_URL)

# MetaData 객체 생성  
metadata = MetaData()

# 비동기 엔진 생성
engine = create_async_engine(DATABASE_URL, echo=True)  # aiosqlite 사용

# 비동기 세션 생성
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    filename='app.log',  # Specify the log file name
    filemode='a',        # Append mode; use 'w' to overwrite the file each time
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Ensure tables are created
async def init_db():
    try:
        # 데이터베이스 디렉토리 확인 및 생성
        db_path = DATABASE_URL.replace("sqlite+aiosqlite:///", "")
        db_dir = os.path.dirname(os.path.abspath(db_path))
        
        # 디렉토리가 없으면 생성
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
            print(f"Created database directory: {db_dir}")

        # 데이터베이스 연결 및 테이블 생성
        async with engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
            print("Database tables created successfully")
            
        logger.info(f"Database initialized successfully at {db_path}")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise e

async def main():
    try:
        # 데이터베이스 파일이 위치할 디렉토리가 없으면 생성
        db_directory = os.path.dirname(DATABASE_URL.split("///")[1])
        if not os.path.exists(db_directory):
            os.makedirs(db_directory)
        await init_db()
    except Exception as e:
        logger.error(f"Error connecting to the database: {e}")

if __name__ == "__main__":
    asyncio.run(main())

