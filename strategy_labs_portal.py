import streamlit as st
from openai import OpenAI
import datetime

# Page config
st.set_page_config(
    page_title="Strategy Labs - AI Portal",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        height: 40px;
        font-weight: 500;
    }
    .new-chat-btn > button {
        background-color: #0ea5e9;
        color: white;
        border: none;
    }
    .new-chat-btn > button:hover {
        background-color: #0284c7;
    }
    .send-btn > button {
        background-color: #0f172a;
        color: white;
        float: right;
    }
    .send-btn > button:hover {
        background-color: #1e293b;
    }
    .kb-item {
        padding: 8px;
        margin: 4px 0;
        border-radius: 4px;
        cursor: pointer;
    }
    .section-header {
        color: #6b7280;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        margin: 16px 0 8px 0;
    }
    div[data-testid="stSidebarContent"] {
        background-color: #f8fafc;
    }
    .assistant-header {
        background-color: #0ea5e9;
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        display: inline-block;
        margin-bottom: 16px;
        font-weight: 500;
    }
    .system-message {
        background-color: #f0f9ff;
        border-left: 4px solid #0ea5e9;
        padding: 12px;
        margin: 16px 0;
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add initial assistant message
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hi! I'm the Strategy Labs assistant. Ask me about campaigns, dashboards, or SOPs. Use Upload Docs* to add context."
    })

if "knowledge_bases" not in st.session_state:
    st.session_state.knowledge_bases = {
        "Playbooks": True,
        "Client Wikis": True,
        "Campaign Docs": False,
        "SOPs": False
    }

# Sidebar
with st.sidebar:
    # Logo and title
    st.markdown("### 🤖 STRATEGY LABS")
    st.markdown("AI Portal")
    
    # New Chat button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<div class="new-chat-btn">', unsafe_allow_html=True)
        if st.button("➕ New Chat", key="new_chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Hi! I'm the Strategy Labs assistant. Ask me about campaigns, dashboards, or SOPs. Use Upload Docs* to add context."
            })
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Knowledge Bases section
    st.markdown('<p class="section-header">📚 KNOWLEDGE BASES</p>', unsafe_allow_html=True)
    
    # Knowledge base checkboxes
    st.session_state.knowledge_bases["Playbooks"] = st.checkbox("Playbooks", value=st.session_state.knowledge_bases["Playbooks"])
    st.session_state.knowledge_bases["Client Wikis"] = st.checkbox("Client Wikis", value=st.session_state.knowledge_bases["Client Wikis"])
    st.session_state.knowledge_bases["Campaign Docs"] = st.checkbox("Campaign Docs", value=st.session_state.knowledge_bases["Campaign Docs"])
    st.session_state.knowledge_bases["SOPs"] = st.checkbox("SOPs", value=st.session_state.knowledge_bases["SOPs"])
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        st.button("⬇ Add KB", use_container_width=True)
    with col2:
        st.button("🔧 Build RAG", use_container_width=True)
    
    # Recent section
    st.markdown('<p class="section-header">🕐 RECENT</p>', unsafe_allow_html=True)
    st.empty()  # Placeholder for recent items
    
    # Admin section
    st.markdown('<p class="section-header">⚙️ ADMIN</p>', unsafe_allow_html=True)
    st.empty()  # Placeholder for admin items
    
    # Brand section at bottom
    st.markdown("---")
    st.markdown("**Brand**")
    st.caption("Lato & Bebas Neue • Palette: Deep/Mid/Light blues, Tint, Canvas.")

# Main content area
# Header with assistant name
st.markdown('<span class="assistant-header">🤖 Strategy Labs Assistant</span>', unsafe_allow_html=True)

# Model and temperature controls
col1, col2, col3 = st.columns([2, 3, 2])
with col1:
    model = st.selectbox("🎯 Model", ["GPT-4.1", "GPT-4", "GPT-3.5-turbo"], label_visibility="visible")
with col2:
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, label_visibility="visible")
with col3:
    active_kbs = sum(st.session_state.knowledge_bases.values())
    st.metric("KBs active", active_kbs)

# System message
st.markdown("""
<div class="system-message">
You are Strategy Labs' helpful internal assistant. Be concise, cite sources, and follow brand voice.
</div>
""", unsafe_allow_html=True)

# API Key input
openai_api_key = st.text_input("OpenAI API Key", type="password", placeholder="Enter your OpenAI API key...")

if not openai_api_key:
    st.info("Please add your OpenAI API key to continue. You can get one [here](https://platform.openai.com/account/api-keys).", icon="🔑")
else:
    # Create OpenAI client
    client = OpenAI(api_key=openai_api_key)
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input with file attachment
    col1, col2 = st.columns([10, 1])
    
    with col1:
        # File uploader
        uploaded_file = st.file_uploader("📎 Attach", type=["txt", "pdf", "docx", "csv"], label_visibility="collapsed")
        if uploaded_file:
            st.success(f"File attached: {uploaded_file.name}")
    
    # Chat input
    if prompt := st.chat_input("Ask about campaigns, dashboards, SOPs..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Include knowledge base context in system message
            active_kbs = [kb for kb, active in st.session_state.knowledge_bases.items() if active]
            system_context = f"You are Strategy Labs' helpful internal assistant. Active knowledge bases: {', '.join(active_kbs)}. Be concise, cite sources, and follow brand voice."
            
            try:
                # Create chat completion
                stream = client.chat.completions.create(
                    model="gpt-3.5-turbo",  # Using gpt-3.5-turbo as fallback
                    messages=[
                        {"role": "system", "content": system_context}
                    ] + [
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    stream=True,
                    temperature=temperature
                )
                
                # Stream the response
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                
            except Exception as e:
                full_response = f"Error generating response: {str(e)}"
                message_placeholder.error(full_response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# Footer
st.markdown("---")
st.caption("Built for Strategy Labs • This UI mirrors OpenWebUI patterns with SL brand treatment. [Docs]()")

