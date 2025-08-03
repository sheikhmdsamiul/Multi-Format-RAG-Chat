import shutil
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from main.modules.document_handler import extract_text_from_file


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
        if not extracted_text:
            raise HTTPException(status_code=400, detail="No text extracted from the file")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

    return extracted_text
