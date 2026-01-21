# PDF Processor - Custom Page Range Feature

## 🎯 New Feature: Start Page Selection

You can now specify which page to start from, perfect for skipping empty cover pages!

---

## 📖 Usage Examples

### Basic Examples

#### 1. Test mode starting from page 1 (default)
```bash
python src/ingestion/pdf_processor.py --test
# Processes pages 1-10
```

#### 2. Test mode starting from page 5 (skip cover pages!)
```bash
python src/ingestion/pdf_processor.py --test --start-page 5
# Processes pages 5-14
```

#### 3. Test mode starting from page 10
```bash
python src/ingestion/pdf_processor.py --test --start-page 10
# Processes pages 10-19
```

### Custom Page Ranges

#### 4. Specific page range (e.g., pages 5-25)
```bash
python src/ingestion/pdf_processor.py --start-page 5 --end-page 25
# Processes pages 5-25 (21 pages total)
```

#### 5. Extract pages 10-50
```bash
python src/ingestion/pdf_processor.py --start-page 10 --end-page 50
# Processes pages 10-50 (41 pages total)
```

### Full Processing

#### 6. Process all pages (from page 1 to end)
```bash
python src/ingestion/pdf_processor.py --full
# Processes all pages starting from page 1
```

#### 7. Process all pages starting from page 5
```bash
python src/ingestion/pdf_processor.py --full --start-page 5
# Processes pages 5 to end (skips pages 1-4)
```

---

## 🔍 How to Find Your Starting Page

### Method 1: Quick Preview
```bash
# Extract first 20 pages to check
python src/ingestion/pdf_processor.py --start-page 1 --end-page 20

# Review the output
cat data/processed/test_extracted_text.json | less
```

Look through the JSON to see which page has actual content.

### Method 2: Check Individual Pages
```python
# Quick Python script to check pages
import pypdf

with open('data/raw/your_pdf.pdf', 'rb') as f:
    reader = pypdf.PdfReader(f)
    for i in range(min(10, len(reader.pages))):
        text = reader.pages[i].extract_text()
        print(f"\n=== PAGE {i+1} ===")
        print(text[:200] if text else "[EMPTY]")
```

### Method 3: Visual Inspection
Open your PDF in a viewer and note the page number where content starts.

---

## 💡 Recommended Workflow

### Step 1: Find Your Starting Page
```bash
# Extract first 15 pages to check
python src/ingestion/pdf_processor.py --start-page 1 --end-page 15
```

Check the output and note where actual content begins (let's say page 5).

### Step 2: Test with Correct Start Page
```bash
# Now test with the correct starting page
python src/ingestion/pdf_processor.py --test --start-page 5
```

This will extract pages 5-14 for testing.

### Step 3: Process Full Document
```bash
# When satisfied, process all pages starting from page 5
python src/ingestion/pdf_processor.py --full --start-page 5
```

---

## 📊 Common Scenarios

### Scenario 1: PDF with Cover Pages
```
Pages 1-4: Cover, title page, empty pages
Page 5: Table of contents
Page 6: Actual content starts

Solution:
python src/ingestion/pdf_processor.py --test --start-page 6
```

### Scenario 2: Book with Preface
```
Pages 1-10: Cover, preface, foreword
Page 11: Chapter 1 starts

Solution:
python src/ingestion/pdf_processor.py --test --start-page 11
```

### Scenario 3: Extract Only Specific Chapters
```
Chapter 3: Pages 50-75
Want to test just this chapter

Solution:
python src/ingestion/pdf_processor.py --start-page 50 --end-page 75
```

---

## ⚙️ All Available Options

```bash
python src/ingestion/pdf_processor.py [OPTIONS]

Options:
  --test              Process 10 pages (default: pages 1-10)
  --full              Process all pages
  --start-page N      Start from page N (default: 1)
  --end-page N        End at page N (default: last page)
  --no-docling        Use PyPDF instead of Docling
  --pdf PATH          Path to specific PDF file
```

---

## 🎯 Quick Reference Table

| What You Want | Command |
|---------------|---------|
| Test pages 1-10 | `--test` |
| Test pages 5-14 | `--test --start-page 5` |
| Pages 10-50 | `--start-page 10 --end-page 50` |
| All pages from 1 | `--full` |
| All pages from 5 | `--full --start-page 5` |
| Pages 20-30 | `--start-page 20 --end-page 30` |

---

## 🔧 Updating Your Test Script

If you're using `test_phase2.sh`, you can modify it to use a custom start page:

```bash
# Edit test_phase2.sh
# Change this line:
python src/ingestion/pdf_processor.py --test

# To this (to start from page 5):
python src/ingestion/pdf_processor.py --test --start-page 5
```

---

## ✅ Verification

After running with a custom start page, check the output:

```bash
# View the extracted pages
python -c "
import json
with open('data/processed/test_extracted_text.json') as f:
    data = json.load(f)
    pages = [p['page_number'] for p in data['pages']]
    print(f'Extracted pages: {min(pages)} to {max(pages)}')
    print(f'Total: {len(pages)} pages')
"
```

---

## 🆘 Troubleshooting

### Error: "Invalid page range"
- Make sure start-page < end-page
- Make sure start-page >= 1
- Check that end-page doesn't exceed PDF total pages

### Error: "No text extracted"
- The pages might be images (scanned PDF)
- Try a different page range
- Use `--no-docling` flag to try PyPDF

### Pages seem wrong
- Remember: page numbers are 1-indexed (first page is 1, not 0)
- Check the page numbers in the PDF viewer match what you're specifying

---

## 📝 Example Session

```bash
# Check what's in the PDF
python src/ingestion/pdf_processor.py --start-page 1 --end-page 10

# Found content starts at page 7
# Now test with correct range
python src/ingestion/pdf_processor.py --test --start-page 7

# Looks good! Process the rest
python src/ingestion/pdf_processor.py --full --start-page 7

# Continue with chunking
python src/ingestion/chunker.py --full
```

---

**Ready to use it?** 🚀

Try this to skip cover pages:
```bash
python src/ingestion/pdf_processor.py --test --start-page 5
```
