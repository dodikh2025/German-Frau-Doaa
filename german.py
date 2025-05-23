import streamlit as st
import requests
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="German Learning Bot - Frau Doaa",
    page_icon="🇩🇪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f4e79;
        margin-bottom: 2rem;
    }
    .chat-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .user-message {
        background-color: #007bff;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        text-align: right;
    }
    .bot-message {
        background-color: #28a745;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        text-align: left;
    }
    .error-message {
        background-color: #dc3545;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'conversation_id' not in st.session_state:
    st.session_state.conversation_id = None

# Dify API configuration
DIFY_API_BASE_URL = "https://api.dify.ai/v1"
APP_TOKEN = "app-N2rqhiYbVvY73Wnvf9FOmULU"

def call_dify_api(message, conversation_id=None):
    """
    Call the Dify API to get a response from the German learning bot
    """
    url = f"{DIFY_API_BASE_URL}/chat-messages"
    
    headers = {
        "Authorization": f"Bearer {APP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": {},
        "query": message,
        "response_mode": "blocking",
        "user": st.session_state.get('user_id', 'streamlit_user')
    }
    
    if conversation_id:
        payload["conversation_id"] = conversation_id
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return {
            "success": True,
            "answer": result.get("answer", ""),
            "conversation_id": result.get("conversation_id", ""),
            "message_id": result.get("message_id", "")
        }
    
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"API request failed: {str(e)}"
        }
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Invalid JSON response: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }

# Main app layout
st.markdown('<h1 class="main-header">🇩🇪 German Learning Bot by Frau Doaa</h1>', unsafe_allow_html=True)

# Sidebar for settings and information
with st.sidebar:
    st.header("📚 About")
    st.info("Welcome to your German learning companion! Ask questions about German grammar, vocabulary, pronunciation, or practice conversations.")
    
    st.header("⚙️ Settings")
    if st.button("🔄 Clear Conversation"):
        st.session_state.messages = []
        st.session_state.conversation_id = None
        st.success("Conversation cleared!")
    
    st.header("📊 Statistics")
    st.metric("Messages in this session", len(st.session_state.messages))
    
    st.header("💡 Tips")
    st.markdown("""
    - Ask about German grammar rules
    - Practice vocabulary with translations
    - Request pronunciation help
    - Have conversations in German
    - Ask for explanations in English when needed
    """)

# Main chat interface
col1, col2, col3 = st.columns([1, 6, 1])

with col2:
    # Display chat messages
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'<div class="user-message">You: {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bot-message"> {message["content"]}</div>', unsafe_allow_html=True)
    
    # Input form
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "Ask Frau Doaa about German learning:",
            placeholder="Type your question in English or German or Arabic...",
            height=100,
            key="user_input"
        )
        
        col_submit, col_attach = st.columns([3, 1])
        
        with col_submit:
            submit_button = st.form_submit_button("Send 📤", use_container_width=True)
        
        with col_attach:
            uploaded_file = st.file_uploader(
                "",
                type=['txt', 'pdf', 'docx', 'jpg', 'jpeg', 'png'],
                key="file_upload",
                label_visibility="collapsed"
            )
    
    # Handle form submission
    if submit_button and user_input.strip():
        # Add user message to chat
        message_content = user_input
        
        # Handle file upload if present
        if uploaded_file is not None:
            message_content += f" [Attached file: {uploaded_file.name}]"
        
        st.session_state.messages.append({"role": "user", "content": message_content})
        
        # Show loading spinner
        with st.spinner("Frau Doaa is thinking... 🤔"):
            # Call Dify API
            response = call_dify_api(user_input, st.session_state.conversation_id)
            
            if response["success"]:
                # Update conversation ID
                if response.get("conversation_id"):
                    st.session_state.conversation_id = response["conversation_id"]
                
                # Add bot response to chat
                bot_response = response["answer"]
                st.session_state.messages.append({"role": "bot", "content": bot_response})
                
                # Rerun to update the display
                st.rerun()
            else:
                # Show error message
                st.markdown(f'<div class="error-message">Error: {response["error"]}</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666;">Powered by Dify AI • Created with ❤️ for German learners</div>',
    unsafe_allow_html=True
)
