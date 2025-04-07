import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaLLM as Ollama
import os
from dotenv import load_dotenv
import time


load_dotenv()
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_API_KEY'] = os.getenv('LANGCHAIN_API_KEY')

st.set_page_config(
    page_title="ChatBuddy",
    page_icon="🤖",
    layout="wide"
)


st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .chat-container {
        border-radius: 10px;
        padding: 20px;
        background-color: #f9f9f9;
    }
    .user-message {
        background-color: #e1f5fe;
        border-radius: 15px;
        padding: 10px 15px;
        margin: 5px 0;
    }
    .assistant-message {
        background-color: #f0f4f8;
        border-radius: 15px;
        padding: 10px 15px;
        margin: 5px 0;
    }
    .chat-header {
        text-align: center;
        margin-bottom: 20px;
    }
    .settings-button {
        font-size: 24px;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)


if "show_settings" not in st.session_state:
    st.session_state.show_settings = False

header_col1, header_col2 = st.columns([0.9, 0.1])
with header_col1:
    st.title("💬 ChatBuddy")
with header_col2:
    if st.button("⚙️", help="Toggle Settings"):
        st.session_state.show_settings = not st.session_state.show_settings
        st.rerun()


if st.session_state.show_settings:
    with st.expander("Settings", expanded=True):

        model_name = "llama2"
        st.info("Using Ollama llama2 model")
        
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Higher values make output more random, lower values more deterministic"
        )
        
        if st.button("Clear Conversation"):
            st.session_state.chat_history = []
            st.session_state.conversation_started = False
            st.rerun()
        
        st.divider()
        st.markdown("Built with Langchain + Ollama")
else:
   
    model_name = "llama2"
    temperature = 0.7

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "conversation_started" not in st.session_state:
    st.session_state.conversation_started = False

if "thinking" not in st.session_state:
    st.session_state.thinking = False

chat_container = st.container()

@st.cache_resource
def get_llm(temperature):
    try:
        return Ollama(model="llama2", temperature=temperature)
    except Exception as e:
        st.error(f"Error initializing Ollama llama2 model: {e}")
        return None


user_input = st.chat_input("Ask me anything...", disabled=st.session_state.thinking)


if user_input:

    st.session_state.thinking = True
    st.session_state.conversation_started = True
    
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    with chat_container:
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)
    
if st.session_state.thinking:
    base_messages = [("system", "You are a helpful AI assistant named ChatBuddy. You're knowledgeable, friendly, and precise in your responses. Please provide accurate and helpful information to the user's queries.")]
    
    
    chat_messages = base_messages.copy()
    for msg in st.session_state.chat_history:
        chat_messages.append((msg["role"], msg["content"]))
    
    prompt = ChatPromptTemplate.from_messages(chat_messages)
    
    llm = get_llm(temperature)
    output_parser = StrOutputParser()
    
    if llm:
        chain = prompt | llm | output_parser
        
        try:
           
            with st.spinner("ChatBuddy is thinking..."):
                response = chain.invoke({"question": st.session_state.chat_history[-1]["content"]})
                
                st.session_state.chat_history.append({"role": "assistant", "content": response})
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
    else:
        st.session_state.chat_history.append({"role": "assistant", "content": "Sorry, I'm having trouble connecting to the language model. Please check your Ollama setup and try again."})

    st.session_state.thinking = False
    

    st.rerun()

with chat_container:
    if not st.session_state.conversation_started:
        st.markdown("""
        ## Welcome to ChatBuddy! 👋
        
        I'm here to assist you with information, answer questions, or just chat.
        
        Click the ⚙️ button in the top right to access settings.
        """)
    

    displayed_user_messages = set()
    
    for i, msg in enumerate(st.session_state.chat_history):
        if msg["role"] == "user":
            if user_input and msg["content"] == user_input:
                
                continue
            with st.chat_message("user", avatar="👤"):
                st.markdown(msg["content"])
            displayed_user_messages.add(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(msg["content"])