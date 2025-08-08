# Multi-Format-RAG-Chat

Multi-Format-RAG-Chat is an AI-powered assistant that enables users to upload documents in various formats and interactively chat with an LLM (Large Language Model) to extract insights, answer questions, and summarize content. The system leverages Retrieval-Augmented Generation (RAG) to provide context-aware responses based on the uploaded document's content. It supports both text and image queries, making it a versatile tool for document analysis and Q&A.

## Features

- **Multi-format Document Support:** Upload and process PDF, DOCX, TXT, image files (JPG, PNG), and SQLite database files.
- **OCR Integration:** Extracts text from images and scanned PDFs using OCR (supports Bangla and English).
- **Retrieval-Augmented Generation (RAG):** Combines document retrieval with LLM-based answer generation for accurate, context-aware responses.
- **Image-to-Text Chat:** Upload images as part of your query; the assistant extracts and incorporates image content into its answers.
- **Session-based Chat:** Maintains chat history and context for each session (in-memory; not persistent across server restarts).
- **File Metadata & Icons:** Upload response includes file name, type, and a file-type icon (e.g., 📄 for PDF, 🗄️ for SQLite DB).
- **Modern UI:** Streamlit-based frontend for seamless document upload and chat experience.

## Architecture

- **Backend:** Modular FastAPI REST API, LangChain, Groq LLM, HuggingFace models, FAISS vector store, OCR (pytesseract, bangla_pdf_ocr)
- **Frontend:** Streamlit app for user interaction
- **Modular API:** Endpoints are organized in separate modules (e.g., `endpoints/chat.py`, `endpoints/upload_file.py`, `endpoints/home.py`) and included in the main FastAPI app using APIRouter for clarity and maintainability.

## Technical Implementation Details

- **API Layer:**
  - Built with FastAPI, exposing endpoints for file upload, health check, and RAG-based chat.
  - Handles file uploads asynchronously and manages session state in memory.

- **Document Handling:**
  - Supports PDF, DOCX, TXT, image (JPG, PNG), and SQLite DB files.
  - Uses `bangla_pdf_ocr` and `pytesseract` for OCR on PDFs and images (Bangla and English support).
  - Extracts and preprocesses text for downstream processing.

- **Vector Store & Embeddings:**
  - Text is split into semantic chunks using LangChain’s `SemanticChunker`.
  - Embeddings are generated with HuggingFace models (`intfloat/multilingual-e5-base`).
  - Chunks are stored in a FAISS vector store for efficient retrieval.

- **Retrieval-Augmented Generation (RAG):**
  - User queries (and optionally images) are combined with chat history.
  - Relevant document chunks are retrieved and re-ranked using a cross-encoder (`BAAI/bge-reranker-base`).
  - The Groq LLM (via LangChain) generates context-aware answers using the retrieved context.

- **Session Management:**
  - Each document upload creates a unique session (UUID) with its own chat history and cleaned text.
  - Session state is stored in memory for fast access during chat. For production, consider persistent or distributed session storage for scalability and reliability.

- **Frontend:**
  - Streamlit app for uploading documents, chatting, and uploading images as part of queries.
  - Communicates with the FastAPI backend via HTTP requests.

- **Configuration:**
  - Sensitive keys (e.g., Groq API key) are loaded from a `.env` file using `python-dotenv`.

- **Extensibility:**
  - Modular code structure allows easy addition of new file types, models, or endpoints.

## Getting Started

