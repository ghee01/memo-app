'''
memo-app/models.py
----------------------
SQLAlchemy 2.0 타입 힌트 스타일

table 2개 → users, memos
'''
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

class User(Base):
    __tablename__ = 'users'

    # Mapped[int] : 파이썬 타입 힌트가 곧 컬럼 타입(Integer)이 된다. (IDE 자동완성/타입검사도 정확해짐)
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    email: Mapped[str] = mapped_column(String(200))
    hashed_password: Mapped[str] = mapped_column(String(255))

    # cascade='all, delete-orphan' : 사용자 삭제 시 메모도 함께 삭제 (고아 데이터 방지)
    memos: Mapped[list['Memo']] = relationship(back_populates='user', cascade='all, delete-orphan')

class Memo(Base):
    __tablename__ = 'memos'

    id: Mapped[int] = mapped_column(primary_key=True)
    # ondelete='CASCADE' : DB 레벨에서도 사용자 삭제 시 메모 삭제
    # index=True : '내 메모 목록' 조회가 user_id로 필터링 되므로 인덱스가 유용하다.
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    title: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(String(1000))

    user: Mapped['User'] = relationship(back_populates='memos')