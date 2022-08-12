from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import utils, models, schemas, oauth2, config

router = APIRouter(
    prefix="/login",
    tags=["Authentication"]
)

@router.post("/")
def login_user(user: schemas.PostUserLoginRequest, db: Session=Depends(get_db)):
    res = db.query(models.User).filter(models.User.username == user.username).first()

    if not user.username or not user.password:
        raise HTTPException(status_code=400, detail="missing username or password!")
    elif not res:
        raise HTTPException(status_code=401, detail="invalid login info!")
    elif not utils.verify(user.password, res.password):
        raise HTTPException(status_code=401, detail="invalid login info!")

    # Create Access Token
    access_token = oauth2.create_access_token(data = {"user_id": res.id})
    if user.username == config.settings.admin_username and user.password == config.settings.admin_password:
        ROLE = "admin"
    else:
        ROLE = "user"

    return schemas.PostUserLoginResponse(token=access_token, role=ROLE, id=res.id)