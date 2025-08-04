import re
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

EMBEDDING_MODEL = "intfloat/multilingual-e5-base"

embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL
        )


def preprocess_text(text):
    """Preprocess extracted text by cleaning lines"""
    if not text:
        return ""
    
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    text = re.sub(r'\n+', '\n', text)  # Replace multiple newlines with a single newline
    
    lines = text.splitlines()
    cleaned_lines = []
    
    for line in lines:
        cleaned_line = line.strip()
        if cleaned_line:  
            cleaned_lines.append(cleaned_line)
    
    return "\n".join(cleaned_lines)



def semantic_text_splitter(text):
    """Split text into semantic chunks"""
    if not text:
        return []
    
    text_splitter = SemanticChunker(embeddings)

    docs = text_splitter.create_documents([text])

    return docs

def get_vector_store(documents):
    """Create and return vectorstore for the documents"""
    
    try:      
        
        chunks = semantic_text_splitter(documents)

        
        vector_store = FAISS.from_documents(chunks, embeddings)
        save_path = "vector_store"
        vector_store.save_local(save_path)
        return vector_store
    
    
    except Exception as e:
        raise ValueError(f"Error creating vector store: {str(e)}")