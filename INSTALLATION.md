# Phase 2 Files - Installation Instructions

## 📦 What's in This Package

This package contains **ONLY the new Phase 2 files** so you don't overwrite your existing Phase 1 setup.

### New Files Included:
1. **pdf_processor.py** - Extracts text from PDF
2. **chunker.py** - Splits text into chunks  
3. **chunk_analyzer.py** - Analyzes chunk quality
4. **test_phase2.sh** - Automated test script
5. **run_phase2_full.sh** - Full processing script
6. **PHASE2_GUIDE.md** - Detailed instructions
7. **PHASE2_WORKFLOW.md** - Visual workflow diagrams

---

## 🚀 How to Install (3 Steps)

### Step 1: Navigate to Your Project
```bash
cd path/to/your/swiss-history-rag
```

### Step 2: Copy the Python Files
```bash
# Copy to the ingestion directory
cp pdf_processor.py src/ingestion/
cp chunker.py src/ingestion/
cp chunk_analyzer.py src/ingestion/
```

### Step 3: Copy the Scripts & Documentation
```bash
# Copy scripts to project root
cp test_phase2.sh .
cp run_phase2_full.sh .

# Make scripts executable (Linux/Mac)
chmod +x test_phase2.sh
chmod +x run_phase2_full.sh

# Copy documentation
cp PHASE2_GUIDE.md .
cp PHASE2_WORKFLOW.md .
```

---

## ✅ Verification

Check that files are in the right place:

```bash
# Should show the 3 new Python files
ls -la src/ingestion/

# Should show the 2 new scripts
ls -la test_phase2.sh run_phase2_full.sh

# Should show the 2 new docs
ls -la PHASE2_*.md
```

Expected structure:
```
your-project/
├── src/
│   └── ingestion/
│       ├── __init__.py (existing)
│       ├── pdf_processor.py (NEW ✨)
│       ├── chunker.py (NEW ✨)
│       └── chunk_analyzer.py (NEW ✨)
├── test_phase2.sh (NEW ✨)
├── run_phase2_full.sh (NEW ✨)
├── PHASE2_GUIDE.md (NEW ✨)
├── PHASE2_WORKFLOW.md (NEW ✨)
└── [all your existing files from Phase 1]
```

---

## 🎯 Quick Start After Installation

```bash
# 1. Place your PDF in data/raw/
cp /path/to/Illustrierte_Schweizer_Geschichte.pdf data/raw/

# 2. Run the test (first 10 pages)
./test_phase2.sh

# 3. Review the results, then run full processing
./run_phase2_full.sh
```

---

## 📝 One More Thing: Update requirements.txt

Add this line to your `requirements.txt` if not already there:

```
langchain-text-splitters==0.0.1
```

Then reinstall:
```bash
pip install -r requirements.txt
```

---

## 🆘 Need Help?

If you have issues:
1. Check PHASE2_GUIDE.md for detailed instructions
2. Make sure you're in your virtual environment
3. Verify your PDF is in data/raw/
4. Check that all files copied correctly

---

## ✨ That's It!

Your Phase 1 files are **completely safe**. These new files just add Phase 2 functionality to your existing project.

Ready to go? Run:
```bash
./test_phase2.sh
```
