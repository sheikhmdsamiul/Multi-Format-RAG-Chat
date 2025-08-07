import os
import sqlite3
from docx import Document
from bangla_pdf_ocr import process_pdf
from PIL import Image
from pytesseract import image_to_string


def extract_text_from_file(file_path: bytes):
    if not os.path.exists(file_path):
        return "Error: File not found."

    # Determine the file type based on the extension
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
       
       
# Extract text from PDF file using bangla-pdf-ocr
def extract_from_pdf(file_path):
    """Extract text from PDF file using OCR
    Args:
        file_path (str): The path to the PDF file.
    Returns:
        str: The extracted text from the PDF file."""
    

    if file_path is None:
        return ""  
      
    try:
        extracted_text = process_pdf(file_path, language="ben+eng")
        return extracted_text if extracted_text else ""
        
    except Exception as e:
        print(f"Error processing PDF file '{file_path.name}': {str(e)}")
        return ""
    

# Extract text from DOCX file
def extract_from_docx(file_path):
    """Extract text from DOCX file
    Args:
        file_path (str): The path to the DOCX file.
    Returns:
        str: The extracted text from the DOCX file."""
    
    try:
        # Open the DOCX file and read its content
        doc = Document(file_path)

        # Extract text from each paragraph and join them
        # This will return a single string with all the text from the document
        return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    
    except Exception as e:
        print(f"Error processing DOCX file '{file_path}': {str(e)}")
        return ""
    

# Extract text from image file using pytesseract
def extract_from_image(file_path):
    """Extract text from image file using OCR
    Args:
        file_path (str): The path to the image file.
    Returns:
        str: The extracted text from the image file."""
    
    try:
        # Open the image file as PIL Image
        img = Image.open(file_path)

        # Use pytesseract to extract text from the image
        return image_to_string(img, lang='ben+eng')
    except Exception as e:
        print(f"Error processing image file '{file_path}': {str(e)}")
        return ""
    

# Extract text from TXT file
def extract_from_txt(file_path):
    """Extract text from TXT file
    Args:
        file_path (str): The path to the TXT file.
    Returns:
        str: The extracted text from the TXT file."""
    
    try:
        # Open the file and read its content
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error processing TXT file '{file_path}': {str(e)}")
        return ""



def extract_from_db(file_path):
    """Extract text from SQLite database file
    Args:
        file_path (str): The path to the SQLite database file.
    Returns:
        str: The extracted text from the database file."""
    
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(file_path)

        # Create a cursor object to execute SQL queries
        cursor = conn.cursor()
        
        # Get the names of all tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

        # Fetch all table names
        tables = cursor.fetchall()
        
        extracted_text = ""
        for table in tables:
            table_name = table[0]

            # Fetch all rows from the table
            cursor.execute(f"SELECT * FROM {table_name}")

            # Fetch all rows and concatenate them into a string
            rows = cursor.fetchall()
            for row in rows:
                extracted_text += " | ".join(map(str, row)) + "\n"
        
        conn.close()
        return extracted_text.strip()
    except Exception as e:
        print(f"Error processing DB file '{file_path}': {str(e)}")
        return ""
    





    
