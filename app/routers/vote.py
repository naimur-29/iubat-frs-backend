from fastapi import APIRouter, HTTPException, Depends, Response
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import schemas, oauth2, models, config

router = APIRouter(
    tags=["Vote"]
)

# GET
@router.get("/faculties/{facultyId}/vote/{userId}", response_model=schemas.GetVoteResponse)
def get_vote_for_specific_user(facultyId: int, userId: int, db: Session=Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    res_vote = db.query(models.Vote).filter(models.Vote.faculty_id == facultyId, models.Vote.user_id == userId).first()
    
    if not res_vote:
        removed_vote = schemas.GetVoteResponse(
            teaching_value=0,
            marking_value=0,
            assignment_value=0,
            vote=False
        )
        return removed_vote
    
    return res_vote

@router.get("/users/{id}/votes", response_model=List[schemas.GetUserVotesResponse])
def get_user_by_id(id: int, db: Session=Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    if current_user.username == config.settings.admin_username or current_user.id == id:
        res = db.query(models.Vote).filter(models.Vote.user_id == id).all()
        
        if not res:
            raise HTTPException(status_code=404, detail=f"votes of user with id:{id} not found!")
        
        return res
    else:
        raise HTTPException(status_code=403, detail="unauthorized!")

# POST
@router.post("/faculties/{facultyId}/vote")
def vote(facultyId: int, vote: schemas.PostVoteRequest, db: Session=Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    faculty = db.query(models.Faculty).filter(models.Faculty.id == facultyId)
    
    if not faculty.first():
        raise HTTPException(status_code=404, detail=f"faculty with id:{facultyId} not found!")
    
    vote_count = db.query(models.Faculty, func.count(models.Vote.faculty_id).label("votes")).join(models.Vote, models.Vote.faculty_id == models.Faculty.id, isouter=True).group_by(models.Faculty.id).filter(models.Faculty.id == facultyId).first().votes
    
    res = db.query(models.Vote).filter(models.Vote.user_id == current_user.id, models.Vote.faculty_id == facultyId)
    
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
        faculty_id=facultyId,
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

#DELETE
@router.delete("/votes")
def delete_all_votes(db: Session=Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    votes = db.query(models.Vote)
    faculties = db.query(models.Faculty)
    
    if not current_user.username == config.settings.admin_username:
        raise HTTPException(status_code=403, detail="unauthorized!")
    
    if not votes.all():
        raise HTTPException(status_code=404, detail="no votes found!")
    
    for vote in votes.all():
        faculty = faculties.filter(models.Faculty.id == vote.faculty_id)
        faculty.update({
                "teaching_rate": 0,
                "total_teaching_rate": 0,
                "marking_rate": 0,
                "total_marking_rate": 0,
                "assignment_rate": 0,
                "total_assignment_rate": 0
            }, synchronize_session=False)
    
    votes.delete()
    db.commit()
    
    return Response(status_code=204)