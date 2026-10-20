'''
memo-app/controllers.py
----------------------
라우터(컨트롤러): 회원 / 메모 / 페이지 엔드포인트
'''
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from dependencies import CurrentUser, DbSession
from models import Memo, User
from schemas import MemoCreate, MemoRead, MemoUpdate, Message, UserCreate, UserLogin
from security import DUMMY_HASH, get_password_hash, verify_password

router = APIRouter()
templates = Jinja2Templates(directory='templates')

# ----------- 인증 (회원가입 / 로그인 / 로그아웃) ---------------
@router.post('/signup', status_code=status.HTTP_201_CREATED, response_model=Message)
def signup(data: UserCreate, db: DbSession):
    """회원가입 - 성공 시 201 Created"""
    # 먼저 중복 확인
    exists = db.scalar(select(User.id).where(User.username == data.username))
    if exists is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, detail='이미 동일 사용자 이름이 가입되어 있습니다.')

    new_user = User(
        username = data.username,
        email=data.email,
        hashed_password=get_password_hash(data.password),   # 평문은 절대 저장 X
    )
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        # 위 중복 확인과 commit 사이에 같은 이름이 동시에 가입된 경우(경쟁 상태), DB를 유니크 제약이 막아준다.
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, detail='이미 동일 사용자 이름이 가입되어 있습니다.')
    return Message(message='회원가입에 성공했습니다.')

@router.post('/login', response_model=Message)
def login(request: Request, data: UserLogin, db: DbSession):
    """로그인 - 성공하면 서명된 세션 쿠키에 username을 저장한다."""
    user = db.scalar(select(User).where(User.username == data.username))

    # 사용자가 없어도 더미 해시로 verify를 한 번 수행 → 응답 시간 차이로 아이디 존재 여부가 새지 않는다.
    hashed = user.hashed_password if user else DUMMY_HASH
    password_ok = verify_password(data.password, hashed)

    if user is None or not password_ok:
        # 아이디 / 비밀번호 중 무엇이 틀렸는지 알려주지 않는다. (계정 열거 공격 방지)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail='아이디 또는 비밀번호가 틀렸습니다.')

    request.session.clear()  # 기존 세션 폐기 (세션 고정 공격 방지)
    request.session['username'] = user.username
    return Message(message='로그인에 성공했습니다.')

@router.post('/logout', response_model=Message)
def logout(request: Request):
    """로그아웃 - 세션 전체를 비운다."""
    request.session.clear()
    return Message(message="로그아웃되었습니다")

# ----------- 메모 CRUD ---------------
# 모든 메모 API는 user: CurrentUser 하나로 → 로그인 확인 + 사용자 조회가 끝난다.
def get_own_memo_or_404(db: DbSession, memo_id: int, user: User) -> Memo:
    """내 소유의 메모만 조회. 없거나 남의 메모면 404 (존재 여부를 숨긴다)."""
    memo = db.scalar(select(Memo).where(Memo.id == memo_id, Memo.user_id == user.id))
    if memo is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='메모를 찾을 수 없습니다.')
    return memo

@router.post("/memos/", status_code=status.HTTP_201_CREATED, response_model=MemoRead)
def create_memo(data: MemoCreate, user: CurrentUser, db: DbSession):
    memo = Memo(user_id=user.id, title=data.title, content=data.content)
    db.add(memo)
    db.commit()
    return memo

@router.get("/memos/", response_class=HTMLResponse)
def list_memos(request: Request, user: CurrentUser, db: DbSession):
    """내 메모 목록 HTML 페이지."""
    memos = db.scalars(select(Memo).where(Memo.user_id == user.id).order_by(Memo.id.desc())).all()
    # TemplateResponse(request, 템플릿이름, 컨텍스트)
    return templates.TemplateResponse(request, "memos.html", {"memos": memos, "username": user.username})

@router.put("/memos/{memo_id}", response_model=MemoRead)
def update_memo(memo_id: int, data: MemoUpdate, user: CurrentUser, db: DbSession):
    memo = get_own_memo_or_404(db, memo_id, user)
    # exclude_unset=True : 클라이언트가 '실제로 보낸 필드'만 꺼낸다.
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(memo, field, value)
    db.commit()
    return memo

@router.delete("/memos/{memo_id}", response_model=Message)
def delete_memo(memo_id: int, user: CurrentUser, db: DbSession):
    memo = get_own_memo_or_404(db, memo_id, user)
    db.delete(memo)
    db.commit()
    return Message(message="메모가 삭제되었습니다")

# -------------- 페이지 ----------------------
@router.get('/', response_class=HTMLResponse)
def read_rood(request: Request):
    return templates.TemplateResponse(request, 'home.html')

@router.get("/about", response_model=Message)
def about():
    return Message(message="이것은 마이 메모 앱의 소개 페이지입니다.")