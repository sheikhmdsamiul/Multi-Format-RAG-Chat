import shutil
from pathlib import Path
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel
from typing import List, Dict
from main.modules.document_handler import extract_text_from_file
from main.modules.process_vector_store import preprocess_text
from main.modules.rag_chat import rag_chat


app = FastAPI()

# Create upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Stores session-specific chat history and cleaned text for each session.
session_state: Dict[str, Dict] = {}


class chatrequest(BaseModel):
    """Request model for chat endpoint containing user query and session ID."""
    query: str
    session_id: str

@app.get("/test")
async def test():
    """Health check endpoint to verify API is running."""
    return {"message": "Welcome to the Document Processing API"}



@app.post("/uploadfile")
async def create_upload_file(file: UploadFile = File(...)):
    """Upload a file, extract and preprocess its text, and initialize a chat session."""

    if file.filename == "":
        raise HTTPException(status_code=400, detail="No file selected")

    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:

        # Extract text from the uploaded file
        extracted_text = extract_text_from_file(str(file_path))

        # Get cleaned Processed text
        cleaned_text = preprocess_text(extracted_text)  

        # Generate unique session ID
        session_id = str(uuid.uuid4())

        # Store session state
        session_state[session_id] = {
            "chat_history": [AIMessage(content="Hi! I've processed your PDF files. How can I help you?")], 
            "cleaned_text": cleaned_text
        }       
        
        return {"message": "File processed successfully", "session_id": session_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    

@app.post("/rag_chat")
async def rag_chat_endpoint(request: chatrequest, ):
    """Endpoint for RAG chat with the given query and context."""

    # Check if session exists
    session = session_state.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Retrieve chat history and cleaned text from session
    chat_history = session["chat_history"]
    cleaned_text = session["cleaned_text"]
        
    try:
        response = rag_chat(request.query, chat_history, cleaned_text)
        if response:
            # Append the new user query to chat history
            chat_history.append(HumanMessage(content=request.query))

            # Convert history to JSON-safe format
            history_json = [{"role": msg.type, "content": msg.content} for msg in chat_history]
            
            # Append the AI response to chat history
            chat_history.append(AIMessage(content=response))
    
        

        return {"chat_history": history_json, "response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in RAG chat: {str(e)}")
    
    
    
