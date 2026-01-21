# Phase 2: PDF Processing & Chunking - Quick Start

## 🎯 Goal
Extract text from your Swiss history PDF and split it into optimized chunks for RAG.

## 📋 Two-Step Workflow

### Step 1: Test with First 10 Pages (30 minutes)
Extract and chunk first 10 pages to test your setup and parameters.

### Step 2: Full Processing (1-2 hours)
Process all 274 pages after confirming everything works well.

---

## 🚀 Step-by-Step Instructions

### Prerequisites ✅
```bash
# Make sure you're in the project directory
cd swiss-history-rag

# Activate your virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Verify PDF is in place
ls data/raw/*.pdf
```

---

## STEP 1: Test with First 10 Pages

### 1.1 Extract Text from First 10 Pages

```bash
python src/ingestion/pdf_processor.py --test
```

**What it does:**
- Extracts text from pages 1-10 only
- Tries Docling first (best quality)
- Falls back to PyPDF if Docling fails
- Saves to: `data/processed/test_extracted_text.json`

**Expected output:**
```
📄 Using Docling to extract text from: your_pdf.pdf
📊 Total pages in PDF: 274
📖 Processing pages: 10
Extracting pages: 100% ████████ 10/10
✅ Saved extracted text to: data/processed/test_extracted_text.json
```

**Troubleshooting:**
- If Docling fails, try: `python src/ingestion/pdf_processor.py --test --no-docling`
- If PDF not found: Copy your PDF to `data/raw/` directory

### 1.2 Create Chunks

```bash
python src/ingestion/chunker.py --test
```

**What it does:**
- Splits extracted text into chunks
- Uses parameters from `config/config.yaml`:
  - chunk_size: 1000 characters
  - chunk_overlap: 200 characters
- Saves to: `data/processed/test_chunks.json`

**Expected output:**
```
🔪 Chunking with parameters:
   - Chunk size: 1000 characters
   - Overlap: 200 characters
   - Min chunk size: 100 characters

✅ Saved 47 chunks to: data/processed/test_chunks.json

📊 Chunk Statistics:
   - Total chunks: 47
   - Total words: 8,234
   - Average chunk size: 892 chars
```

### 1.3 Analyze Chunk Quality

```bash
python src/ingestion/chunk_analyzer.py --test
```

**What it does:**
- Analyzes chunk size distribution
- Shows chunks per page
- Displays 3 sample chunks
- Provides quality recommendations

**What to look for:**
- ✅ **Good**: Average chunk size 800-1200 chars
- ✅ **Good**: Chunks are relatively consistent in size
- ✅ **Good**: Sample chunks contain complete thoughts/sentences
- ⚠️ **Bad**: Chunks are too small (<500 chars) or too large (>1500 chars)
- ⚠️ **Bad**: Chunks cut off mid-sentence
- ⚠️ **Bad**: Wide variation in sizes

**Example output:**
```
📊 CHUNK ANALYSIS REPORT
========================

📈 Overall Statistics:
   Total chunks: 47
   Total pages: 10
   Average chunk size: 892 chars

📏 Chunk Size Distribution:
   Minimum: 456 chars
   Median: 901 chars
   Maximum: 1243 chars

✅ Quality Assessment:
   ✓ Chunk sizes look good
   ✓ Chunk sizes are relatively consistent
   ✓ Overlap ratio looks good

📝 SAMPLE CHUNKS
================

Sample 1: Chunk #0 (Page 1)
Size: 943 chars, 156 words
----------------------------------------------------------------------
Die Geschichte der Schweiz beginnt mit der Gründung...
[Preview of chunk text]
```

---

## 🎨 Adjusting Parameters (If Needed)

If the chunks don't look good, edit `config/config.yaml`:

```yaml
pdf_processing:
  chunk_size: 1000      # Increase if chunks too small, decrease if too large
  chunk_overlap: 200    # Increase for more context, decrease for less redundancy
  min_chunk_size: 100   # Minimum size to keep a chunk
```

**Common adjustments:**

| Issue | Solution |
|-------|----------|
| Chunks too small | Increase `chunk_size` to 1500 |
| Chunks too large | Decrease `chunk_size` to 800 |
| Poor context | Increase `chunk_overlap` to 300 |
| Too much redundancy | Decrease `chunk_overlap` to 100 |
| Chunks cut mid-sentence | Adjust both size and overlap |

