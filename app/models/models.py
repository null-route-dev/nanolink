from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Link(Base):
    __tablename__ = 'links'
    
    id = Column(Integer, primary_key=True)
    short_code = Column(String(20), nullable=False, unique=True)
    original_url = Column(Text(), nullable=False)
    created_at = Column(DateTime, default=datetime.now)