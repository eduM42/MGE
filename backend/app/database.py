from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import os
from .models import models
from sqlalchemy.orm import Session
from app.utils.security import get_password_hash

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./test.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Auto-create and auto-update tables
try:
    models.Base.metadata.create_all(bind=engine)
except OperationalError as e:
    print(f"Database error: {e}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_default_admin(db: Session):
    if not db.query(models.User).filter(models.User.username == 'admin').first():
        admin_user = models.User(
            name='Administrator',
            username='admin',
            email='admin@example.com',
            hashed_password=get_password_hash('admin'),
            is_residential=False,
            role='admin'
        )
        db.add(admin_user)
        db.commit()
        print('Default admin user created: admin/admin')

def init_db():
    from app.models import models
    models.Base.metadata.create_all(bind=engine)
    # Create default admin user
    db = SessionLocal()
    create_default_admin(db)
    db.close()

init_db()
