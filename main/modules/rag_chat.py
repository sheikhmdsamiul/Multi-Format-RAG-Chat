import os
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain.chains import create_history_aware_retriever  
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from main.modules.process_vector_store import get_vector_store


load_dotenv()

# LLM and re-ranking model configurations
MODEL = "meta-llama/llama-4-maverick-17b-128e-instruct"
RE_RANKING_MODEL = "BAAI/bge-reranker-base"

groq_api_key = os.environ.get("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set.")

llm = ChatGroq(
    groq_api_key=groq_api_key,
    model=MODEL,
    temperature=0.1   
)

def rag_chat(query, chat_history,text):
    """Run RAG chat with the given query and context."""
    if not query:
        return "Query cannot be empty."
    
    # Creating vector store and retriever
    vector_store = get_vector_store(text)
    retriever = vector_store.as_retriever(search_kwargs={"k": 10})

    # Contextualization prompt
    contextualize_prompt = ChatPromptTemplate.from_messages([
        ("system", "Given a chat history and the latest user question, "
                   "reformulate the question so it is standalone. Do NOT answer it."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}")
    ])
    
    # Re-ranker for the retrieved documents
    re_ranker = HuggingFaceCrossEncoder(
        model_name=RE_RANKING_MODEL)
    
    # Cross-encoder compressor
    compressor = CrossEncoderReranker(model=re_ranker, top_n=3)

    # Contextual compression retriever
    compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor, 
            base_retriever=retriever
        )

    # History-aware retriever
    history_aware_retriever = create_history_aware_retriever(
        llm=llm,
        retriever=compression_retriever,
        prompt=contextualize_prompt
    )
    

    # question answer prompt
    qa_prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are an assistant for question-answering tasks."
                    "Use the following pieces of retrieved context to answer the question."
                    "If you don't know the answer, just say that you don't know."
                    "Keep the answer concise and use language relevant to the context."
                    "Finally, provide the context you used to answer and the Source info (e.g., page 3 of invoice.pdf)"
                    "{context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}")
    ])

  
    # Question answer chain
    qa_chain = create_stuff_documents_chain(
        llm=llm,
        prompt=qa_prompt_template     
    )

    # Retrieval chain 
    rag_chain = create_retrieval_chain(
        history_aware_retriever,
        qa_chain
    )


    answer = rag_chain.invoke({
        "input": query,
        "chat_history": chat_history
    })
    
    return answer["answer"]


