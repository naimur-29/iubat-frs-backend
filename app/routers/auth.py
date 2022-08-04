from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import utils, models, schemas, oauth2

router = APIRouter(
    prefix="/login",
    tags=["Authentication"]
)

@router.post("/")
def login_user(user: schemas.PostUserLoginRequest, db: Session=Depends(get_db)):
    res = db.query(models.User).filter(models.User.username == user.username).first()

    if not res:
        raise HTTPException(status_code=404, detail=f"invalid login info!")
    elif not utils.verify(user.password, res.password):
        raise HTTPException(status_code=403, detail=f"invalid login info!")

    # Create Access Token
    access_token = oauth2.create_access_token(data = {"user_id": res.id})

    return schemas.PostUserLoginResponse(token=access_token)