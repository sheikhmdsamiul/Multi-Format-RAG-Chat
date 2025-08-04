import shutil
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from langchain_huggingface import HuggingFaceEmbeddings
from main.modules.document_handler import extract_text_from_file
from main.modules.process_vector_store import preprocess_text, semantic_text_splitter, get_vector_store


app = FastAPI()

# Create upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/test")
async def test():
    return {"message": "Welcome to the Document Processing API"}



@app.post("/uploadfile")
async def create_upload_file(file: UploadFile = File(...)):
    """Endpoint to upload a file and extract text from it.""" 
    """Upload a single file with basic validation"""
    if file.filename == "":
        raise HTTPException(status_code=400, detail="No file selected")

    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        extracted_text = extract_text_from_file(str(file_path))

        cleaned_text = preprocess_text(extracted_text)

        #chunked_text = semantic_text_splitter(cleaned_text)
        vector_store = get_vector_store(cleaned_text)

        retriver = vector_store.as_retriever(search_kwargs={"k": 1})
        invoke = retriver.invoke("What is the content of the uploaded file?")
    

        
        return invoke
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
