from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app import models, oauth2, schemas
from app.database import get_db

router = APIRouter(prefix="/events", tags=["Events"])


# POST / CREATE
@router.post("", status_code=status.HTTP_201_CREATED, response_model=schemas.EventOut)
def create_event(
    event: schemas.EventCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(oauth2.get_current_user)],
):
    event_data = event.model_dump()

    new_event = models.Event(created_by=current_user.id, **event_data)

    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event


# GET ONE / READ
@router.get("/{id}", response_model=schemas.EventOut)
def get_event(
    id: int,
    current_user: Annotated[models.User, Depends(oauth2.get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    event = (
        db.query(models.Event)
        .filter(models.Event.id == id, models.Event.created_by == current_user.id)
        .first()
    )

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {id} not found",
        )
    return event


# GET ALL / READ
@router.get("", response_model=list[schemas.EventOut])
def get_events(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(oauth2.get_current_user)],
):
    events = (
        db.query(models.Event).filter(models.Event.created_by == current_user.id).all()
    )
    return events


# UPDATE
@router.put("/{id}", response_model=schemas.EventOut)
def update_event(
    id: int,
    current_user: Annotated[models.User, Depends(oauth2.get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    event: schemas.EventUpdate,
):
    event_query = db.query(models.Event).filter(
        models.Event.id == id, models.Event.created_by == current_user.id
    )
    updated_event = event_query.first()

    if not updated_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {id} not found",
        )

    update_data = event.model_dump(exclude_unset=True)
    event_query.update(update_data, synchronize_session=False)

    db.commit()
    db.refresh(updated_event)

    return updated_event


# DELETE
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    id: int,
    current_user: Annotated[models.User, Depends(oauth2.get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    event_query = db.query(models.Event).filter(
        models.Event.id == id, models.Event.created_by == current_user.id
    )

    if not event_query.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {id} not found",
        )

    event_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
