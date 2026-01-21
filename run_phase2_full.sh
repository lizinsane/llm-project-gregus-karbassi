#!/bin/bash

# Swiss History RAG - Phase 2 Full Processing Script
# Run this AFTER testing with test_phase2.sh

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Swiss History RAG - Phase 2 FULL Processing           ║"
echo "║     Processing all 274 pages                               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Confirmation
echo "⚠️  This will process all 274 pages (may take 5-15 minutes)"
echo ""
read -p "Have you tested with test_phase2.sh first? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Please run test_phase2.sh first to verify your setup!"
    exit 1
fi

echo ""
read -p "Are you satisfied with the test results? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Please adjust config/config.yaml and re-run test_phase2.sh"
    exit 1
fi

echo ""
echo "✅ Starting full processing..."
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not activated!"
    echo "Please run: source venv/bin/activate"
    exit 1
fi

# Step 1: Extract all pages
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1/2: Extracting text from all 274 pages"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⏳ This may take 5-15 minutes depending on PDF complexity..."
echo ""

START_TIME=$(date +%s)

python src/ingestion/pdf_processor.py --full

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ PDF extraction failed!"
    echo "Try running with PyPDF: python src/ingestion/pdf_processor.py --full --no-docling"
    exit 1
fi

EXTRACT_TIME=$(($(date +%s) - START_TIME))
echo ""
echo "✅ Step 1 complete: Full text extracted (${EXTRACT_TIME}s)"
echo ""
sleep 2

# Step 2: Create all chunks
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2/2: Creating chunks from full extracted text"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python src/ingestion/chunker.py --full

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Chunking failed!"
    exit 1
fi

TOTAL_TIME=$(($(date +%s) - START_TIME))
echo ""
echo "✅ Step 2 complete: All chunks created"
echo ""

# Optional: Analyze full results
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Generating analysis report..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python src/ingestion/chunk_analyzer.py --full --save

# Final summary
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              PHASE 2 COMPLETE! 🎉                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "⏱️  Total time: ${TOTAL_TIME} seconds"
echo ""
echo "📊 Results saved to:"
echo "   • data/processed/extracted_text.json"
echo "   • data/processed/chunks.json"
echo "   • data/processed/chunk_analysis.txt"
echo ""
echo "📈 Quick stats:"
CHUNK_COUNT=$(python -c "import json; data=json.load(open('data/processed/chunks.json')); print(data['metadata']['total_chunks'])" 2>/dev/null || echo "N/A")
WORD_COUNT=$(python -c "import json; data=json.load(open('data/processed/chunks.json')); print(data['metadata']['total_words'])" 2>/dev/null || echo "N/A")
echo "   • Total chunks: ${CHUNK_COUNT}"
echo "   • Total words: ${WORD_COUNT}"
echo ""
echo "✅ Your PDF is now processed and ready for Phase 3!"
echo ""
echo "📋 Next step:"
echo "   Tell me: \"Let's start Phase 3!\""
echo "   And I'll help you build the RAG pipeline with:"
echo "   • Embeddings generation"
echo "   • ChromaDB vector store"
echo "   • LangChain RAG chain"
echo "   • Query system with citations"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
