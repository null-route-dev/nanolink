from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Link(Base):
    __tablename__ = 'links'
    
    id = Column(Integer, primary_key=True)
    short_code = Column(String(20), nullable=False, unique=True)
    original_url = Column(Text(), nullable=False)
    created_at = Column(DateTime, default=func.now())

    click_logs = relationship("ClickLog", back_populates="link", cascade="all, delete-orphan")

class ClickLog(Base):
    __tablename__ = "clicks_log"
    
    id = Column(Integer, primary_key=True)
    link_id = Column(Integer, ForeignKey("links.id", ondelete="CASCADE"), nullable=False)
    clicked_at = Column(DateTime, default=func.now(), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    link = relationship("Link", back_populates="click_logs")