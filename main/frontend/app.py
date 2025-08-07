from io import BytesIO
import streamlit as st
import requests
import base64
from PIL import Image

# Configure page
st.set_page_config(page_title="RAG Chat", page_icon="🤖", layout="centered")

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'messages' not in st.session_state:
    st.session_state.messages = []


# Helper functions
def upload_file(file):
    """
    Upload a file to the backend API for processing.

    Args:
        file (UploadedFile): The file object selected by the user in Streamlit.

    Returns:
        tuple: (success (bool), response (dict or str))
            - success: True if upload and processing succeeded, False otherwise.
            - response: JSON response from the API if successful, or error message string.
    """
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.post(f"{API_BASE_URL}/uploadfile", files=files)
        return response.status_code == 200, response.json() if response.status_code == 200 else response.text
    except Exception as e:
        return False, str(e)

def send_message(query, session_id):
    """
    Send a chat message (and optional image) to the backend RAG chat API.

    Args:
        query (dict): The user query and optional image in base64 format.
        session_id (str): The current chat session ID.

    Returns:
        tuple: (success (bool), response (dict or str))
            - success: True if the chat request succeeded, False otherwise.
            - response: JSON response from the API if successful, or error message string.
    """
    try:
        payload = {"query": query, "session_id": session_id}
        response = requests.post(f"{API_BASE_URL}/rag_chat", json=payload)
        return response.status_code == 200, response.json() if response.status_code == 200 else response.text
    except Exception as e:
        return False, str(e)

# Main UI
st.title("🤖 RAG Chat Assistant")

# File upload section
if not st.session_state.session_id:
    st.markdown("### Upload a document to get started")
    
    uploaded_file = st.file_uploader(
        "Choose a file", 
        type=['pdf', 'txt', 'docx', 'doc', 'jpg', 'jpeg', 'png', 'db', 'sqlite'],
        help="Upload a document to chat with"
    )
    
    if uploaded_file:
        if st.button("Process Document", type="primary"):
            with st.spinner("Processing document..."):
                success, result = upload_file(uploaded_file)
                
                if success:
                    st.session_state.session_id = result['session_id']
                    st.session_state.messages = [{"role": "assistant", "content": "Hi! I've processed your document. What would you like to know?"}]
                    st.success("Document processed successfully!")
                    st.rerun()
                else:
                    st.error(f"Error: {result}")

        

# Chat interface
else:
    # Display message history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if "image" in message and message["image"]:
                st.image(message["image"], caption="Uploaded Image", use_container_width=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        user_query = st.chat_input("Ask me anything about your document...")
    with col2:
        # Add key parameter to reset the uploader
        uploaded_image = st.file_uploader( 
            label= "Upload an image",
            type=["png", "jpg", "jpeg"],
            key=f"image_uploader_{len(st.session_state.messages)}"  # Dynamic key
        )

    if user_query or uploaded_image:
        image_base64 = None
        display_image = None
        
        # Handle image if uploaded
        if uploaded_image:
            image = Image.open(uploaded_image)
            display_image = image.copy()
            
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            image_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Add user message to session state
        user_message = {
            "role": "user", 
            "content": user_query if user_query else ""
        }
        if display_image:
            user_message["image"] = display_image
        
        st.session_state.messages.append(user_message)
        
        # Display user message
        with st.chat_message("user"):
            if user_query:
                st.write(user_query)
            if display_image:
                st.image(display_image, caption="Uploaded Image", use_container_width=True)
        
        # Create API payload
        prompt = {
            "query": user_query if user_query else "",
            "image": image_base64 if image_base64 else None
        }
        
        # Get AI response
        with st.spinner("Thinking..."):
            success, result = send_message(query=prompt, session_id=st.session_state.session_id)
            
            if success:
                response = result["response"]
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                with st.chat_message("assistant"):
                    st.write(response)
                
                st.rerun()  # This will reset the file uploader
            else:
                st.error(f"Error: {result}")
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 New Document"):
            st.session_state.session_id = None
            st.session_state.messages = []
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = [{"role": "assistant", "content": "Hi! I've processed your document. What would you like to know?"}]
            st.rerun()