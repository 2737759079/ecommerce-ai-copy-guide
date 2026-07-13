from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.address import Address
from app.schemas import AddressCreate, AddressOut
from app.utils.security import get_current_user

router = APIRouter()


@router.get("", response_model=List[AddressOut])
def list_addresses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Address).filter(Address.user_id == current_user.id).order_by(Address.is_default.desc(), Address.created_at.desc()).all()


@router.post("", response_model=AddressOut)
def create_address(payload: AddressCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if payload.is_default:
        db.query(Address).filter(Address.user_id == current_user.id).update({"is_default": False})
    address = Address(user_id=current_user.id, **payload.model_dump())
    db.add(address)
    db.commit()
    db.refresh(address)
    return address


@router.put("/{address_id}", response_model=AddressOut)
def update_address(address_id: int, payload: AddressCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    address = db.query(Address).filter(Address.id == address_id, Address.user_id == current_user.id).first()
    if not address:
        raise HTTPException(status_code=404, detail="地址不存在")
    if payload.is_default:
        db.query(Address).filter(Address.user_id == current_user.id, Address.id != address_id).update({"is_default": False})
    for k, v in payload.model_dump().items():
        setattr(address, k, v)
    db.commit()
    db.refresh(address)
    return address


@router.delete("/{address_id}")
def delete_address(address_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    address = db.query(Address).filter(Address.id == address_id, Address.user_id == current_user.id).first()
    if not address:
        raise HTTPException(status_code=404, detail="地址不存在")
    db.delete(address)
    db.commit()
    return {"ok": True}
