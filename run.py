"""
Entry point untuk menjalankan aplikasi
Run: uvicorn app.main:app --reload
"""
from app.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
