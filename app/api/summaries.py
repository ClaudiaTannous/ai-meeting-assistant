from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from app.db import crud,schemas,models
from app.db.session import get_db
from app.api.auth import get_current_user

router = APIRouter("/{meeting_id}",response_model=schemas.TranscriptOut)

@router.post("/{meeting_id}" , response_model=schemas.TranscriptOut)
def create_transcript(
    meeting_id: int,
    transcript: schemas.TranscriptCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    meeting = crud.get_meeting(db,meeting_id=meeting_id)
    if not meeting or meeting.user_id!=current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="meeting not found")
    return crud.create_transcript(db=db,transcript=transcript,meeting_id=meeting_id)

@router.get("/{transcript_id}",response_model=schemas.TranscriptOut)
def get_transcript(
    transcipt_id:int,db: Session =Depends(get_db),current_user:models.User=Depends(get_current_user),
):
    transcript = crud.get_transcript(db,transcipt_id=transcipt_id)
    if not transcript or transcript.meeting.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="transcript not found")
    
    return transcript

@router.get("/{transcript_id}/with-summaries" ,response_model=schemas.TranscriptWithSummaries)
def get_transcript_with_summaries(
    transcript_id:int,db: Session = Depends(get_db),current_user: models.User=Depends(get_current_user)
):
    transcript = crud.get_transcript_with_summaries(db,transcript_id=transcript_id)
    if not transcript or transcript.meeting.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="transcript not found")
    return transcript

@router.delete("/{transcript_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_transcript(transcript_id: int , db: Session = Depends(get_db), current_user: models.User =Depends(get_current_user)):
    transcript = crud.get_transcript(db, transcript_id=transcript_id)
    if not transcript or transcript.meeting.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="transcript not found")
    
    db.delete(transcript)
    db.commit()
    return{"detail":"transcript deleted"}

    
    