from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from jose import jwt, JWTError

from apps.api.core.db import get_db
from apps.api.core.security import get_password_hash, verify_password, create_access_token, generate_refresh_token, get_current_user
from apps.api.core.config import settings
from apps.api.models.user import User
from apps.api.models.refresh_token import RefreshToken
import hashlib
from datetime import datetime, timezone, timedelta

router = APIRouter(tags=["auth"])

class UserCreate(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshRequest(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: str
    email: str
    
    class Config:
        from_attributes = True


@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserResponse(id=str(new_user.id), email=new_user.email)

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(subject=user.id)
    raw_token, token_hash = generate_refresh_token()
    
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    rt = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at
    )
    db.add(rt)
    db.commit()
    
    return {"access_token": access_token, "refresh_token": raw_token, "token_type": "bearer"}

@router.post("/refresh", response_model=Token)
def refresh(request: RefreshRequest, db: Session = Depends(get_db)):
    token_hash = hashlib.sha256(request.refresh_token.encode()).hexdigest()
    rt = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    
    now = datetime.now(timezone.utc)
    if not rt or rt.revoked_at or rt.expires_at < now:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
        
    # Revoke old token
    rt.revoked_at = now
    rt.last_used_at = now
    db.add(rt)
    
    # Issue new tokens
    access_token = create_access_token(subject=rt.user_id)
    new_raw, new_hash = generate_refresh_token()
    
    new_rt = RefreshToken(
        user_id=rt.user_id,
        token_hash=new_hash,
        expires_at=now + timedelta(days=30)
    )
    db.add(new_rt)
    db.commit()
    
    return {"access_token": access_token, "refresh_token": new_raw, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(id=str(current_user.id), email=current_user.email)
