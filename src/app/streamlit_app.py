"""
Streamlit Web Application for Swiss History RAG
Interactive interface for querying Swiss history using RAG.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from datetime import datetime

from src.retrieval.rag_chain import SwissHistoryRAG
from src.utils import load_config


# Page configuration
st.set_page_config(
    page_title="Swiss History RAG",
    page_icon="🇨🇭",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #DC143C;
        text-align: center;
        margin-bottom: 2rem;
    }
    .question-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .answer-box {
        background-color: #e8f4f8;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 5px solid #DC143C;
    }
    .source-box {
        background-color: #f9f9f9;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 3px solid #666;
    }
    .stButton>button {
        background-color: #DC143C;
        color: white;
        border-radius: 0.5rem;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_rag_system():
    """Load RAG system (cached)."""
    with st.spinner("🔄 Loading RAG system..."):
        config = load_config()
        rag = SwissHistoryRAG(config)
    return rag


def display_source(doc, index):
    """Display a source document."""
    page = doc.metadata.get('page_number', 'Unknown')
    chunk_id = doc.metadata.get('chunk_id', 'Unknown')
    
    with st.expander(f"📄 Source {index}: Page {page}"):
        st.markdown(f"**Chunk ID:** {chunk_id}")
        st.markdown(f"**Page:** {page}")
        st.markdown("**Content:**")
        st.text(doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content)


def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<h1 class="main-header">🇨🇭 Swiss History RAG</h1>', unsafe_allow_html=True)
    st.markdown("### Ask questions about Swiss history in German")
    
    # Sidebar
    with st.sidebar:
        st.header("ℹ️ Information")
        st.markdown("""
        This application uses **Retrieval-Augmented Generation (RAG)** to answer questions about Swiss history.
        
        **How it works:**
        1. Enter your question in German
        2. The system searches the historical text
        3. AI generates an answer based on the context
        
        **Features:**
        - 🔍 Semantic search through Swiss history
        - 🤖 AI-powered answers with GPT-4o-mini
        - 📚 Source citations with page numbers
        - 🇩🇪 German language support
        """)
        
        st.divider()
        
        st.header("📖 Source Book")
        st.markdown("""
        **Illustrierte Schweizer Geschichte für Sekundar- und Mittelschulen**
        
        - **Author:** Troxler, Joseph
        - **Published:** Einsiedeln, 1925
        - **Collection:** Stiftung Pestalozzianum
        - **Shelf Mark:** SH 772
        - **Link:** [e-rara.ch](https://doi.org/10.3931/e-rara-95069)
        """)
        
        st.divider()
        
        st.header("⚙️ Settings")
        
        # Number of sources to retrieve
        num_sources = st.slider(
            "Number of sources",
            min_value=1,
            max_value=10,
            value=5,
            help="How many text chunks to retrieve"
        )
        
        # Show sources toggle
        show_sources = st.checkbox(
            "Show sources",
            value=True,
            help="Display the source documents used for the answer"
        )
        
        st.divider()
        
        # Sample questions
        st.header("💡 Sample Questions")
        sample_questions = [
            "Wann wurde die Schweiz gegründet?",
            "Wer war Wilhelm Tell?",
            "Was ist die Eidgenossenschaft?",
            "Welche Rolle spielte die Schweiz im Zweiten Weltkrieg?",
            "Was war der Sonderbundskrieg?",
            "Wann wurde die Bundesverfassung verabschiedet?"
        ]
        
        for q in sample_questions:
            if st.button(q, key=f"sample_{q}", use_container_width=True):
                st.session_state.current_question = q
                st.rerun()
    
    # Initialize session state
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    if 'current_question' not in st.session_state:
        st.session_state.current_question = ""
    
    if 'rag' not in st.session_state:
        try:
            st.session_state.rag = load_rag_system()
            st.success("✅ RAG system loaded successfully!")
        except Exception as e:
            st.error(f"❌ Error loading RAG system: {e}")
            st.stop()
    
    # Question input
    st.markdown("### 💬 Ask your question")
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_question = st.text_input(
            "Enter your question in German:",
            value=st.session_state.current_question,
            placeholder="z.B. Wann wurde die Schweiz gegründet?",
            label_visibility="collapsed",
            key="question_input"
        )
        
        # Update session state with current input
        if user_question != st.session_state.current_question:
            st.session_state.current_question = user_question
    
    with col2:
        submit = st.button("🔍 Search", use_container_width=True)
    
    # Process question
    if submit and user_question:
        with st.spinner("🤔 Thinking..."):
            try:
                # Update retriever k value
                st.session_state.rag.vectorstore._collection
                
                # Query RAG
                result = st.session_state.rag.query(
                    user_question,
                    return_sources=True,
                    k=num_sources
                )
                
                # Add to history
                st.session_state.history.insert(0, {
                    'timestamp': datetime.now(),
                    'question': user_question,
                    'answer': result['answer'],
                    'sources': result['sources']
                })
                
                # Clear the input field after successful query
                st.session_state.current_question = ""
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {e}")
                import traceback
                st.code(traceback.format_exc())
    
    # Display results
    if st.session_state.history:
        st.divider()
        
        # Latest result
        latest = st.session_state.history[0]
        
        st.markdown("### 📝 Answer")
        
        # Question
        st.markdown('<div class="question-box">', unsafe_allow_html=True)
        st.markdown(f"**Question:** {latest['question']}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Answer
        st.markdown('<div class="answer-box">', unsafe_allow_html=True)
        st.markdown(latest['answer'])
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Sources
        if show_sources and latest['sources']:
            st.markdown("### 📚 Sources")
            st.caption(f"Retrieved {len(latest['sources'])} relevant chunks")
            
            for i, doc in enumerate(latest['sources'], 1):
                display_source(doc, i)
        
        # History
        if len(st.session_state.history) > 1:
            st.divider()
            st.markdown("### 📜 Previous Questions")
            
            for i, item in enumerate(st.session_state.history[1:6], 1):  # Show last 5
                with st.expander(f"{i}. {item['question'][:60]}..."):
                    st.markdown(f"**Timestamp:** {item['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                    st.markdown(f"**Question:** {item['question']}")
                    st.markdown(f"**Answer:** {item['answer']}")
            
            if st.button("🗑️ Clear History"):
                st.session_state.history = []
                st.rerun()
    
    else:
        # Welcome message
        st.info("👆 Enter a question above or select a sample question from the sidebar to get started!")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>🇨🇭 Swiss History RAG System | Built with LangChain, ChromaDB, and OpenAI</p>
        <p><strong>Source:</strong> Illustrierte Schweizer Geschichte für Sekundar- und Mittelschulen (Troxler, 1925)</p>
        <p><a href="https://doi.org/10.3931/e-rara-95069" target="_blank">View original book on e-rara.ch</a></p>
        <p>ZHAW LLM Project 2025</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
