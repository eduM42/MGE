from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..models import models, schemas
from ..database import get_db
from .auth import get_password_hash, get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=schemas.UserRead)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
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
        hashed_password=get_password_hash(user.password.get_secret_value())
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# All other user routes should be protected
# Example: get current user (already protected)
# Add more protected user routes as needed, using current_user: models.User = Depends(get_current_user)
