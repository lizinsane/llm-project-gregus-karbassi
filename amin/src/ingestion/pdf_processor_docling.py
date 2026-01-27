from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from pathlib import Path
import sys
import pypdf

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils import get_project_root
from src.ingestion.text_cleaner import clean_german_text

# Path to PDF file - reads from data/raw directory
project_root = get_project_root()
pdf_path = project_root / "data" / "raw" / "Illustrierte_Schweizer_Geschichte.pdf"

# Output path - saves to data/processed directory
output_path = project_root / "data" / "processed" / "extracted_content_geschichtsbuch.md"

# Create processed directory if it doesn't exist
output_path.parent.mkdir(parents=True, exist_ok=True)

print(f"📄 Processing: {pdf_path.name}")
print(f"💾 Output: {output_path}")
print("=" * 60)

# OPTION 1: Use PyPDF for simple text extraction (fastest, no OCR issues)
print("⏳ Extracting text with PyPDF (starting from page 12)...")

START_PAGE = 12  # Start from page 12
END_PAGE = None  # None = process all pages, or set a number like 50 for testing

extracted_text = []

with open(pdf_path, 'rb') as file:
    pdf_reader = pypdf.PdfReader(file)
    total_pages = len(pdf_reader.pages)
    
    # Calculate page range
    start_idx = START_PAGE - 1  # Convert to 0-indexed
    end_idx = END_PAGE if END_PAGE else total_pages
    
    print(f"📊 Total pages in PDF: {total_pages}")
    print(f"📖 Processing pages: {START_PAGE} to {end_idx}")
    print()
    
    for page_num in range(start_idx, end_idx):
        try:
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            
            if text.strip():
                # Clean the text to remove excessive line breaks
                cleaned_text = clean_german_text(text)
                extracted_text.append(f"## Page {page_num + 1}\n\n{cleaned_text}\n\n")
                print(f"✓ Extracted page {page_num + 1}")
            else:
                print(f"⚠️  Page {page_num + 1} is empty")
                
        except Exception as e:
            print(f"❌ Error on page {page_num + 1}: {e}")

# Combine all text
markdown_text = "\n".join(extracted_text)

print("\n✅ Extraction successful!")
print(f"📊 Extracted {len(extracted_text)} pages")
print("\n📄 Sample of extracted text:")
print("=" * 60)
print(markdown_text[:500] + "..." if len(markdown_text) > 500 else markdown_text)
print("=" * 60)

# Save as Markdown file
with open(output_path, "w", encoding="utf-8") as f:
    f.write(markdown_text)

print(f"\n✅ Text has been saved to '{output_path}'")
print("\n" + "=" * 60)
print("🎉 Extraction completed successfully!")
print("=" * 60)
