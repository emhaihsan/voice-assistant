"""
Pydantic schemas untuk request dan response validation
"""
from datetime import datetime
from typing import Union
from pydantic import BaseModel


# ========== Vapi Request Schemas ==========
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


# ========== Response Schemas ==========
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
    event_from: datetime
    event_to: datetime
    
    class Config:
        from_attributes = True


# ========== Vapi Response Format ==========
class ToolCallResult(BaseModel):
    toolCallId: str
    result: Union[str, list, dict]


class VapiResponse(BaseModel):
    results: list[ToolCallResult]
