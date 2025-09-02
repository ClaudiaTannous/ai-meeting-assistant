from fastapi import APIRouter, status, HTTPException, Depends
from backend.app.db import crud, schemas, models
from backend.app.db.session import get_db
from sqlalchemy.orm import Session
from backend.app.api.auth import get_current_user

router = APIRouter(prefix="/meetings", tags=["meetings"])


@router.post("/", response_model=schemas.MeetingOut)
def create_meeting(
    meeting: schemas.MeetingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.create_meeting(db=db, meeting=meeting, user_id=current_user.id)


@router.get("/", response_model=list[schemas.MeetingOut])
def get_meetings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.get_meetings_for_user(db=db, user_id=current_user.id)


@router.get("/{meeting_id}", response_model=schemas.MeetingOut)
def get_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    meeting = crud.get_meeting(db, meeting_id=meeting_id)
    if not meeting or meeting.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
    return meeting


@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    meeting = crud.get_meeting(db, meeting_id=meeting_id)
    if not meeting or meeting.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")

    db.delete(meeting)
    db.commit()
    return None  