**After adjusting, re-run:**
```bash
python src/ingestion/chunker.py --test
python src/ingestion/chunk_analyzer.py --test
```

---

## STEP 2: Process All 274 Pages

Once you're satisfied with the test results:

### 2.1 Extract All Pages

```bash
python src/ingestion/pdf_processor.py --full
```

**Time estimate:** 5-15 minutes depending on PDF complexity

**Output:** `data/processed/extracted_text.json`

### 2.2 Create All Chunks

```bash
python src/ingestion/chunker.py --full
```

**Time estimate:** 1-2 minutes

**Output:** `data/processed/chunks.json`

**Expected results:**
- ~1,200-1,500 chunks (depends on your settings)
- ~200,000-300,000 words
- Ready for Phase 3!

### 2.3 Analyze Full Results (Optional)

```bash
python src/ingestion/chunk_analyzer.py --full --save
```

This saves a full analysis report to `data/processed/chunk_analysis.txt`

---

## 📊 Expected File Sizes

| File | Test (10 pages) | Full (274 pages) |
|------|-----------------|------------------|
| extracted_text.json | ~50-100 KB | ~1-2 MB |
| chunks.json | ~80-150 KB | ~2-4 MB |
| chunk_analysis.txt | ~5 KB | ~10 KB |

---

## 🔍 Verifying Your Results

### Check the files exist:
```bash
ls -lh data/processed/
```

You should see:
```
test_extracted_text.json    # Test extraction
test_chunks.json           # Test chunks
extracted_text.json        # Full extraction (after --full)
chunks.json               # Full chunks (after --full)
```

### Quick check of chunk quality:
```bash
# View first chunk
python -c "import json; data=json.load(open('data/processed/test_chunks.json')); print(data['chunks'][0]['text'][:500])"
```

---

## ⚠️ Common Issues & Solutions

### Issue: "No PDF files found"
**Solution:**
```bash
# Copy your PDF to the right location
cp /path/to/your/Illustrierte_Schweizer_Geschichte.pdf data/raw/
```

### Issue: "Docling extraction fails"
**Solution:**
```bash
# Use PyPDF instead
python src/ingestion/pdf_processor.py --test --no-docling
```

### Issue: "ImportError: No module named 'docling'"
**Solution:**
```bash
# Install missing dependencies
pip install docling
# or use PyPDF
python src/ingestion/pdf_processor.py --test --no-docling
```

### Issue: "Chunks are too small/large"
**Solution:**
Edit `config/config.yaml` and adjust `chunk_size`, then re-run chunker

### Issue: "Text extraction looks corrupted"
**Solution:**
- Try with `--no-docling` flag to use PyPDF
- Or manually check if PDF is text-based (not scanned images)

---

## 🎯 Success Criteria

Before moving to Phase 3, verify:

- ✅ Extracted text is readable German
- ✅ Chunks are 800-1200 characters on average
- ✅ Sample chunks contain complete thoughts
- ✅ No major text corruption or encoding issues
- ✅ Page numbers are correctly tracked
- ✅ Full processing completed successfully

---

## 📈 What's Next?

Once Phase 2 is complete:

1. ✅ Your text is extracted and chunked
2. ✅ Chunks are saved with metadata (page numbers)
3. ✅ Ready for Phase 3: RAG Pipeline

**Next command:**
```
"Let's start Phase 3!"
```

And I'll help you build:
- Embedding generation
- Vector store setup with ChromaDB
- RAG chain with LangChain
- Query system with citations

---

## 💾 Backup Tip

Before running full processing, backup your test results:
```bash
cp data/processed/test_chunks.json data/processed/test_chunks_backup.json
```

---

## 🕐 Time Investment

| Task | Time |
|------|------|
| Step 1.1: Extract test pages | 2-5 min |
| Step 1.2: Chunk test pages | 1 min |
| Step 1.3: Analyze chunks | 1 min |
| Adjust parameters (if needed) | 5-15 min |
| Step 2.1: Extract all pages | 5-15 min |
| Step 2.2: Chunk all pages | 1-2 min |
| **Total** | **15-40 min** |

---

**Ready?** Start with:
```bash
python src/ingestion/pdf_processor.py --test
```

Good luck! 🚀
