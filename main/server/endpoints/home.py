
from fastapi import APIRouter

router = APIRouter()

# Health check endpoint to verify API is running
@router.get("/")
async def home():
    """Health check endpoint to verify API is running.
    Returns:
        dict: A simple welcome message."""
    
    return {"message": "Welcome to the Multi-Format-RAG-Chat API"}