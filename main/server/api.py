"""
Main FastAPI application entry point.
Includes routers for health check, file upload, and RAG chat endpoints.
"""

from fastapi import FastAPI
from .endpoints import home, upload_file, chat


app = FastAPI(
    title="Multi-Format-RAG-Chat API",
    description="API for document upload and Retrieval-Augmented Generation (RAG) chat with multi-format support.",
    version="1.0.0"
)

app.include_router(home.router)
app.include_router(upload_file.router)
app.include_router(chat.router)








    
    



    
    

    
    
    
