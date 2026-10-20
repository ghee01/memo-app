'''
memo-app/main.py
----------------------
앱 진입점

uv 사용, 실행 방법
- 개발 모드(자동 재시작) : uv run fastapi dev main.py
- 운영 모드 : uv run fastapi run main.py

구버전(유비콘 사용, 둘 다 가능)
uvicorn main:app --reload
'''
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from config import settings
from controllers import router
from database import engine

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """앱 시작/종료 시점의 작업을 한 곳에 모은 함수"""
    yield
    # 종료 시 : 커넥션 풀 정리
    engine.dispose()

app = FastAPI(title="마이 메모 앱", lifespan=lifespan)

# 세션 미들웨어: 세션 데이터를 secret_key 로 '서명'한 쿠키에 담는다. (암호화가 아니라 변조 방지)
#  - secret_key : .env 에서 읽음 (코드에 하드코딩 금지)
#  - same_site="lax" : 다른 사이트에서 오는 POST 요청에는 쿠키를 보내지 않아 CSRF 위험 감소
#  - https_only : 운영(HTTPS)에서는 True 로 바꿔 쿠키가 평문 HTTP 로 새지 않게 한다
#  - max_age : 쿠키 유효 기간(초)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key.get_secret_value(),
    same_site='lax',
    https_only=False,
    max_age=settings.session_max_age,
)

app.include_router(router)