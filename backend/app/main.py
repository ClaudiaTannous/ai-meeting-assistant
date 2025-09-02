from fastapi import FastAPI
from .api import auth, meetings, transcripts, summaries
from .db.session import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Meeting Assistance", version="1.0.0")

app.include_router(auth.router)
app.include_router(meetings.router)
app.include_router(transcripts.router)
app.include_router(summaries.router)

@app.get("/")
def root():
    return {"message": "AI Meeting Assistant is running"}
