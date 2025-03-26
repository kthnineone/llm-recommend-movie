backend/
│── app/
│   ├── main.py             # FastAPI 엔트리포인트
│   ├── models.py           # 데이터베이스 모델 정의
│   ├── schemas.py          # Pydantic 데이터 모델 (요청/응답 타입)
│   ├── database.py         # DB 연결 설정
│   ├── routers/            # 엔드포인트 (API 라우터)
│   │   ├── movies.py       # 영화 관련 API
│   │   ├── ratings.py      # 평점 관련 API
│   │   └── users.py        # 사용자 관련 API
│   ├── services/           # 비즈니스 로직 (서비스 계층)
│   ├── core/               # 설정 파일 (환경 변수, 로깅)
│   ├── tests/              # 유닛 테스트 코드
│── .env                    # 환경 변수 파일 (DB 접속 정보 등)
│── requirements.txt        # Python 패키지 목록
│── Dockerfile              # 컨테이너화 설정
│── docker-compose.yml      # 여러 서비스 연동 (DB, 백엔드)
│── README.md               # 프로젝트 설명



