from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..models import models, schemas
from ..database import get_db
from typing import List
from uuid import UUID
from .auth import get_current_user

router = APIRouter(prefix="/organizations", tags=["organizations"])

@router.post("/", response_model=schemas.OrganizationRead, status_code=status.HTTP_201_CREATED)
def create_organization(org: schemas.OrganizationCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Only admin can create organizations
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can create organizations")
    if not org.owner_id:
        raise HTTPException(status_code=400, detail="Organization must have an owner")
    owner = db.query(models.User).filter(models.User.id == org.owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Owner user not found")
    db_org = models.Organization(
        name=org.name,
        description=org.description,
        owner_id=org.owner_id
    )
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    # Set owner as org_owner and assign organization_id
    owner.role = 'org_owner'
    owner.organization_id = db_org.id
    db.commit()
    return db_org

@router.get("/", response_model=List[schemas.OrganizationRead])
def list_organizations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Organization).offset(skip).limit(limit).all()

@router.get("/{org_id}", response_model=schemas.OrganizationRead)
def get_organization(org_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    org = db.query(models.Organization).filter(models.Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

@router.put("/{org_id}", response_model=schemas.OrganizationRead)
def update_organization(org_id: UUID, org_update: schemas.OrganizationCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    org = db.query(models.Organization).filter(models.Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    for key, value in org_update.dict().items():
        setattr(org, key, value)
    db.commit()
    db.refresh(org)
    return org

@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organization(org_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    org = db.query(models.Organization).filter(models.Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    db.delete(org)
    db.commit()
    return None
