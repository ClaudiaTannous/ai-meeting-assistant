from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import crud, schemas, models
from app.db.session import get_db
from app.api.auth import get_current_user

router = APIRouter(prefix="/summaries", tags=["summaries"])


@router.post("/{transcript_id}", response_model=schemas.SummaryOut)
def create_summary(
    transcript_id: int,
    summary: schemas.SummaryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    transcript = crud.get_transcript(db, transcript_id=transcript_id)
    if not transcript or transcript.meeting.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transcript not found")
    return crud.create_summary(db=db, summary=summary, transcript_id=transcript_id)


@router.get("/{transcript_id}", response_model=list[schemas.SummaryOut])
def get_summaries_for_transcript(
    transcript_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    transcript = crud.get_transcript(db, transcript_id=transcript_id)
    if not transcript or transcript.meeting.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transcript not found")
    return crud.get_summaries_for_transcript(db, transcript_id=transcript_id)


@router.delete("/{summary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_summary(
    summary_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    summary = db.query(models.Summary).filter(models.Summary.id == summary_id).first()
    if not summary or summary.transcript.meeting.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Summary not found")

    crud.delete_summary(db, summary_id)
    return None  
