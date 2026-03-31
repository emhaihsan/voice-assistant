"""
AI Voice Assistant Backend - FastAPI + Vapi Integration
Professional voice assistant with todo management, reminders, and calendar events.
"""

import json
from datetime import datetime as dt
from typing import Union
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends
from fastapi.requests import Request
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

# Database setup
DATABASE_URL = "sqlite:///./voice_assistant.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Data Models
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

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI App
app = FastAPI(title="AI Voice Assistant API")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Vapi Request/Response Models
class ToolCallFunction(BaseModel):
    name: str
    arguments: Union[str, dict]

class ToolCall(BaseModel):
    id: str
    function: ToolCallFunction

class Message(BaseModel):
    tool_calls: list[ToolCall]

class VapiRequest(BaseModel):
    message: Message

# Response Models
class TodoResponse(BaseModel):
    id: int
    title: str
    description: Union[str, None]
    completed: bool
    
    class Config:
        from_attributes = True

class ReminderResponse(BaseModel):
    id: int
    reminder_text: str
    importance: str
    
    class Config:
        from_attributes = True

class CalendarEventResponse(BaseModel):
    id: int
    title: str
    description: Union[str, None]
    event_from: dt
    event_to: dt
    
    class Config:
        from_attributes = True

# Todo Endpoints
@app.post("/create_todo")
def create_todo(request: VapiRequest, db: Session = Depends(get_db)):
    for tool_call in request.message.tool_calls:
        if tool_call.function.name == "create_todo":
            arguments = tool_call.function.arguments
            
            if isinstance(arguments, str):
                arguments = json.loads(arguments)
            
            title = arguments.get("title", "")
            description = arguments.get("description", "")
            
            todo = Todo(title=title, description=description, completed=False)
            db.add(todo)
            db.commit()
            db.refresh(todo)
            
            return {
                "results": [
                    {
                        "toolCallId": tool_call.id,
                        "result": "success"
                    }
                ]
            }
    
    raise HTTPException(status_code=400, detail="Invalid request")

@app.post("/get_todos")
def get_todos(request: VapiRequest, db: Session = Depends(get_db)):
    for tool_call in request.message.tool_calls:
        if tool_call.function.name == "get_todos":
            todos = db.query(Todo).all()
            
            return {
                "results": [
                    {
                        "toolCallId": tool_call.id,
                        "result": [TodoResponse.from_orm(todo).dict() for todo in todos]
                    }
                ]
            }
    
    raise HTTPException(status_code=400, detail="Invalid request")

@app.post("/complete_todo")
def complete_todo(request: VapiRequest, db: Session = Depends(get_db)):
    for tool_call in request.message.tool_calls:
        if tool_call.function.name == "complete_todo":
            arguments = tool_call.function.arguments
            
            if isinstance(arguments, str):
                arguments = json.loads(arguments)
            
            todo_id = arguments.get("id")
            if not todo_id:
                raise HTTPException(status_code=400, detail="Missing todo ID")
            
            todo = db.query(Todo).filter(Todo.id == todo_id).first()
            if not todo:
                raise HTTPException(status_code=404, detail="Todo not found")
            
            todo.completed = True
            db.commit()
            db.refresh(todo)
            
            return {
                "results": [
                    {
                        "toolCallId": tool_call.id,
                        "result": "success"
                    }
                ]
            }
    
    raise HTTPException(status_code=400, detail="Invalid request")

@app.post("/delete_todo")
def delete_todo(request: VapiRequest, db: Session = Depends(get_db)):
    for tool_call in request.message.tool_calls:
        if tool_call.function.name == "delete_todo":
            arguments = tool_call.function.arguments
            
            if isinstance(arguments, str):
                arguments = json.loads(arguments)
            
            todo_id = arguments.get("id")
            if not todo_id:
                raise HTTPException(status_code=400, detail="Missing todo ID")
            
            todo = db.query(Todo).filter(Todo.id == todo_id).first()
            if not todo:
                raise HTTPException(status_code=404, detail="Todo not found")
            
            db.delete(todo)
            db.commit()
            
            return {
                "results": [
                    {
                        "toolCallId": tool_call.id,
                        "result": "success"
                    }
                ]
            }
    
    raise HTTPException(status_code=400, detail="Invalid request")

