from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# USER
class PostUserRequest(BaseModel):
    username: str
    password: str
    img_url: Optional[str]
    
class PostUserResponse(BaseModel):
    id: int
    username: str
    img_url: str
    created_at: datetime
    
    class Config:
        orm_mode = True    


class GetUserVotesResponse(BaseModel):
    faculty_id: int
    teaching_value: int
    marking_value: int
    assignment_value: int
    
    class Config:
        orm_mode = True

class PostSingleUserResponse(BaseModel):
    id: int
    username: str
    description: str
    img_url: str
    cover_img_url: str
    created_at: datetime
    
    class Config:
        orm_mode = True
        
class UpdateUserImgRequest(BaseModel):
    img_url: str = "default"
    
class UpdateUserPasswordRequest(BaseModel):
    old_password: str
    new_password: str

# FACULTY
class GetFacultyResponse(BaseModel):
    id: int
    name: str
    department: str
    img_url: str
    
    teaching_rate: float
    marking_rate: float
    assignment_rate: float
    
    class Config:
        orm_mode = True
        
class PostFacultyRequest(BaseModel):
    name: str
    department: str
    img_url: str
    
class PostFacultyResponse(BaseModel):
    name: str
    department: str
    img_url: str
    
    class Config:
        orm_mode = True
        
class PutFacultyRequest(BaseModel):
    name: str
    department: str
    img_url: str
    
# USER AUTHENTICATION
class PostUserLoginRequest(BaseModel):
    username: str
    password: str
    
class PostUserLoginResponse(BaseModel):
    token: str
    token_type: str = "bearer"
    role: str
    id: int
    
class PostTokenDataRequest(BaseModel):
    id: Optional[str]
    
# VOTE
class PostVoteRequest(BaseModel):
    teaching_value: int
    marking_value: int
    assignment_value: int
    
class GetVoteResponse(BaseModel):
    teaching_value: int
    marking_value: int
    assignment_value: int
    vote: bool = True
    
    class Config:
        orm_mode = True