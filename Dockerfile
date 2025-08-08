# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for OCR and PDF/image handling
RUN apt-get update && \
    apt-get install -y tesseract-ocr libtesseract-dev poppler-utils supervisor && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Run bangla-pdf-ocr setup to install additional dependencies
RUN bangla-pdf-ocr-setup

# Copy project files
COPY . .

# Expose FastAPI 
EXPOSE 8000 

# Set environment variables
ENV PYTHONUNBUFFERED=1


CMD ["uvicorn", "main.server.api:app", "--host", "0.0.0.0", "--port", "8000"]
