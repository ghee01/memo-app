'''
memo-app/schemas.py
----------------------
요청/응답 데이터 검증 스키마 (Pydantic v2)
'''
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserCreate(BaseModel):
    """
    회원가입 요청 바디

    Field로 길이 제약을 건다. 위반 시 FastAPI가 자동으로 422 응답
    email은 이미 있는 EmailStr로 이메일 형식을 검사
    """
    username: str = Field(min_length=3, max_length=100)     # 3~100자
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)     # 해시 전 평문 비밀번호 (8~128자)

class UserLogin(BaseModel):
    """로그인 요청 바디"""
    username: str
    password: str

class MemoCreate(BaseModel):
    """
    메모 생성
    DB 컬럼 길이(100/1000)와 맞춰두면, DB 오류(500) 대신 422가 반환된다.
    """
    title: str = Field(min_length=1, max_length=100)    # 1~100자
    content: str = Field(min_length=1, max_length=1000) # 1~1000자

class MemoUpdate(BaseModel):
    """메모 부분 수정(PATCH), 보낸 필드만 바꾼다."""
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default=None, min_length=1, max_length=1000)

class MemoRead(BaseModel):
    """메모 응답 모델, response_model로 지정하면 이 필드만 JSON으로 나간다."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str

class Message(BaseModel):
    """{'message':'...'} 형태의 단순한 응답"""
    message: str