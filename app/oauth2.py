from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from config import settings
from database import get_db
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app import models, schemas

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algoritm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minute=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encode_jwt = jwt.encode(payload=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt


def verify_access_token(token: str) -> schemas.TokeData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithm=[ALGORITHM])
        extracted_user_id: int | None = payload.get("user_id")

        if extracted_user_id is None:
            raise credentials_exception

        token_data = schemas.TokeData(user_id=int(extracted_user_id))
        return token_data

    except jwt.PyJWTError:
        raise credentials_exception


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> models.User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Verify token & extract ID safely
    token_data = verify_access_token(token)

    # 2. Fetch the real user object from PostgreSQL
    user = db.query(models.User).filter(models.User.id == token_data.user_id).first()

    # 3. Handle valid token, but user deleted/not found in DB
    if user is None:
        raise credentials_exception

    return user
