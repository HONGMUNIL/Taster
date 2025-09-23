from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import ExpiredSignatureError, JWTError
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, Token
from app.core.security import hash_password, verify_password, create_access_token, decode_token

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()

@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def signup(body: UserCreate, db: Session = Depends(get_db)):
    exists = db.exec(select(User).where(User.email == body.email)).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(email=body.email, hashed_password=hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/login", response_model=Token)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.exec(select(User).where(User.email == body.email)).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_access_token(subject=user.id)
    return Token(access_token=token)


def get_current_user(
     creds: HTTPAuthorizationCredentials = Depends(security),
     db: Session = Depends(get_db),
) -> User:
    token = creds.credentials
    try:
        data = decode_token(token)
        user_id = int(data.get("sub"))
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Expired token") #에러 명확하게 전달
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user

