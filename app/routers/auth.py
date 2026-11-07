from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import database, models, oauth2, schemas
from app.utils import verify_password

router = APIRouter(tags=["Auth"])


@router.post("/login", response_model=schemas.Token)
def user_login(
    user_credential: schemas.LoginRequest,
    db: Annotated[Session, Depends(database.get_db)],
):
    user_db = (
        db.query(models.User).filter(models.User.email == user_credential.email).first()
    )

    if not user_db or not verify_password(
        user_credential.password, user_db.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = oauth2.create_access_token(data={"user_id": user_db.id})
    return {"access_token": access_token, "token_type": "bearer"}
