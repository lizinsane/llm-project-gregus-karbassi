#!/bin/bash

# Swiss History RAG - Phase 2 Complete Test Script
# This script runs all Phase 2 steps in sequence

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Swiss History RAG - Phase 2 Complete Test             ║"
echo "║     Test with first 10 pages before full processing       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not activated!"
    echo "Please run: source venv/bin/activate"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if PDF exists
PDF_COUNT=$(find data/raw -name "*.pdf" 2>/dev/null | wc -l)
if [ "$PDF_COUNT" -eq 0 ]; then
    echo "❌ No PDF files found in data/raw/"
    echo ""
    echo "Please place your Swiss history PDF in data/raw/"
    echo "Example:"
    echo "  cp /path/to/your/Illustrierte_Schweizer_Geschichte.pdf data/raw/"
    echo ""
    exit 1
fi

echo "✅ Found PDF file in data/raw/"
echo ""

# Step 1: Extract text from first 10 pages
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1/3: Extracting text from first 10 pages"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python src/ingestion/pdf_processor.py --test --no-docling

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ PDF extraction failed!"
    echo "Try running with PyPDF: python src/ingestion/pdf_processor.py --test --no-docling"
    exit 1
fi

echo ""
echo "✅ Step 1 complete: Text extracted"
echo ""
sleep 2

# Step 2: Create chunks
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2/3: Creating chunks from extracted text"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python src/ingestion/chunker.py --test

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Chunking failed!"
    exit 1
fi

echo ""
echo "✅ Step 2 complete: Chunks created"
echo ""
sleep 2

# Step 3: Analyze chunks
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3/3: Analyzing chunk quality"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python src/ingestion/chunk_analyzer.py --test --save

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Analysis failed!"
    exit 1
fi

echo ""
echo "✅ Step 3 complete: Analysis done"
echo ""

# Final summary
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    TEST COMPLETE! ✅                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Results saved to:"
echo "   • data/processed/test_extracted_text.json"
echo "   • data/processed/test_chunks.json"
echo "   • data/processed/test_chunk_analysis.txt"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. REVIEW the analysis report above"
echo "   → Are chunks the right size?"
echo "   → Do sample chunks look good?"
echo ""
echo "2. If adjustments needed:"
echo "   → Edit config/config.yaml"
echo "   → Change chunk_size and/or chunk_overlap"
echo "   → Re-run this script: ./test_phase2.sh"
echo ""
echo "3. If everything looks good:"
echo "   → Process full PDF: ./run_phase2_full.sh"
echo "   → Or manually: python src/ingestion/pdf_processor.py --full"
echo "                  python src/ingestion/chunker.py --full"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
