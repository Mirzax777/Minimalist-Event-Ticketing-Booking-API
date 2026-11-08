from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app import models, oauth2, schemas
from app.database import get_db
from app.utils import hash_password

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=schemas.UserOut)
def get_user(
    current_user: Annotated[
        models.User,
        Depends(oauth2.get_current_user),
    ],
):
    return current_user


# CREATE USER
@router.post("", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(
    user: schemas.UserCreate,
    db: Annotated[Session, Depends(get_db)],
):
    existing_user = (
        db.query(models.User).filter(models.User.email == user.email).first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email Already Registered"
        )

    new_user = models.User(
        email=user.email, hashed_password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# UPDATE CURRENT LOGGED-IN USER
@router.put("/me", response_model=schemas.UserOut)
def update_user(
    current_user: Annotated[models.User, Depends(oauth2.get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    user: schemas.UserUpdate,
):
    update_data = user.model_dump(exclude_unset=True)

    if "password" in update_data:
        raw_password = update_data.pop("password")
        update_data["hashed_password"] = hash_password(raw_password)

    for key, value in update_data.items():
        setattr(current_user, key, value)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return current_user


# DELETE CURRENT LOGGED-IN USER
@router.delete("/me", status_code=status.HTTP_204_NO_CONTETNT)
def delete_user(
    current_user: Annotated[models.User, Depends(oauth2.get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    db.delete(current_user)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
