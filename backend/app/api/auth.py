from fastapi import APIRouter, Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.app.db import crud , schemas ,models
from backend.app.core.security import hash_password, verify_password, create_access_token, verify_access_token
from backend.app.db.session import get_db

router=APIRouter(prefix="/auth",tags=["auth"])

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/register",response_model=schemas.UserOut)
def register(user: schemas.UserCreate,db:Session=Depends(get_db)):
    db_user = crud.get_user_by_email(db,user.email)
    if db_user:
        raise HTTPException(status_code=400,detail="Email already registered")
    
    hashed_pw = hash_password(user.password)
    return crud.create_user(db=db, user=user,hashed_password=hashed_pw)

@router.post("/login")
def login(from_data:OAuth2PasswordRequestForm = Depends(), db:Session=Depends(get_db)):
    user=crud.get_user_by_email(db,from_data.username)
    if not user or not verify_password(from_data.password,user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate":"Bearer"},
        )
        
    access_token = create_access_token({"sub" :str(user.id)})
    return {"access_token":access_token,"token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme), db: Session=Depends(get_db)):
    payload=verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="invalid or expired token" )
    
    user_id:str = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="invalid payload" )
    
    user = crud.get_user(db,int(user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    
    return user

@router.get("/me",response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    
    return current_user