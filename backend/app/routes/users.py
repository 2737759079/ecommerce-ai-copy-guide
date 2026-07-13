from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.admin_note import AdminNote
from app.schemas import UserOut, AdminCreate, AdminUpdate, AdminNoteCreate
from app.utils.security import require_merchant, get_password_hash, get_current_user
from app.utils.helpers import generate_user_display_id

router = APIRouter()


@router.get("/admins/list", response_model=List[UserOut])
def list_admins(keyword: str = None, db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    q = db.query(User).filter(User.role == "merchant")
    if keyword:
        q = q.filter((User.username.contains(keyword)) | (User.nickname.contains(keyword)) | (User.display_id.contains(keyword)))
    return q.all()


@router.post("/admins", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_admin(payload: AdminCreate, db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="账号已存在")
    user = User(
        username=payload.username,
        display_id=generate_user_display_id(db),
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


@router.get("/admins/{target_id}/note")
def get_admin_note(target_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_merchant)):
    note = db.query(AdminNote).filter(AdminNote.admin_id == current_user.id, AdminNote.target_admin_id == target_id).first()
    return {"note": note.note if note else ""}


@router.post("/admins/{target_id}/note")
def save_admin_note(target_id: int, payload: AdminNoteCreate, db: Session = Depends(get_db), current_user: User = Depends(require_merchant)):
    if current_user.id == target_id:
        raise HTTPException(status_code=400, detail="不能给自己备注")
    note = db.query(AdminNote).filter(AdminNote.admin_id == current_user.id, AdminNote.target_admin_id == target_id).first()
    if note:
        note.note = payload.note
    else:
        note = AdminNote(admin_id=current_user.id, target_admin_id=target_id, note=payload.note)
        db.add(note)
    db.commit()
    return {"ok": True}


@router.get("", response_model=List[UserOut])
def list_users(keyword: str = None, db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    q = db.query(User)
    if keyword:
        q = q.filter((User.username.contains(keyword)) | (User.nickname.contains(keyword)) | (User.display_id.contains(keyword)))
    return q.all()


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    return db.query(User).filter(User.id == user_id).first()
