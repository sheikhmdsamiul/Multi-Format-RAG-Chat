import os
import sqlite3
from docx import Document
from bangla_pdf_ocr import process_pdf
from PIL import Image
from pytesseract import image_to_string


def extract_text_from_file(file_path):
    if not os.path.exists(file_path):
        return "Error: File not found."

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_from_pdf(file_path)
    elif ext == ".docx":
        return extract_from_docx(file_path)
    elif ext in [".jpg", ".jpeg", ".png"]:
        return extract_from_image(file_path)
    elif ext == ".txt":
        return extract_from_txt(file_path)
    elif ext in [".db", ".sqlite"]:
        return extract_from_db(file_path)
    else:
        raise ValueError("Unsupported file type")
       
       
       
def extract_from_pdf(file):
    """Extract text from PDF file using OCR"""
    if file is None:
        return ""  
      
    try:
        # Extract text using OCR
        extracted_text = process_pdf(file, language="ben+eng")
        return extracted_text if extracted_text else ""
        
    except Exception as e:
        print(f"Error processing PDF file '{file.name}': {str(e)}")
        return ""
    



def extract_from_docx(file_path):
    """Extract text from DOCX file"""
    try:
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    except Exception as e:
        print(f"Error processing DOCX file '{file_path}': {str(e)}")
        return ""
    


def extract_from_image(file_path):
    """Extract text from image file using OCR"""
    try:
        img = Image.open(file_path)
        return image_to_string(img, lang='ben+eng')
    except Exception as e:
        print(f"Error processing image file '{file_path}': {str(e)}")
        return ""
    


def extract_from_txt(file_path):
    """Extract text from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error processing TXT file '{file_path}': {str(e)}")
        return ""

def extract_from_db(file_path):
    """Extract text from SQLite database file"""
    try:
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        extracted_text = ""
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            for row in rows:
                extracted_text += " | ".join(map(str, row)) + "\n"
        
        conn.close()
        return extracted_text.strip()
    except Exception as e:
        print(f"Error processing DB file '{file_path}': {str(e)}")
        return ""
    





    
