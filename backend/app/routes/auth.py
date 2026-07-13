from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas import UserCreate, UserLogin, UserOut, PasswordReset, Token, UserPasswordUpdate
from app.utils.security import verify_password, get_password_hash, create_access_token, get_current_user
from app.utils.helpers import save_upload_file, generate_user_display_id

router = APIRouter()


@router.post("/register", response_model=UserOut)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if not payload.nickname:
        raise HTTPException(status_code=400, detail="昵称不能为空")
    if db.query(User).filter(User.nickname == payload.nickname).first():
        raise HTTPException(status_code=400, detail="昵称已存在")
    display_id = generate_user_display_id(db)
    user = User(
        username=display_id,
        display_id=display_id,
        password_hash=get_password_hash(payload.password),
        nickname=payload.nickname,
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.nickname == payload.username).first()
    if not user:
        user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="账号或密码错误")
    if user.role != payload.role:
        raise HTTPException(status_code=403, detail="身份不匹配")
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return Token(access_token=token, token_type="bearer", role=user.role)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/forgot-password")
def forgot_password(payload: PasswordReset, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.nickname == payload.username).first()
    if not user:
        user = db.query(User).filter(User.username == payload.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="账号不存在")
    return {"ok": True, "username": user.username}


@router.post("/reset-password")
def reset_password(payload: PasswordReset, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.nickname == payload.username).first()
    if not user:
        user = db.query(User).filter(User.username == payload.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="账号不存在")
    user.password_hash = get_password_hash(payload.new_password)
    db.commit()
    return {"ok": True}


@router.post("/change-password")
def change_password(payload: UserPasswordUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not verify_password(payload.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="原密码错误")
    current_user.password_hash = get_password_hash(payload.new_password)
    db.commit()
    return {"ok": True}


@router.post("/upload-avatar", response_model=UserOut)
def upload_avatar(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    url = save_upload_file(file, "avatars")
    current_user.avatar_url = url
    db.commit()
    db.refresh(current_user)
    return current_user
