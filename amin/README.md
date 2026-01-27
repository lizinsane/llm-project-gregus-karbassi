# 🇨🇭 Swiss History RAG Chatbot

A Retrieval-Augmented Generation (RAG) system for querying Swiss historical information from "Illustrierte Schweizer Geschichte für Sekundar- und Mittelschulen" (Troxler, 1925).

## 📚 Project Overview

This project implements a conversational AI system that allows users to ask questions about Swiss history in German. The system uses:
- **RAG Architecture**: Combines document retrieval with LLM generation
- **LangChain Framework**: For building the RAG pipeline
- **PyPDF & Docling**: For PDF text extraction with structure preservation
- **ChromaDB**: Vector database for semantic search
- **HuggingFace Embeddings**: Multilingual semantic embeddings
- **OpenAI GPT-4o-mini**: For question answering
- **Streamlit**: Interactive web interface
- **RAGAS**: Automated RAG evaluation framework

## 🏗️ Architecture

```
User Question → Embedding → Vector Search → Context Retrieval → LLM → Answer + Citations
```

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Navigate to project directory
cd swiss-history-rag

# Create virtual environment
python3.13 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install streamlit langchain-community langchain-openai chromadb sentence-transformers pypdf python-dotenv pyyaml tqdm ragas
```

### 2. Configure Environment

Create a `.env` file in the project root:

```bash
nano .env
```

Add your OpenAI API key:
```
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

**Get your API key:** https://platform.openai.com/api-keys

### 3. Add Your PDF

Place the PDF file in `data/raw/`:
```bash
# The file should be named: Illustrierte_Schweizer_Geschichte.pdf
# Located at: data/raw/Illustrierte_Schweizer_Geschichte.pdf
```

## 📝 Usage Instructions

### Phase 1: PDF Extraction

Extract text from the PDF:

```bash
# Extract all pages (starting from page 12)
python src/ingestion/pdf_processor.py --full --start-page 12

# Extract specific page range for testing
python src/ingestion/pdf_processor.py --start-page 12 --end-page 20
```

**Output:** Extracted text saved to `data/processed/extracted_text.json`

### Phase 2: Text Chunking

Split the extracted text into chunks:

```bash
# Create chunks from extracted text
python src/ingestion/chunker.py --full

# Analyze chunk quality
python src/ingestion/chunk_analyzer.py
```

**Output:** Chunks saved to `data/processed/chunks.json`

### Phase 3: Vector Store Creation

Create embeddings and vector database:

```bash
# Create vector store (one-time setup)
python src/retrieval/vector_store.py --create

# Test vector store with sample queries
python src/retrieval/vector_store.py --test
```

**Output:** Vector database saved to `data/chroma_db/`

### Phase 4: RAG System Testing

Test the RAG chain:

```bash
# Run with test questions
python src/retrieval/rag_chain.py --test

# Ask a single question
python src/retrieval/rag_chain.py --question "Wann wurde die Schweiz gegründet?"

# Interactive mode
python src/retrieval/rag_chain.py
```

### Phase 5: Streamlit Web Application

Launch the interactive web interface:

```bash
streamlit run src/app/streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

**Features:**
- 🇩🇪 German language interface
- 📚 Source citations with page numbers
- 💬 Sample questions in sidebar
- 🔍 Adjustable retrieval settings
- 📜 Query history

### Phase 6: Evaluation with RAGAS

Evaluate RAG system performance:

```bash
# Run automated evaluation with test questions
python src/evaluation/ragas_eval.py

# Use custom test questions
python src/evaluation/ragas_eval.py --test-file custom_questions.json

# Specify output filename
python src/evaluation/ragas_eval.py --output my_results.csv
```

**Metrics:**
- **Faithfulness**: Does the answer align with retrieved context?
- **Answer Relevancy**: Does the answer address the question?
- **Context Precision**: Are retrieved contexts relevant?
- **Context Recall**: Are all relevant contexts retrieved?

**Output:** Results saved to `data/evaluation/ragas_evaluation_*.csv`

## 🔧 Configuration

Edit `config/config.yaml` to customize:

```yaml
# Embedding model
embeddings:
  model_name: "intfloat/multilingual-e5-small"
  model_type: "huggingface"

# LLM settings
llm:
  model_name: "gpt-4o-mini"
  temperature: 0.3

# Chunking parameters
chunking:
  chunk_size: 1000
  chunk_overlap: 200

# Retrieval settings
retrieval:
  top_k: 5
```

## 📊 Example Queries

- "Wann wurde die Schweiz gegründet?"
- "Wer war Wilhelm Tell?"
- "Was war die Schlacht am Morgarten?"
- "Welche Orte gehörten zum Bund der acht alten Orte?"
- "Was war der Sonderbundskrieg?"
- "Wann trat die erste Bundesverfassung in Kraft?"

## 📖 Source Document

**Title:** Illustrierte Schweizer Geschichte für Sekundar- und Mittelschulen  
**Author:** Troxler, Joseph  
**Published:** Einsiedeln, 1925  
**Pages:** 274  
**Collection:** Stiftung Pestalozzianum  
**Shelf Mark:** SH 772  
**Link:** [e-rara.ch](https://doi.org/10.3931/e-rara-95069)

## 🔍 Troubleshooting

### Import Errors
```bash
# Reinstall dependencies
pip install --upgrade streamlit langchain-community langchain-openai chromadb sentence-transformers
```

### Vector Store Not Found
```bash
# Recreate vector store
rm -rf data/chroma_db/
python src/retrieval/vector_store.py --create
```

### Deprecation Warnings
Warnings about `HuggingFaceEmbeddings` or `Chroma` are harmless and can be ignored. The system works correctly.

## 🧪 Project Phases

1. ✅ **Phase 1:** Project setup & structure
2. ✅ **Phase 2:** PDF extraction & chunking
3. ✅ **Phase 3:** Embeddings & vector store
4. ✅ **Phase 4:** RAG chain implementation
5. ✅ **Phase 5:** Streamlit web interface
6. ✅ **Phase 6:** RAGAS evaluation framework

## 🤝 Contributors

ZHAW LLM Project 2025

## 📄 License

This project is for educational purposes as part of the ZHAW LLM course.

---

**Note:** Make sure to keep your `.env` file private and never commit it to version control. It's already included in `.gitignore`.
