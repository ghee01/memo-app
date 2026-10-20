'''
memo-app/config.py
----------------------
pydantic-settings로 환경변수 .env 파일에서 읽어온다.
'''
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # .env 파일을 utf-8로 읽고, 정의되지 않은 키가 있어도 무시한다.
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # 기본값은 로컬 개발용, 실제 값은 .env에서 덮어쓴다.
    # postgresql+psycopg:// : SQLAlchemy에게 postgresql+psycopg3 드라이버를 사용하라는 뜻
    database_url: str='postgresql+psycopg://memo_user:change-me@localhost:5432/my_memo_app'

    # SecretStr → print 함수나 log에 찍혀도 '********'로 가려지는 타입
    secret_key: SecretStr=SecretStr('dev-only-change-me')

    # 세션 쿠키 유효 시간(초), 기본 14일
    session_max_age: int=60 * 60 * 24 * 14

# 모듈 import 할 때 한 번만 생성해서 앱 전체가 공유한다.
settings = Settings()