"""
SQLAlchemy models untuk Todo, Reminder, dan CalendarEvent
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.core.database import Base


class Todo(Base):
    __tablename__ = "todos"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)


class Reminder(Base):
    __tablename__ = "reminders"
    
    id = Column(Integer, primary_key=True, index=True)
    reminder_text = Column(String)
    importance = Column(String)  # high, medium, low


class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    event_from = Column(DateTime)
    event_to = Column(DateTime)
