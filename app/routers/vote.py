from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas, oauth2, models

router = APIRouter(
    prefix="/faculties/{id}",
    tags=["Vote"]
)

# POST
@router.post("/vote")
def vote(id: int, vote: schemas.PostVoteRequest, db: Session=Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    faculty = db.query(models.Faculty).filter(models.Faculty.id == id)
    
    if not faculty.first():
        raise HTTPException(status_code=404, detail=f"faculty with id:{id} not found!")
    
    vote_count = db.query(models.Faculty, func.count(models.Vote.faculty_id).label("votes")).join(models.Vote, models.Vote.faculty_id == models.Faculty.id, isouter=True).group_by(models.Faculty.id).filter(models.Faculty.id == id).first().votes
    
    res = db.query(models.Vote).filter(models.Vote.user_id == current_user.id, models.Vote.faculty_id == id)
    
    if res.first():
        total_teaching = faculty.first().total_teaching_rate - res.first().teaching_value
        total_marking = faculty.first().total_marking_rate - res.first().marking_value
        total_assignment = faculty.first().total_assignment_rate - res.first().assignment_value
        if vote_count:
            vote_count -= 1
            faculty.update({
                "teaching_rate": format(total_teaching/vote_count if vote_count else total_teaching, ".1f"),
                "total_teaching_rate": format(total_teaching, ".1f"),
                "marking_rate": format(total_marking/vote_count if vote_count else total_marking, ".1f"),
                "total_marking_rate": format(total_marking, ".1f"),
                "assignment_rate": format(total_assignment/vote_count if vote_count else total_assignment, ".1f"),
                "total_assignment_rate": format(total_assignment, ".1f")
            }, synchronize_session=False)
            
        res.delete(synchronize_session=False)
        db.commit()
        
        return {"message": "removed the rating!"}
    
    new_vote = models.Vote(
        user_id=current_user.id,
        faculty_id=id,
        teaching_value=vote.teaching_value,
        marking_value=vote.marking_value,
        assignment_value=vote.assignment_value
    )
    
    vote_count += 1
    total_teaching = float(faculty.first().total_teaching_rate) + vote.teaching_value
    total_marking = float(faculty.first().total_marking_rate) + vote.marking_value
    total_assignment = float(faculty.first().total_assignment_rate) + vote.assignment_value
    if vote_count:
        faculty.update({
            "teaching_rate": format(total_teaching/vote_count if vote_count else total_teaching, ".1f"),
            "total_teaching_rate": format(total_teaching, ".1f"),
            "marking_rate": format(total_marking/vote_count if vote_count else total_marking, ".1f"),
            "total_marking_rate": format(total_marking, ".1f"),
            "assignment_rate": format(total_assignment/vote_count if vote_count else total_assignment, ".1f"),
            "total_assignment_rate": format(total_assignment, ".1f")
        }, synchronize_session=False)
        
    db.add(new_vote)
    db.commit()
    db.refresh(new_vote)

    return {"message": "successfully added rating!"}