from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session


from app.database import get_db
import app.models as models
import app.schemas as schemas
import app.oauth2 as oauth2
from app.utils import hash_password, verify_password


router = APIRouter(prefix="/users", tag=["Users"])


@router.get("me", response_model=schemas.UserOut)
def get_user(current_user: models.User = Depends(oauth2.get_current_user)):
    return current_user
