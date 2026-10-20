'''
memo-app/security.py
----------------------
비밀번호 해시 유틸리티

pwdlib + Argon2id (OWASP 권장 알고리즘)
'''
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

# 사용자 이름이 존재하지 않을 때도 '해시 검증 시간'을 동일하게 쓰기 위한 더미 해시
# (응답 시간의 차이로 '이 아이디는 존재한다'를 추측하는 타이밍 공격 방지)
DUMMY_HASH = password_hash.hash('dummy-password')

def get_password_hash(password: str) -> str:
    """평문 → 해시 (솔트 자동 포함)"""
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """평문과 저장된 해시가 일치하는지 검사"""
    return password_hash.verify(plain_password, hashed_password)