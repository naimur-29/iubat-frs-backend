from sqlalchemy import Column, Integer, TIMESTAMP, String, Numeric, ForeignKey
from sqlalchemy.sql.expression import text
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    description = Column(String, nullable=False, server_default='default')
    img_url = Column(String, nullable=False, server_default='default')
    cover_img_url = Column(String, nullable=False, server_default='default')
    
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
class Faculty(Base):
    __tablename__ = "faculties"
    
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    department = Column(String, nullable=False)
    img_url = Column(String, nullable=False)
    
    teaching_rate = Column(Numeric, nullable=False, server_default='0')
    total_teaching_rate = Column(Numeric, nullable=False, server_default='0')
    
    marking_rate = Column(Numeric, nullable=False, server_default='0')
    total_marking_rate = Column(Numeric, nullable=False, server_default='0')
    
    assignment_rate = Column(Numeric, nullable=False, server_default='0')
    total_assignment_rate = Column(Numeric, nullable=False, server_default='0')
    
class Vote(Base):
    __tablename__ = "votes"
    
    user_id  = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    faculty_id = Column(Integer, ForeignKey("faculties.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    
    teaching_value = Column(Numeric, nullable=False)
    marking_value = Column(Numeric, nullable=False)
    assignment_value = Column(Numeric, nullable=False)