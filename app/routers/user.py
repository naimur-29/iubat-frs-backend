from fastapi import HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from .. import models, schemas, utils, oauth2, config

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# GET
@router.get("/", response_model=List[schemas.PostUserResponse])
def get_users(db: Session=Depends(get_db), current_user = Depends(oauth2.get_current_user), limit: int = 0, skip: int = 0, username: Optional[str]=""):
    if current_user.username == config.settings.admin_username:
        if not limit:
            res = db.query(models.User).filter(models.User.username.contains(username)).offset(skip).all()
        else:
            res = db.query(models.User).filter(models.User.username.contains(username)).limit(limit).offset(skip).all()
        
        if not res:
            raise HTTPException(status_code=404, detail="no user found!")
        return res
    else:
        raise HTTPException(status_code=403, detail="unauthorized!")
        

@router.get("/{id}", response_model=schemas.PostSingleUserResponse)
def get_user_by_id(id: int, db: Session=Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    if current_user.username == config.settings.admin_username or current_user.id == id:
        res = db.query(models.User).filter(models.User.id == id).first()
        if not res:
            raise HTTPException(status_code=404, detail=f"user with id:{id} not found!")
        
        return res
    else:
        raise HTTPException(status_code=403, detail="unauthorized!")

# POST
@router.post("/", status_code=201, response_model=schemas.PostUserResponse)
def register_user(user: schemas.PostUserRequest, db: Session=Depends(get_db)):
    user.password = utils.hash(user.password)
    res = new_user = models.User(**user.dict())
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return res
    except:
        raise HTTPException(status_code=409, detail="username already exists!")
    
# DELETE
@router.delete("/{id}", status_code=204)
def delete_user_by_id(id: int, db: Session=Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    if current_user.username == config.settings.admin_username or current_user.id == id:
        user = db.query(models.User).filter(models.User.id == id)

        if not user.first():
            raise HTTPException(status_code=404, detail=f"user with id:{id} not found!")
        elif not current_user:
            raise HTTPException(status_code=401, detail="not authenticated!")

        user.delete()
        db.commit()

        return Response(status_code=204)
    else:
        raise HTTPException(status_code=403, detail="unauthorized!")

# PUT
@router.put("/{id}", status_code=200, response_model=schemas.PostUserResponse)
def update_user_img(id: int, new_url: schemas.UpdateUserImgRequest, db: Session=Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    res = db.query(models.User).filter(models.User.id == id)
    
    if not res.first():
        raise HTTPException(status_code=404, detail=f"user with id:{id} not found!")
    elif id != current_user.id:
        raise HTTPException(status_code=403, detail="not authorized to change this!")
    
    res.update(new_url.dict(), synchronize_session=False)
    db.commit()
    
    return res.first()

@router.put("/changepassword/{id}", status_code=200)
def change_user_password(id: int, new_password: schemas.UpdateUserPasswordRequest, db: Session=Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    res = db.query(models.User).filter(models.User.id == id)
    
    if not res.first():
        raise HTTPException(status_code=404, detail=f"user with id:{id} not found!")
    elif id != current_user.id:
        raise HTTPException(status_code=403, detail="not authorized to change this!")
    elif not new_password.new_password:
        raise HTTPException(status_code=403, detail="password can't be null!")
    elif not utils.verify(new_password.old_password, res.first().password):
        raise HTTPException(status_code=409, detail="invalid credentials!")
    
    res.update({"password": utils.hash(new_password.new_password)}, synchronize_session=False)
    db.commit()
    
    return {"message": "password successfully changed!"}
