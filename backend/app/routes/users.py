from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.schemas import UserOut, AdminCreate, AdminUpdate
from app.utils.security import require_merchant, get_password_hash

router = APIRouter()


@router.get("", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    return db.query(User).all()


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    return db.query(User).filter(User.id == user_id).first()


@router.get("/admins/list", response_model=List[UserOut])
def list_admins(db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    return db.query(User).filter(User.role == "merchant").all()


@router.post("/admins", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_admin(payload: AdminCreate, db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="账号已存在")
    user = User(
        username=payload.username,
        password_hash=get_password_hash(payload.password),
        nickname=payload.nickname or payload.username,
        role="merchant",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/admins/{user_id}", response_model=UserOut)
def update_admin(user_id: int, payload: AdminUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_merchant)):
    user = db.query(User).filter(User.id == user_id, User.role == "merchant").first()
    if not user:
        raise HTTPException(status_code=404, detail="管理员不存在")
    if payload.nickname is not None:
        user.nickname = payload.nickname
    if payload.password:
        user.password_hash = get_password_hash(payload.password)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/admins/{user_id}")
def delete_admin(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_merchant)):
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="不能删除当前登录的管理员账号")
    user = db.query(User).filter(User.id == user_id, User.role == "merchant").first()
    if not user:
        raise HTTPException(status_code=404, detail="管理员不存在")
    db.delete(user)
    db.commit()
    return {"ok": True}
