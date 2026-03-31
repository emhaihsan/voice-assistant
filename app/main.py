"""
Main FastAPI application - entry point untuk Voice Assistant API
Modular structure dengan routers untuk todos, reminders, dan calendar events.
"""
from fastapi import FastAPI
from app.core.database import engine, Base
from app.api.v1.endpoints import todos, reminders, calendar

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="AI Voice Assistant API",
    description="Professional voice assistant backend dengan Vapi integration",
    version="1.0.0"
)

# Include routers
app.include_router(todos.router)
app.include_router(reminders.router)
app.include_router(calendar.router)


@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "message": "AI Voice Assistant API is running",
        "docs": "/docs",
        "endpoints": {
            "todos": ["/create_todo", "/get_todos", "/complete_todo", "/delete_todo"],
            "reminders": ["/add_reminder", "/get_reminders", "/delete_reminder"],
            "calendar": ["/add_calendar_entry", "/get_calendar_entries", "/delete_calendar_entry"]
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
