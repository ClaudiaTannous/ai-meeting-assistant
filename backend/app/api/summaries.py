from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db import crud, schemas, models
from backend.app.db.session import get_db
from backend.app.api.auth import get_current_user
from backend.app.ai.summarizer import generate_summary


router = APIRouter(prefix="/summaries", tags=["summaries"])

@router.post("/{transcript_id}/ai", response_model=schemas.SummaryOut)
def create_ai_summary(
    transcript_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Automatically generate and save a summary for a transcript using OpenAI.
    """
    transcript = crud.get_transcript(db, transcript_id=transcript_id)
    if not transcript or transcript.meeting.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript not found or not authorized",
        )

   
    ai_text = generate_summary(transcript.text)

    summary_in = schemas.SummaryCreate(content=ai_text)
    return crud.create_summary(db=db, summary=summary_in, transcript_id=transcript_id)

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

@router.put("/{summary_id}", response_model=schemas.SummaryOut)
def update_summary(
    summary_id: int,
    new_data: schemas.SummaryUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    summary = db.query(models.Summary).filter(models.Summary.id == summary_id).first()

    if not summary or summary.transcript.meeting.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found or not authorized",
        )

    updated = crud.update_summary(db, summary_id=summary_id, new_data=new_data)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Summary not found")

    return updated

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
