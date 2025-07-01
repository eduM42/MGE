from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from ..models import models, schemas
from ..database import get_db
from .auth import get_password_hash, get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=schemas.UserRead)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if user.role == 'org_owner' and not user.organization_id:
        raise HTTPException(status_code=400, detail="Org Owner must have an organization_id")
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = models.User(
        name=user.name,
        username=user.username,
        email=user.email,
        phone=user.phone,
        address=user.address,
        is_residential=user.is_residential,
        organization_id=user.organization_id,
        role=user.role,
        hashed_password=get_password_hash(user.password.get_secret_value())
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/", response_model=List[schemas.UserRead])
def list_users(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Only admin can see all users
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")
    return db.query(models.User).all()

@router.get("/by_organization/{org_id}", response_model=List[schemas.UserRead])
def list_users_by_organization(org_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Only admin or org_owner of this org can see users
    if current_user.role not in ['admin', 'org_owner']:
        raise HTTPException(status_code=403, detail="Not authorized")
    if current_user.role == 'org_owner' and str(current_user.organization_id) != org_id:
        raise HTTPException(status_code=403, detail="Not authorized for this organization")
    return db.query(models.User).filter(models.User.organization_id == org_id).all()

@router.patch("/{user_id}", response_model=schemas.UserRead)
def update_user(user_id: str, user: dict = Body(...), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    try:
        user_uuid = UUID(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user_id format")
    db_user = db.query(models.User).filter(models.User.id == user_uuid).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    # Only admin or org_owner of the same org can update
    if current_user.role == 'admin' or (current_user.role == 'org_owner' and db_user.organization_id == current_user.organization_id):
        update_data = user
        if update_data.get('role') == 'org_owner' and not update_data.get('organization_id'):
            raise HTTPException(status_code=400, detail="Org Owner must have an organization_id")
        update_data.pop('id', None)
        update_data.pop('username', None)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        db.commit()
        db.refresh(db_user)
        return db_user
    raise HTTPException(status_code=403, detail="Not authorized")

@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    try:
        user_uuid = UUID(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user_id format")
    db_user = db.query(models.User).filter(models.User.id == user_uuid).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    # Only admin or org_owner of the same org can delete
    if current_user.role == 'admin' or (current_user.role == 'org_owner' and db_user.organization_id == current_user.organization_id):
        db.delete(db_user)
        db.commit()
        return
    raise HTTPException(status_code=403, detail="Not authorized")
