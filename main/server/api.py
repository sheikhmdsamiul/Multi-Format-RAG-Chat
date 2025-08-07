import base64
from io import BytesIO
import json
import shutil
from pathlib import Path
import uuid
from PIL import Image
from fastapi import FastAPI, File, UploadFile, HTTPException
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel
from typing import Dict
from main.modules.document_handler import extract_text_from_file, extract_from_image
from main.modules.process_vector_store import preprocess_text
from main.modules.rag_chat import rag_chat


app = FastAPI()

# Create upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Stores session-specific chat history and cleaned text for each session.
session_state: Dict[str, Dict] = {}

# Define the request model for the chat endpoint
class chatrequest(BaseModel):
    """Request model for chat endpoint containing user query and session ID."""
    query: dict 
    session_id: str

# Health check endpoint to verify API is running
@app.get("/")
async def home():
    """Health check endpoint to verify API is running."""
    return {"message": "Welcome to the Document Processing API"}


# Endpoint to upload a file, extract and preprocess its text, and initialize a chat session.
@app.post("/uploadfile")
async def create_upload_file(file: UploadFile = File(...)):
    """Upload a file, extract and preprocess its text, and initialize a chat session."""

    if file.filename == "":
        raise HTTPException(status_code=400, detail="No file selected")

    file_path = UPLOAD_DIR / file.filename

    # Save the uploaded file to the upload directory
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
    
    
# Endpoint for RAG chat with the given query and context.
@app.post("/rag_chat")
async def rag_chat_endpoint(request: chatrequest):
    """Endpoint for RAG chat with the given query and context."""
    
    # Validate session ID
    session = session_state.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    chat_history = session["chat_history"]
    cleaned_text = session["cleaned_text"]
    
    # Extract user query and image if present
    user_query = request.query["query"] if "query" in request.query else ""
    image_base64 = request.query["image"] if "image" in request.query else None
    
    try:
        # Build combined input
        combined_input = user_query
        
        # Process image if present
        if image_base64:
            image_data = base64.b64decode(image_base64)
            image = BytesIO(image_data)
            image_context = extract_from_image(image)
            
            if image_context.strip():
                combined_input = f"{user_query}\n\nImage content: {image_context}".strip()
        
        # Only proceed if we have some input
        if not combined_input.strip():
            raise HTTPException(status_code=400, detail="No query or image content provided")
        
        # Add user message to history (store the original query, not combined)
        chat_history.append(HumanMessage(content=user_query if user_query else "Uploaded an image"))
        
        # Get RAG response with combined input
        response = rag_chat(combined_input, chat_history, cleaned_text)
        
        # Add AI response to history
        if response:
            chat_history.append(AIMessage(content=response))
            
            # Convert history to JSON-safe format
            history_json = [{"role": msg.type, "content": msg.content} for msg in chat_history]
            
            return {"chat_history": history_json, "response": response}
        else:
            raise HTTPException(status_code=500, detail="No response generated")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in RAG chat: {str(e)}")
    
    
    
