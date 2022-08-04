from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from .. import models, schemas

router = APIRouter(
    prefix="/faculties",
    tags=["Faculties"]
)

# GET
@router.get("/", response_model=List[schemas.GetFacultyResponse])
def get_all_faculties(db: Session=Depends(get_db), name: Optional[str] = "", limit: int = 20, skip: int = 0):
    res = db.query(models.Faculty).filter(models.Faculty.name.contains(name)).order_by(models.Faculty.rate.desc()).limit(limit).offset(skip).all()
    
    if not res:
        raise HTTPException(status_code=404, detail="no faculties available!")
    
    return res;

@router.get("/{id}", response_model=schemas.GetFacultyResponse)
def get_user_by_id(id: int, db: Session=Depends(get_db)):
    res = db.query(models.Faculty).filter(models.Faculty.id == id).first()
    
    if not res:
        raise HTTPException(status_code=404, detail=f"faculty with id:{id} not found!")
    
    return res

# POST
@router.post("/", status_code=201, response_model=schemas.PostFacultyResponse)
def add_faculty(faculty: schemas.PostFacultyRequest, db: Session=Depends(get_db)):
    res = new_faculty = models.Faculty(**faculty.dict())
    db.add(new_faculty)
    db.commit()
    db.refresh(new_faculty)
    
    return res

# DELETE
@router.delete("/{id}", status_code=204)
def remove_faculty_by_id(id: int, db: Session=Depends(get_db)):
    res = db.query(models.Faculty).filter(models.Faculty.id == id)
    
    if not res.first():
        raise HTTPException(status_code=404, detail=f"faculty with id:{id} not found!")
    
    res.delete(synchronize_session=False)
    db.commit()
    
    return Response(status_code=204)

@router.put("/{id}", status_code=200, response_model=schemas.GetFacultyResponse)
def update_faculty_infos(id: int, update: schemas.PutFacultyRequest, db: Session=Depends(get_db)):
    res = db.query(models.Faculty).filter(models.Faculty.id == id)
    
    if not res.first():
        raise HTTPException(status_code=404, detail=f"user with id:{id} not found!")
    
    res.update(update.dict(), synchronize_session=False)
    db.commit()
    
    return res.first()
    
