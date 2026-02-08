"""
Streamlit Web App for Pidgin AI Tutor
Professional interface for the chatbot with user feedback collection
"""

import streamlit as st
import sys
from pathlib import Path
import json
from datetime import datetime
import os

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from chatbot import PidginChatbot, RuleBasedFallback

# Page config
st.set_page_config(
    page_title="Pidgin AI Tutor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        animation: fadeIn 0.5s;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 2rem;
        border-left: 4px solid #5568d3;
    }
    .bot-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        margin-right: 2rem;
        border-left: 4px solid #d84a5f;
    }
    .stats-box {
        background: linear-gradient(135deg, #FA8BFF 0%, #2BD2FF 90%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .feature-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E7D32;
        margin-bottom: 0.5rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'chatbot' not in st.session_state:
    try:
        st.session_state.chatbot = PidginChatbot("models/fine_tuned_pidgin")
        st.session_state.model_loaded = True
    except Exception as e:
        st.session_state.model_loaded = False
        st.session_state.error_message = str(e)

if 'feedback' not in st.session_state:
    st.session_state.feedback = []

if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

if 'total_questions' not in st.session_state:
    st.session_state.total_questions = 0


def save_feedback(message, response, rating, comment=""):
    """Save user feedback for visa documentation"""
    os.makedirs("data", exist_ok=True)
    
    feedback_entry = {
        'timestamp': datetime.now().isoformat(),
        'user_name': st.session_state.user_name if st.session_state.user_name else "Anonymous",
        'message': message,
        'response': response,
        'rating': rating,
        'comment': comment
    }
    st.session_state.feedback.append(feedback_entry)
    
    # Save to file
    try:
        with open('data/user_feedback.json', 'w', encoding='utf-8') as f:
            json.dump(st.session_state.feedback, f, indent=2, ensure_ascii=False)
    except Exception as e:
        st.error(f"Could not save feedback: {e}")


def main():
    # Header
    st.markdown('<h1 class="main-header">🎓 Pidgin AI Tutor</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Learn Mathematics and Coding in Nigerian Pidgin English</p>', 
                unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 👋 Welcome!")
        
        # User name input
        if not st.session_state.user_name:
            name = st.text_input("Wetin be your name?", placeholder="Enter your name")
            if name:
                st.session_state.user_name = name
                st.rerun()
        else:
            st.success(f"Hello, {st.session_state.user_name}! 👋")
            if st.button("Change Name"):
                st.session_state.user_name = ""
                st.rerun()
        
        st.markdown("---")
        
        # Topic selection
        st.markdown("### 📚 Wetin you wan learn?")
        topic = st.radio(
            "Choose topic:",
            ["General Chat", "Mathematics", "Coding (Python)"],
            help="Pick the subject wey you wan learn"
        )
        
        st.markdown("---")
        
        # Statistics
        st.markdown("### 📊 Your Progress")
        st.markdown(f"""
        <div class="stats-box">
            <strong>💬 Messages:</strong> {len(st.session_state.messages)}<br>
            <strong>📚 Current Topic:</strong> {topic}<br>
            <strong>⭐ Feedback Given:</strong> {len(st.session_state.feedback)}<br>
            <strong>❓ Questions Asked:</strong> {st.session_state.total_questions}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick examples
        st.markdown("### 💡 Try These Questions")
        example_questions = {
            "General Chat": [
                "Hello, how you dey?",
                "Wetin you fit do?",
                "I wan learn something new"
            ],
            "Mathematics": [
                "Wetin be algebra?",
                "How I go add 25 + 47?",
                "Teach me about fractions",
                "Calculate 12 × 8",
                "Wetin be percentage?"
            ],
            "Coding (Python)": [
                "Wetin be programming?",
                "How I go start learn Python?",
                "Show me how to write if statement",
                "Wetin be variable?",
                "How I go write function?"
            ]
        }
        
        for question in example_questions.get(topic, []):
            if st.button(question, key=f"example_{question}"):
                st.session_state.current_input = question
                st.rerun()
        
        st.markdown("---")
        
        # Features info
        st.markdown("### ✨ Features")
        st.markdown("""
        <div class="feature-box">
            ✅ Learn in Pidgin English<br>
            ✅ Math & Coding lessons<br>
            ✅ Free forever<br>
            ✅ 24/7 availability
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            if 'chatbot' in st.session_state:
                st.session_state.chatbot.clear_history()
            st.rerun()
        
        # Download conversation
        if st.session_state.messages:
            conversation_json = json.dumps(st.session_state.messages, indent=2, ensure_ascii=False)
            st.download_button(
                "📥 Download Chat",
                conversation_json,
                file_name=f"pidgin_tutor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; font-size: 0.8rem; color: #888;">
            Made with ❤️ for Nigerian learners<br>
            🇳🇬 Democratizing Education 🇳🇬
        </div>
        """, unsafe_allow_html=True)
    
    # Main chat area
    if not st.session_state.model_loaded:
        st.info("ℹ️ AI model not loaded. Using smart rule-based responses. For full AI, train the model first!")
        
        with st.expander("📖 How to train the AI model"):
            st.code("""
# Step 1: Install AI packages (takes 10-15 mins)
pip install transformers torch datasets

# Step 2: Train the model (takes 15-30 mins)
python train_model.py

# Step 3: Restart this app
streamlit run streamlit_app.py
            """, language="bash")
    
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>👤 You:</strong><br>{message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message bot-message">
                <strong>🤖 Pidgin AI:</strong><br>{message["content"]}
            </div>
            """, unsafe_allow_html=True)
    
    # Chat input
    user_input = st.chat_input("Ask your question in Pidgin or English...", key="chat_input")
    
    # Handle example button clicks
    if hasattr(st.session_state, 'current_input'):
        user_input = st.session_state.current_input
        delattr(st.session_state, 'current_input')
    
    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.total_questions += 1
        
        # Generate response
        with st.spinner("Thinking... 🤔"):
            try:
                if 'chatbot' in st.session_state:
                    response = st.session_state.chatbot.generate_response(user_input)
                else:
                    fallback = RuleBasedFallback.get_response(user_input)
                    response = fallback if fallback else "I dey learn to answer that question. Try ask me about Math or Python coding!"
                
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                error_response = f"Sorry, I get small problem: {str(e)}. Try ask your question another way."
                st.session_state.messages.append({"role": "assistant", "content": error_response})
        
        st.rerun()
    
    # Feedback section
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
        st.markdown("---")
        st.markdown("### 💬 How was this response?")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("⭐ Excellent", use_container_width=True, key="feedback_excellent"):
                last_user = st.session_state.messages[-2]["content"]
                last_bot = st.session_state.messages[-1]["content"]
                save_feedback(last_user, last_bot, "excellent")
                st.success("Thank you! 🎉")
        
        with col2:
            if st.button("👍 Good", use_container_width=True, key="feedback_good"):
                last_user = st.session_state.messages[-2]["content"]
                last_bot = st.session_state.messages[-1]["content"]
                save_feedback(last_user, last_bot, "good")
                st.success("Thanks for the feedback!")
        
        with col3:
            if st.button("😐 Okay", use_container_width=True, key="feedback_okay"):
                last_user = st.session_state.messages[-2]["content"]
                last_bot = st.session_state.messages[-1]["content"]
                save_feedback(last_user, last_bot, "okay")
                st.info("We'll improve!")
        
        with col4:
            if st.button("👎 Poor", use_container_width=True, key="feedback_poor"):
                last_user = st.session_state.messages[-2]["content"]
                last_bot = st.session_state.messages[-1]["content"]
                save_feedback(last_user, last_bot, "poor")
                st.warning("Sorry! We'll do better.")
        
        # Detailed feedback form
        with st.expander("✍️ Give detailed feedback (optional)"):
            detailed_feedback = st.text_area("Tell us how we can improve:", key="detailed_feedback")
            if st.button("Submit Detailed Feedback"):
                if detailed_feedback:
                    last_user = st.session_state.messages[-2]["content"]
                    last_bot = st.session_state.messages[-1]["content"]
                    save_feedback(last_user, last_bot, "detailed", detailed_feedback)
                    st.success("Thank you for your detailed feedback! 🙏")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 0.9rem;">
        <strong>Pidgin AI Tutor</strong> - Making Education Accessible 🇳🇬<br>
        Built with Python, Streamlit & ❤️<br>
        <a href="https://github.com/yourusername/pidgin-ai-tutor" target="_blank" style="color: #2E7D32;">View on GitHub</a>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()