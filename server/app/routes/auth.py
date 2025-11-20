from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from ..auth import create_access_token, get_password_hash, verify_password
from ..config import get_settings
from ..database import get_session
from ..models import User
from ..schemas import Token, UserCreate, UserRead


router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/register", response_model=UserRead)
def register_user(payload: UserCreate, session: Session = Depends(get_session)) -> User:
    existing = session.exec(select(User).where(User.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = User(
        email=payload.email.lower(),
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
) -> Token:
    user = session.exec(select(User).where(User.email == form_data.username.lower())).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    token = create_access_token(data={"sub": str(user.id)}, expires_delta=access_token_expires)
    return Token(access_token=token)

