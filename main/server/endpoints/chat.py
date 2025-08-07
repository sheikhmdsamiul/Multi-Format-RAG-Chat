import base64
from io import BytesIO
from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage, AIMessage

from main.modules.rag_chat import rag_chat
from main.modules.document_handler import extract_from_image
from main.server.schema import ChatResponse, chatrequest
from main.server.session import session_state

router = APIRouter()


# Endpoint for RAG chat with the given query and context.
@router.post("/rag_chat", response_model = ChatResponse)
async def rag_chat_endpoint(request: chatrequest):
    """Endpoint for RAG chat with the given query and context.
    Args:
        request (chatrequest): The request containing user query and session ID.
    Returns:
        ChatResponse: The response containing chat history and generated response."""
    
    # Validate session ID
    session = session_state.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Retrieve chat history and cleaned text from session
    chat_history = session["chat_history"]
    cleaned_text = session["cleaned_text"]
    
    # Extract user query and image if present
    # If the user query is empty, returns an error
    # If an image is provided, decode it and extract text from the image
    # This allows to combine the query and image context for the RAG chat
    user_query = request.query["query"] if "query" in request.query else ""
    image_base64 = request.query["image"] if "image" in request.query else None
    
    try:

        combined_input = user_query
        
        # Process image if present
        if image_base64:
            # Decode the base64 image
            image_data = base64.b64decode(image_base64)

            # Create a BytesIO object from the decoded image data
            image = BytesIO(image_data)

            # Extract text from the image
            # This will use OCR to extract text from the image
            image_context = extract_from_image(image)
            
            # and combine it with the user query
            if image_context.strip():
                combined_input = f"{user_query}\n\nImage content: {image_context}".strip()
        
        # Only proceed if we have some input
        if not combined_input.strip():
            raise HTTPException(status_code=400, detail="No query or image content provided")
        
        # Add user message to history (store the original query, not combined)
        # This allows to maintain the original text user query in the chat history
        chat_history.append(HumanMessage(content=user_query if user_query else "Uploaded an image"))
        
        # Get RAG response with combined input
        response = rag_chat(combined_input, chat_history, cleaned_text)
        
        # Add AI response to history
        if response:
            chat_history.append(AIMessage(content=response))
            
            # Convert history to JSON-safe format
            # This is to ensure the chat history can be serialized properly
            history_json = [{"role": msg.type, "content": msg.content} for msg in chat_history]
            
            return {"chat_history": history_json, "response": response}
        else:
            raise HTTPException(status_code=500, detail="No response generated")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in RAG chat: {str(e)}")