### Prerequisites
- Python 3.8+
- [Groq API Key](https://console.groq.com/)
- [HuggingFace account](https://huggingface.co/) (for model downloads)
- Docker (recommended for backend deployment)

### Quick Start

#### 1. Clone the repository:
```bash
git clone https://github.com/sheikhmdsamiul/Multi-Format-RAG-Chat.git
cd Multi-Format-RAG-Chat
```

#### 2. Set up environment variables:
- Create a `.env` file in the project root with your Groq API key:
  ```env
  GROQ_API_KEY=your_groq_api_key_here
  ```

#### 3. Run the FastAPI backend (choose one):

- **Option 1: Using the pre-built Docker image (recommended):**
  ```sh
  docker pull sheikhmdsamiul/multi-format-rag-chat-api
  docker run -p 8000:8000 sheikhmdsamiul/multi-format-rag-chat-api
  ```

- **OR**

- **Option 2: Run outside Docker (manual Python environment):**
  ```sh
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  pip install -r requirements.txt
  bangla-pdf-ocr-setup
  uvicorn main.server.api:app --reload
  ```

#### 4. Run the Streamlit frontend on your host (outside Docker):
Make sure you have Python and the required dependencies installed on your host:
```bash
pip install -r requirements.txt
streamlit run main/frontend/app.py
```

#### 5. Open the App
- Visit [http://localhost:8501](http://localhost:8501) in your browser for the Streamlit UI.
- The FastAPI backend will be available at [http://localhost:8000](http://localhost:8000).

> **Note:** The Streamlit frontend communicates with the FastAPI backend at `http://localhost:8000`. Ensure both are running for full functionality.


## Usage
1. **Upload a Document:**
   - Supported formats: PDF, DOCX, TXT, JPG, PNG, SQLite DB
   - The backend extracts and preprocesses the text (including OCR for images and scanned PDFs).
2. **Chat with the Assistant:**
   - Ask questions about the document content.
   - Optionally, upload an image as part of your query for image-to-text Q&A.
   - The assistant uses RAG to retrieve relevant context and generate accurate answers.
3. **Session Management:**
   - Each upload creates a new session with its own chat history.
   - You can clear the chat or upload a new document at any time.

## File Structure
```
Multi-Format-RAG-Chat/
├── main/
│   ├── frontend/
│   │   └── app.py                   # Streamlit frontend
│   ├── modules/
│   │   ├── document_handler.py      # Document and image text extraction
│   │   ├── process_vector_store.py  # Text preprocessing and vector store
│   │   └── rag_chat.py              # RAG chat logic
│   └── server/
│       ├── api.py                   # Main FastAPI app, includes routers
│       ├── endpoints/
│       │   ├── chat.py              # RAG chat endpoint
│       │   ├── upload_file.py       # File upload endpoint
│       │   └── home.py              # Health check endpoint
│       ├── schema.py                # Pydantic models for requests/responses
│       └── session.py               # Session state management
├── .env                             # Environment variables
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Docker build file for backend
└── README.md
```

## API Usage

#### File-Type Icon Mapping
The backend automatically assigns an icon to each uploaded file based on its extension:
- `.pdf`, `.txt` → 📄
- `.docx` → 📝
- `.png`, `.jpg`, `.jpeg` → 🖼️
- `.db`, `.sqlite` → 🗄️
- (Other/unknown types) → 📁

### Health Check
`GET /`
```json
{
  "message": "Welcome to the Multi-Format-RAG-Chat API"
}
```

### Upload File
`POST /uploadfile`
- **Request:** Multipart form-data with a file field (PDF, DOCX, TXT, JPG, PNG, DB, SQLITE)
- **Response:**
  - `200 OK` on success
```json
{
  "message": "File processed successfully",
  "filename": "example.pdf",
  "filetype": "application/pdf",
  "icon": "📄",
  "session_id": "<session-uuid>"
}
```
  - `400 Bad Request` if no file is selected
  - `500 Internal Server Error` on processing failure

### RAG Chat
`POST /rag_chat`
- **Request (JSON):**
```json
{
  "query": {
    "query": "What is the total amount?",
    "image": "<optional base64 image>"
  },
  "session_id": "<session-uuid>"
}
```
- **Response:**
  - `200 OK` on success
```json
{
  "chat_history": [
    {"role": "user", "content": "What is the total amount?"},
    {"role": "assistant", "content": "The total amount is ..."}
  ],
  "response": "The total amount is ..."
}
```
  - `404 Not Found` if session is missing
  - `400 Bad Request` if query/image is missing
  - `500 Internal Server Error` on processing failure

## Sample Queries and Outputs
*Note: Outputs are examples and may vary depending on the document and model version.*
**Context file: [PDF](https://ncert.nic.in/textbook/pdf/lekl101.pdf)**

### English
**Query:** Who is Gabriel Garcia Marquez?
**Output:**
>Answer: Gabriel Garcia Marquez is a novelist, short-story writer, and journalist widely considered the greatest living Latin American master of narrative.

>Supporting Context: "Gabriel Garcia Marquez was brought up by his grandparents in Northern Columbia because his parents were poor and struggling. A novelist, short-story writer and journalist, he is widely considered the greatest living Latin American master of narrative."

>Source: Page 2

>Confidence: High - The text directly states Marquez's profession and reputation, providing a clear and concise description of who he is.

**Query:** What was Pablo Neruda’s reaction to Frau Frieda’s dreams?
**Output:**
>Answer: Pablo Neruda did not believe in prophetic dreams, saying "Only poetry is clairvoyant."

>Supporting Context: "He paid no attention, for from the very beginning he had announced that he did not believe in prophetic dreams. 'Only poetry is clairvoyant,' he said."

>Source: Page 7, "I Set my Dreams"

>Confidence: High - The text directly quotes Neruda's statement, clearly indicating his skepticism towards Frau Frieda's dreams.

### Bangla
**Query:** ফ্রাউ ফ্রিদা কীভাবে জীবিকা নির্বাহ করতেন এবং তিনি কেন নিজেকে বলেন ‘আমি স্বপ্ন বিক্রি করি’?
**Output:**
>Answer: ফ্রাউ ফ্রিদা তার স্বপ্নের ব্যাখ্যা দিয়ে জীবিকা নির্বাহ করতেন। তিনি ভিয়েনায় একটি প���িবারের জন্য কাজ করতেন, যেখানে তিনি প্রতিদিন সকালে তার স্বপ্নের মাধ্যমে পরিবারের সদস্যদের ভবিষ্যত সম্পর্কে বলতেন। তিনি নিজেকে বলেন 'আমি স্বপ্ন বিক্রি করি' কারণ তিনি তার স্বপ্নের ব্যাখ্যা দিয়ে অর্থ উপার্জন করতেন।

>Supporting Context: "In reality, that was her only trade. ... She looked for work at the first house where she would have liked to live, and when she was asked what she could do, she told only the truth: 'I dream.'"

>Source: Page5, "my Dreams"

>Confidence: High - পাঠ্যটি স্পষ্টভাবে ফ্রাউ ফ্রিদার জীবিকা নির্বাহের উপায় এবং তার স্বপ্ন বিক্রির কারণ ব্যাখ্যা করে।


## Dependencies
- FastAPI
- Streamlit
- LangChain
- Groq LLM
- HuggingFace Transformers & Embeddings
- FAISS
- pytesseract, Pillow
- bangla_pdf_ocr
- python-docx
- requests
- python-dotenv
- Docker

## Acknowledgements
- [LangChain](https://github.com/langchain-ai/langchain)
- [Groq](https://groq.com/)
- [bangla-pdf-ocr](https://pydigger.com/pypi/bangla-pdf-ocr)
- [HuggingFace](https://huggingface.co/)
- [Streamlit](https://streamlit.io/)
- [pytesseract](https://github.com/madmaze/pytesseract)

---
