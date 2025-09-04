from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api import auth, meetings, transcripts, summaries
from backend.app.db.session import Base, engine

# ✅ Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Meeting Assistance", version="1.0.0")

# ✅ CORS setup
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://172.20.208.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # 👈 must be explicit if allow_credentials=True
    allow_credentials=True,
    allow_methods=["*"],          # allow all methods
    allow_headers=["*"],          # allow all headers
)

# ✅ Routers
app.include_router(auth.router)
app.include_router(meetings.router)
app.include_router(transcripts.router)
app.include_router(summaries.router)

@app.get("/")
def root():
    return {"message": "AI Meeting Assistant is running"}
