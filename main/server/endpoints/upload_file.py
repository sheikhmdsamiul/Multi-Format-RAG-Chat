import os
from pathlib import Path
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from langchain_core.messages import HumanMessage, AIMessage

from main.modules.document_handler import extract_text_from_file
from main.modules.process_vector_store import preprocess_text
from main.server.schema import UploadResponse
from main.server.session import session_state

router = APIRouter()

# Create upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)




# Endpoint to upload a file, extract and preprocess its text, and initialize a chat session.
@router.post("/uploadfile")
async def create_upload_file(file: UploadFile = File(...), response_model = UploadResponse):
    """Upload a file, extract and preprocess its text, and initialize a chat session.
    Args:
        file (UploadFile): The file to be uploaded.
    Returns:
        dict: A message indicating success and the session ID."""

    if file.filename == "":
        raise HTTPException(status_code=400, detail="No file selected")

    file_path = UPLOAD_DIR / file.filename

    ICON_MAP = {
    ".pdf": "📄",
    ".png": "🖼️",
    ".jpg": "🖼️",
    ".jpeg":"🖼️",
    ".txt": "📄",
    ".docx": "📝",
    ".db": "🗄️",
    ".sqlite":"🗄️" 
    }

    # Getting file type
    ext = os.path.splitext(file.filename)[1].lower()
    icon = ICON_MAP.get(ext, "📁")

    # Save the uploaded file to the upload directory
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:

        # Extract text from the uploaded file
        # This will handle various file types like PDF, DOCX, TXT, etc.
        extracted_text = extract_text_from_file(str(file_path),ext)

        # Get cleaned Processed text
        # from the extracted text to prepare it for vectorization
        cleaned_text = preprocess_text(extracted_text)  

        # Generate unique session ID
        session_id = str(uuid.uuid4())

        # Store session state
        # This will hold the chat history and cleaned text for the session
        # This allows us to maintain context across multiple interactions       
        session_state[session_id] = {
            "chat_history": [AIMessage(content="Hi! I've processed your PDF files. How can I help you?")], 
            "cleaned_text": cleaned_text
        }       
        
        return {"message": "File processed successfully", 
                "filename": file.filename,
                "filetype": file.content_type,
                "icon": icon,
                "session_id": session_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
        