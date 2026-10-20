'''
memo-app/database.py
----------------------
DB 연결 설정 (SQLAlchemy 2.0 버전 스타일)
'''
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config import settings

# 엔진 → DB와의 커넥션 풀을 관리하는 객체
# pool_pre_ping=True : 풀에서 커넥션을 꺼낼 때 살아있는지 먼저 확인
#                      DB 재시작/유휴 끊김으로 인한 'connection closed' 오류 방지
engine = create_engine(settings.database_url, pool_pre_ping=True)

# 세션 팩토리
# expire_on_commit=False : commit 후에도 객체 속성을 다시 SELECT 하지 않고 그대로 사용
#                          commit 뒤 response로 객체를 반환할 때 편리하다.
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

class Base(DeclarativeBase):
    pass