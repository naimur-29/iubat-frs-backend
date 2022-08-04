from sqlalchemy import Column, Integer, TIMESTAMP, String, Numeric, ForeignKey
from sqlalchemy.sql.expression import text
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    img_url = Column(String, nullable=False, server_default='default')
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
class Faculty(Base):
    __tablename__ = "faculties"
    
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    department = Column(String, nullable=False)
    img_url = Column(String, nullable=False)
    rate = Column(Numeric, nullable=False, server_default='0')
    total_rate = Column(Numeric, nullable=False, server_default='0')
    
class Vote(Base):
    __tablename__ = "votes"
    
    user_id  = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    faculty_id = Column(Integer, ForeignKey("faculties.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    vote_value = Column(Integer, nullable=False)