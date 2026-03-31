"""
Todo endpoints - CRUD operations untuk todos
"""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Todo
from app.schemas.schemas import VapiRequest, TodoResponse

router = APIRouter()


@router.post("/create_todo")
def create_todo(request: VapiRequest, db: Session = Depends(get_db)):
    """Create new todo item"""
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
    
    raise HTTPException(status_code=400, detail="Invalid function name for this endpoint")


@router.post("/get_todos")
def get_todos(request: VapiRequest, db: Session = Depends(get_db)):
    """Get all todos"""
    for tool_call in request.message.tool_calls:
        if tool_call.function.name == "get_todos":
            todos = db.query(Todo).all()
            
            return {
                "results": [
                    {
                        "toolCallId": tool_call.id,
                        "result": [TodoResponse.model_validate(todo).model_dump() for todo in todos]
                    }
                ]
            }
    
    raise HTTPException(status_code=400, detail="Invalid function name for this endpoint")


@router.post("/complete_todo")
def complete_todo(request: VapiRequest, db: Session = Depends(get_db)):
    """Mark todo as completed"""
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
    
    raise HTTPException(status_code=400, detail="Invalid function name for this endpoint")


@router.post("/delete_todo")
def delete_todo(request: VapiRequest, db: Session = Depends(get_db)):
    """Delete todo by ID"""
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
    
    raise HTTPException(status_code=400, detail="Invalid function name for this endpoint")
