"""
Calendar endpoints - CRUD operations untuk calendar events
"""
import json
from datetime import datetime as dt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import CalendarEvent
from app.schemas.schemas import VapiRequest, CalendarEventResponse

router = APIRouter()


@router.post("/add_calendar_entry")
def add_calendar_entry(request: VapiRequest, db: Session = Depends(get_db)):
    """Add new calendar event"""
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
    
    raise HTTPException(status_code=400, detail="Invalid function name for this endpoint")


@router.post("/get_calendar_entries")
def get_calendar_entries(request: VapiRequest, db: Session = Depends(get_db)):
    """Get all calendar events"""
    for tool_call in request.message.tool_calls:
        if tool_call.function.name == "get_calendar_entries":
            events = db.query(CalendarEvent).all()
            
            return {
                "results": [
                    {
                        "toolCallId": tool_call.id,
                        "result": [CalendarEventResponse.model_validate(event).model_dump() for event in events]
                    }
                ]
            }
    
    raise HTTPException(status_code=400, detail="Invalid function name for this endpoint")


@router.post("/delete_calendar_entry")
def delete_calendar_entry(request: VapiRequest, db: Session = Depends(get_db)):
    """Delete calendar event by ID"""
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
    
    raise HTTPException(status_code=400, detail="Invalid function name for this endpoint")
