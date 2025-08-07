import re
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Define the embedding model to be used
EMBEDDING_MODEL = "intfloat/multilingual-e5-base"

# Initialize the embeddings
embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL
        )

# Preprocess extracted text by cleaning lines
def preprocess_text(text: str):
    """Preprocess extracted text by cleaning lines
    Args:
        text (str): The extracted text to be preprocessed.
    Returns:
        str: The cleaned text with empty lines removed."""
    
    if not text:
        return ""
    
    # Strip each line and remove empty lines
    lines = text.splitlines()
    cleaned_lines = []  
    
    # Strip each line and remove empty lines
    for line in lines:
        cleaned_line = line.strip()
        if cleaned_line:  
            cleaned_lines.append(cleaned_line)
    
    return "\n".join(cleaned_lines)


# Function to split text into semantic chunks
# This function uses the SemanticChunker to create chunks based on semantic meaning
def semantic_text_splitter(text):
    """Split text into semantic chunks

    Args:   
         text (str): The text to be split into chunks.

    Returns:        
         list: A list of semantic chunks."""
    

    if not text:
        return []
    
    # Create a SemanticChunker instance with the embeddings
    text_splitter = SemanticChunker(embeddings, breakpoint_threshold_type="percentile")

    docs = text_splitter.create_documents([text])

    return docs

# Function to create and return a vector store for the documents
# This function uses the FAISS vector store to index the semantic chunks
def get_vector_store(documents):
    """ Create and return a vector store for the documents
    Args:
        documents (list): A list of documents to be indexed in the vector store.
    Returns:
        FAISS: A FAISS vector store containing the indexed documents."""
    
    try:      
        chunks = semantic_text_splitter(documents)

        # Create a FAISS vector store from the chunks
        vector_store = FAISS.from_documents(chunks, embeddings)

        # Save the vector store to a local directory
        # This is useful for later retrieval without needing to reprocess the documents
        # But we used direct retrieval in the RAG chat
        # so this was to ensure the vector store are being created 
        save_path = "vector_store"
        vector_store.save_local(save_path)
        return vector_store
    
    
    except Exception as e:
        raise ValueError(f"Error creating vector store: {str(e)}")