# Reminder Endpoints
@app.post("/add_reminder")
def add_reminder(request: VapiRequest, db: Session = Depends(get_db)):
    for tool_call in request.message.tool_calls:
        if tool_call.function.name == "add_reminder":
            arguments = tool_call.function.arguments
            
            if isinstance(arguments, str):
                arguments = json.loads(arguments)
            
            reminder_text = arguments.get("reminder_text", "")
            importance = arguments.get("importance", "medium")
            
            reminder = Reminder(reminder_text=reminder_text, importance=importance)
            db.add(reminder)
            db.commit()
            db.refresh(reminder)
            
            return {
                "results": [
                    {
                        "toolCallId": tool_call.id,
                        "result": "success"
                    }
                ]
            }
    
    raise HTTPException(status_code=400, detail="Invalid request")

@app.post("/get_reminders")
def get_reminders(request: VapiRequest, db: Session = Depends(get_db)):
    for tool_call in request.message.tool_calls:
        if tool_call.function.name == "get_reminders":
            reminders = db.query(Reminder).all()
            
            return {
                "results": [
                    {
                        "toolCallId": tool_call.id,
                        "result": [ReminderResponse.from_orm(reminder).dict() for reminder in reminders]
                    }
                ]
            }
    
    raise HTTPException(status_code=400, detail="Invalid request")

@app.post("/delete_reminder")
def delete_reminder(request: VapiRequest, db: Session = Depends(get_db)):
    for tool_call in request.message.tool_calls:
        if tool_call.function.name == "delete_reminder":
            arguments = tool_call.function.arguments
            
            if isinstance(arguments, str):
                arguments = json.loads(arguments)
            
            reminder_id = arguments.get("id")
            if not reminder_id:
                raise HTTPException(status_code=400, detail="Missing reminder ID")
            
            reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
            if not reminder:
                raise HTTPException(status_code=404, detail="Reminder not found")
            
            db.delete(reminder)
            db.commit()
            
            return {
                "results": [
                    {
                        "toolCallId": tool_call.id,
                        "result": "success"
                    }
                ]
            }
    
    raise HTTPException(status_code=400, detail="Invalid request")

# Calendar Event Endpoints
@app.post("/add_calendar_entry")
def add_calendar_entry(request: VapiRequest, db: Session = Depends(get_db)):
    for tool_call in request.message.tool_calls:
        if tool_call.function.name == "add_calendar_entry":
            arguments = tool_call.function.arguments
            
            if isinstance(arguments, str):
                arguments = json.loads(arguments)
            
            title = arguments.get("title", "")
            description = arguments.get("description", "")
            event_from = arguments.get("event_from", "")
            event_to = arguments.get("event_to", "")
            
            # Parse ISO format datetime
            event_from_dt = dt.fromisoformat(event_from.replace("Z", "+00:00"))
            event_to_dt = dt.fromisoformat(event_to.replace("Z", "+00:00"))
            
            event = CalendarEvent(
                title=title,
                description=description,
                event_from=event_from_dt,
                event_to=event_to_dt
            )
            db.add(event)
            db.commit()
            db.refresh(event)
            
            return {
                "results": [
                    {
                        "toolCallId": tool_call.id,
                        "result": "success"
                    }
                ]
            }
    
    raise HTTPException(status_code=400, detail="Invalid request")

@app.post("/get_calendar_entries")
def get_calendar_entries(request: VapiRequest, db: Session = Depends(get_db)):
    for tool_call in request.message.tool_calls:
        if tool_call.function.name == "get_calendar_entries":
            events = db.query(CalendarEvent).all()
            
            return {
                "results": [
                    {
                        "toolCallId": tool_call.id,
                        "result": [CalendarEventResponse.from_orm(event).dict() for event in events]
                    }
                ]
            }
    
    raise HTTPException(status_code=400, detail="Invalid request")

@app.post("/delete_calendar_entry")
def delete_calendar_entry(request: VapiRequest, db: Session = Depends(get_db)):
    for tool_call in request.message.tool_calls:
        if tool_call.function.name == "delete_calendar_entry":
            arguments = tool_call.function.arguments
            
            if isinstance(arguments, str):
                arguments = json.loads(arguments)
            
            event_id = arguments.get("id")
            if not event_id:
                raise HTTPException(status_code=400, detail="Missing event ID")
            
            event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
            if not event:
                raise HTTPException(status_code=404, detail="Calendar event not found")
            
            db.delete(event)
            db.commit()
            
            return {
                "results": [
                    {
                        "toolCallId": tool_call.id,
                        "result": "success"
                    }
                ]
            }
    
    raise HTTPException(status_code=400, detail="Invalid request")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
