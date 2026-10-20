'''
memo-app/dependencies.py
----------------------
FastAPI 의존성(Depends) 모음

최신 버전으로 업데이트 db: DbSession
→ Annotated로 '타입 별칭'을 만들어두면 라우터에서 한 단어로 재사용할 수 있다.
'''
from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import SessionLocal
from models import User

def get_db() -> Generator[Session, None, None]:
    """요청 1건당 DB세션 1개를 열고, 응답이 끝나면 반드시 닫는다."""
    with SessionLocal() as db:  # with 블록을 벗어나면 db.close() 자동 호출
        yield db

# 타입 별칭 → 라우터 함수 매개변수에 db: DbSession
DbSession = Annotated[Session, Depends(get_db)]

def get_current_user(request: Request, db: DbSession) -> User:
    """세션 쿠키에서 로그인 사용자를 꺼낸다.

    [구버전] 메모 API 4개에서 '세션 확인 -> 사용자 조회 -> 없으면 오류' 코드를 복붙했음.
    [최신]   의존성 하나로 추출 -> 라우터는 `user: CurrentUser` 만 받으면 끝. 중복 제거.
    """
    username = request.session.get("username")
    if username is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="로그인이 필요합니다.")
    # SQLAlchemy 2.0: db.query(User).filter(...).first() (1.x 레거시) -> select() + scalar()
    user = db.scalar(select(User).where(User.username == username))
    if user is None:
        # 세션엔 이름이 있으나 DB 에서 삭제된 경우 -> 세션을 비우고 재로그인 유도
        request.session.clear()
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="사용자를 찾을 수 없습니다.")
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]