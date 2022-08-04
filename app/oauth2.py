from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import models, schemas, config
from .database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = config.settings.secret_key
ALGORITHM = config.settings.algorithm
ACCESS_TOKEN_EXPIRE_DURATION = config.settings.access_token_expire_duration

def create_access_token(data: dict):
    to_encode  = data.copy()
    
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_DURATION)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        id: str = payload.get("user_id")
        
        if not id:
            raise credentials_exception
        
        token_data = schemas.PostTokenDataRequest(id=id)
    except:
        raise credentials_exception
    
    return token_data

def get_current_user(token: str = Depends(oauth2_scheme), db: Session=Depends(get_db)):
    credential_exception = HTTPException(status_code=403, detail="couldn't validate credentials!", headers={"WWW-Authenticate": "Bearer"})
    token = verify_access_token(token, credential_exception)
    
    current_user = db.query(models.User).filter(models.User.id == token.id).first()
    
    return current_user