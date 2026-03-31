"""
Reminder endpoints - CRUD operations untuk reminders
"""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Reminder
from app.schemas.schemas import VapiRequest, ReminderResponse

router = APIRouter()


@router.post("/add_reminder")
def add_reminder(request: VapiRequest, db: Session = Depends(get_db)):
    """Add new reminder"""
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
    
    raise HTTPException(status_code=400, detail="Invalid function name for this endpoint")


@router.post("/get_reminders")
def get_reminders(request: VapiRequest, db: Session = Depends(get_db)):
    """Get all reminders"""
    for tool_call in request.message.tool_calls:
        if tool_call.function.name == "get_reminders":
            reminders = db.query(Reminder).all()
            
            return {
                "results": [
                    {
                        "toolCallId": tool_call.id,
                        "result": [ReminderResponse.model_validate(reminder).model_dump() for reminder in reminders]
                    }
                ]
            }
    
    raise HTTPException(status_code=400, detail="Invalid function name for this endpoint")


@router.post("/delete_reminder")
def delete_reminder(request: VapiRequest, db: Session = Depends(get_db)):
    """Delete reminder by ID"""
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
    
    raise HTTPException(status_code=400, detail="Invalid function name for this endpoint")
