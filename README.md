# 🇨🇭 Swiss History RAG Chatbot

A Retrieval-Augmented Generation (RAG) system for querying Swiss historical information from "Illustrierte Schweizer Geschichte für Sekundar- und Mittelschulen" (274 pages).

## 📚 Project Overview

This project implements a conversational AI system that allows users to ask questions about Swiss history in German. The system uses:
- **RAG Architecture**: Combines document retrieval with LLM generation
- **LangChain Framework**: For building the RAG pipeline
- **Docling**: For PDF text extraction with structure preservation
- **ChromaDB**: Vector database for semantic search
- **Streamlit**: Interactive web interface

## 🏗️ Architecture

```
User Question → Embedding → Vector Search → Context Retrieval → LLM → Answer + Citations
```

## 📁 Project Structure

```
swiss-history-rag/
├── data/
│   ├── raw/                 # Place your PDF here
│   ├── processed/           # Processed chunks (auto-generated)
│   └── chroma_db/           # Vector database (auto-generated)
├── src/
│   ├── ingestion/          # PDF processing & chunking
│   │   ├── __init__.py
│   │   ├── pdf_processor.py
│   │   └── chunker.py
│   ├── retrieval/          # RAG pipeline
│   │   ├── __init__.py
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   └── rag_chain.py
│   └── web/                # Streamlit application
│       ├── __init__.py
│       └── app.py
├── notebooks/              # Jupyter notebooks for experimentation
├── tests/                  # Unit tests
├── config/                 # Configuration files
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository (or download the project folder)
cd swiss-history-rag

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

**Required API Keys:**
- OpenAI API key (get from https://platform.openai.com/)
- OR Anthropic API key (get from https://console.anthropic.com/)

### 3. Add Your PDF

Place your PDF file in the `data/raw/` directory:
```bash
cp /path/to/your/Illustrierte_Schweizer_Geschichte.pdf data/raw/
```

### 4. Process the PDF (Phase 2)

```bash
python src/ingestion/pdf_processor.py
```

### 5. Run the Web Application (Phase 4)

```bash
streamlit run src/web/app.py
```

## 🔧 Configuration Options

Edit `.env` file to customize:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `LLM_MODEL` | Language model to use | `gpt-4o-mini` |
| `EMBEDDING_MODEL` | Embedding type | `huggingface` |
| `CHUNK_SIZE` | Text chunk size (tokens) | `1000` |
| `CHUNK_OVERLAP` | Overlap between chunks | `200` |
| `TOP_K_RESULTS` | Number of results to retrieve | `5` |

## 📊 Features

- ✅ Conversational interface in German
- ✅ Source citations with page numbers
- ✅ Timeline visualization of Swiss history
- ✅ Query statistics dashboard
- ✅ Multi-language support (DE/EN/FR)
- ✅ Export chat history
- ✅ Dark/light mode

## 🧪 Testing

Run tests:
```bash
pytest tests/
```

