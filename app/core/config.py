from pydantic import BaseSettings

class Settings(BaseSettings):
    
    SQLALCHEMY_DATABASE_URL: str="postgresql://postgres:password@localhost:5432/meeting_assistant"
    SECRET_KEY: str="secretkey"
    ALGORITHM:str="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES:int=30
    
    PROJECT_NAME:str="AI MEETING ASSISTANCE"
    VERSION: str="1.0.0"
    
    class Config:
        env_file=".env"
        

settings=Settings()
    

