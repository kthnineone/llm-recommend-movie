import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker
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

# MetaData 객체 생성  
metadata = MetaData()

database = 1

'''
# 동기 엔진
engine = create_engine(DATABASE_URL, echo=True)

# 동기 세션
Session = sessionmaker(bind=engine, expire_on_commit=False)
'''

# 비동기 엔진 생성
engine = create_async_engine(DATABASE_URL, echo=True)  # aiosqlite 사용

# 비동기 세션 생성
async_session_maker = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
# Session = sessionmaker(bind=crm_engine, autocommit=False, autoflush=False, expire_on_commit=False)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    filename='app.log',  # Specify the log file name
    filemode='a',        # Append mode; use 'w' to overwrite the file each time
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


