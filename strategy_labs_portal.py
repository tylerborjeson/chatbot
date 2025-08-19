import streamlit as st
from openai import OpenAI
import time

# Configure page
st.set_page_config(
    page_title="Strategy Labs AI Portal",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to match the design
st.markdown("""
<style>
    .main-header {
        background-color: #0f4c75;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .agent-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #0f4c75;
        margin-bottom: 0.5rem;
    }
    .knowledge-base {
        background-color: #e3f2fd;
        padding: 0.5rem;
        border-radius: 4px;
        margin-bottom: 0.25rem;
    }
    .stSelectbox > div > div {
        background-color: #0f4c75;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🎯 STRATEGY LABS")
    st.markdown("**AI Portal**")
    
    # New Chat Button
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    
    # Knowledge Bases Section
    st.markdown("### 📚 KNOWLEDGE BASES")
    
    kb_options = {
        "📖 Playbooks": ["Marketing Playbook", "Sales Process", "Brand Guidelines"],
        "📝 Client Wikis": ["Client A Wiki", "Client B Wiki", "Industry Research"],
        "📊 Campaign Docs": ["Q4 Campaign", "Social Media Strategy", "Email Templates"],
        "📋 SOPs": ["Content Creation SOP", "Client Onboarding", "Reporting Process"]
    }
    
    selected_kb = None
    for kb_type, items in kb_options.items():
        if st.checkbox(kb_type):
            selected_kb = kb_type
            for item in items:
                st.markdown(f'<div class="knowledge-base">• {item}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Add KB and Build RAG buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📁 Add KB"):
            st.info("Upload documents to knowledge base")
    with col2:
        if st.button("🔧 Build RAG"):
            st.info("RAG system building...")
    
    st.markdown("---")
    
    # Recent Section
    st.markdown("### 🕒 RECENT")
    recent_chats = [
        "Content Strategy Discussion",
        "Ad Copy Generation",
        "Client Onboarding Help",
        "Campaign Performance Review"
    ]
    
    for chat in recent_chats:
        if st.button(f"💬 {chat}", key=chat):
            st.info(f"Loading {chat}...")
    
    st.markdown("---")
    
    # Admin Section
    st.markdown("### ⚙️ ADMIN")
    
    # Brand Settings
    st.markdown("**Brand**")
    st.markdown('<div class="knowledge-base">Lato & Bebas Neue • Deep/Mid/Light blues, Tint, Canvas</div>', unsafe_allow_html=True)

# Main Content Area
st.markdown('<div class="main-header"><h1>💬 Strategy Labs Assistant</h1></div>', unsafe_allow_html=True)

# Model and Temperature Controls
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    model = st.selectbox(
        "🧠 Model", 
        ["GPT-4.1", "GPT-4", "Claude-3.5-Sonnet", "Claude-3-Opus"],
        help="Select AI model"
    )

with col2:
    temperature = st.slider(
        "🌡️ Temperature", 
        min_value=0.0, 
        max_value=2.0, 
        value=0.7, 
        step=0.1,
        help="Control randomness (0=focused, 2=creative)"
    )

with col3:
    st.markdown("**KBs active: 2**")

# System Prompt
system_prompt = st.text_area(
    "System Prompt:",
    value="You are Strategy Labs' helpful internal assistant. Be concise, cite sources, and follow brand voice.",
    height=100,
    help="Define the AI's behavior and personality"
)

# API Key Input
openai_api_key = st.text_input("🔑 OpenAI API Key", type="password")

if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Create OpenAI client
    client = OpenAI(api_key=openai_api_key)

    # Initialize chat messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display existing messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # File upload section
    uploaded_file = st.file_uploader(
        "📎 Attach files to enhance answers via RAG", 
        type=['pdf', 'txt', 'docx', 'csv'],
        help="Upload documents to provide context"
    )

    if uploaded_file:
        st.success(f"File uploaded: {uploaded_file.name}")

    # Chat input
    if prompt := st.chat_input("Ask about campaigns, dashboards, SOPs..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Prepare messages with system prompt
        messages_for_api = [{"role": "system", "content": system_prompt}]
        messages_for_api.extend([
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ])

        # Generate AI response
        with st.chat_message("assistant"):
            try:
                # Convert model name to API format
                api_model = "gpt-4" if "GPT-4" in model else "gpt-3.5-turbo"
                
                stream = client.chat.completions.create(
                    model=api_model,
                    messages=messages_for_api,
                    temperature=temperature,
                    stream=True,
                )
                
                response = st.write_stream(stream)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Please check your API key and try again.")

# Footer
st.markdown("---")
st.markdown("**Built for Strategy Labs** • This UI mirrors OpenWebUI patterns with SL brand treatment. [Docs](https://docs.example.com)")

