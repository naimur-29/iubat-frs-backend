from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas, oauth2, models

router = APIRouter(
    tags=["Vote"]
)

# POST
@router.post("/faculties/{id}/vote")
def vote(id: int, vote_value: schemas.PostVoteRequest, db: Session=Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    faculty = db.query(models.Faculty).filter(models.Faculty.id == id)
    
    if not faculty.first():
        raise HTTPException(status_code=404, detail=f"faculty with id:{id} not found!")
    
    vote_count = db.query(models.Faculty, func.count(models.Vote.faculty_id).label("votes")).join(models.Vote, models.Vote.faculty_id == models.Faculty.id, isouter=True).group_by(models.Faculty.id).filter(models.Faculty.id == id).first().votes
    
    res = db.query(models.Vote).filter(models.Vote.user_id == current_user.id, models.Vote.faculty_id == id)
    
    if res.first():
        res.delete(synchronize_session=False)
        db.commit()
        
        vote_count -= 1
        if vote_count:
            faculty.update({
                "total_rate": float(faculty.first().total_rate)-vote_value.vote_value,
                "rate": format(float(faculty.first().total_rate)/vote_count, ".2f")
            }, synchronize_session=False)
            db.commit()
        
        return {"message": "removed the vote!"}
    
    new_vote = models.Vote(user_id=current_user.id, faculty_id=id, vote_value=vote_value.vote_value)
    db.add(new_vote)
    db.commit()
    
    vote_count += 1
    if vote_count:
        faculty.update({
            "total_rate": float(faculty.first().total_rate)+vote_value.vote_value,
            "rate": format(float(faculty.first().total_rate)/vote_count, ".2f")
        }, synchronize_session=False)
        db.commit()

    return {"message": "successfully added a vote!"}