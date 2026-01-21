"""
PDF Processor for Swiss History RAG Project
Extracts text from PDF with support for test mode (first 10 pages) and full mode.
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Optional
import argparse
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from docling.document_converter import DocumentConverter
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False
    print("⚠️  Docling not available, falling back to PyPDF")

import pypdf
from tqdm import tqdm

from src.utils import load_config, get_project_root
from src.ingestion.text_cleaner import clean_german_text


class PDFProcessor:
    """Process PDF files and extract text with metadata."""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize PDF processor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or load_config()
        self.project_root = get_project_root()
        
    def find_pdf_files(self) -> List[Path]:
        """
        Find all PDF files in data/raw directory.
        
        Returns:
            List of PDF file paths
        """
        raw_dir = self.project_root / "data" / "raw"
        pdf_files = list(raw_dir.glob("*.pdf"))
        
        if not pdf_files:
            raise FileNotFoundError(
                f"No PDF files found in {raw_dir}. "
                f"Please place your Swiss history PDF in data/raw/"
            )
        
        return pdf_files
    
    def extract_text_pypdf(self, pdf_path: Path, start_page: int = 1, end_page: Optional[int] = None) -> List[Dict]:
        """
        Extract text using PyPDF (fallback method).
        
        Args:
            pdf_path: Path to PDF file
            start_page: Starting page number (1-indexed, default: 1)
            end_page: Ending page number (1-indexed, None for all pages)
            
        Returns:
            List of dictionaries with page text and metadata
        """
        print(f"📄 Using PyPDF to extract text from: {pdf_path.name}")
        
        pages_data = []
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            
            # Validate and adjust page numbers (convert to 0-indexed)
            start_idx = max(0, start_page - 1)
            end_idx = min(end_page, total_pages) if end_page else total_pages
            
            # Ensure start is before end
            if start_idx >= end_idx:
                raise ValueError(f"Invalid page range: start_page ({start_page}) must be less than end_page ({end_page})")
            
            pages_to_process = end_idx - start_idx
            
            print(f"📊 Total pages in PDF: {total_pages}")
            print(f"📖 Processing pages: {start_page} to {end_idx} ({pages_to_process} pages)")
            
            for page_idx in tqdm(range(start_idx, end_idx), desc="Extracting pages"):
                try:
                    page = pdf_reader.pages[page_idx]
                    text = page.extract_text()
                    
                    # Clean up text - fix excessive newlines and formatting issues
                    text = clean_german_text(text) if text else ""
                    text = text.strip()
                    
                    if text:  # Only include pages with text
                        pages_data.append({
                            'page_number': page_idx + 1,
                            'text': text,
                            'char_count': len(text),
                            'word_count': len(text.split()),
                        })
                    else:
                        print(f"⚠️  Page {page_idx + 1} has no extractable text")
                        
                except Exception as e:
                    print(f"❌ Error extracting page {page_idx + 1}: {e}")
                    
        return pages_data
    
    def extract_text_docling(self, pdf_path: Path, start_page: int = 1, end_page: Optional[int] = None) -> List[Dict]:
        """
        Extract text using Docling (preferred method for complex documents).
        
        Args:
            pdf_path: Path to PDF file
            start_page: Starting page number (1-indexed, default: 1)
            end_page: Ending page number (1-indexed, None for all pages)
            
        Returns:
            List of dictionaries with page text and metadata
        """
        print(f"📄 Using Docling to extract text from: {pdf_path.name}")
        print("⏳ This may take a few minutes for complex documents...")
        
        try:
            converter = DocumentConverter()
            result = converter.convert(str(pdf_path))
            
            pages_data = []
            doc = result.document
            
            # Get total pages
            total_pages = len(doc.pages) if hasattr(doc, 'pages') else 0
            
            # Validate and adjust page numbers (convert to 0-indexed)
            start_idx = max(0, start_page - 1)
            end_idx = min(end_page, total_pages) if end_page else total_pages
            
            # Ensure start is before end
            if start_idx >= end_idx:
                raise ValueError(f"Invalid page range: start_page ({start_page}) must be less than end_page ({end_page})")
            
            pages_to_process = end_idx - start_idx
            
            print(f"📊 Total pages in PDF: {total_pages}")
            print(f"📖 Processing pages: {start_page} to {end_idx} ({pages_to_process} pages)")
            
            # Process pages
            for page_idx in tqdm(range(start_idx, end_idx), desc="Extracting pages"):
                page = doc.pages[page_idx]
                
                # Extract text from page
                page_text = page.export_to_text() if hasattr(page, 'export_to_text') else str(page)
                
                # Clean the text
                page_text = clean_german_text(page_text) if page_text else ""
                
                if page_text.strip():
                    pages_data.append({
                        'page_number': page_idx + 1,
                        'text': page_text.strip(),
                        'char_count': len(page_text),
                        'word_count': len(page_text.split()),
                    })
            
            return pages_data
            
        except Exception as e:
            print(f"❌ Docling error: {e}")
            print("⚠️  Falling back to PyPDF...")
            return self.extract_text_pypdf(pdf_path, start_page, end_page)
    
    def extract_text(self, pdf_path: Optional[Path] = None, 
                    start_page: int = 1,
                    end_page: Optional[int] = None,
                    use_docling: bool = True) -> List[Dict]:
        """
        Extract text from PDF file.
        
        Args:
            pdf_path: Path to PDF file (if None, searches data/raw/)
            start_page: Starting page number (1-indexed, default: 1)
            end_page: Ending page number (1-indexed, None for all pages)
            use_docling: Whether to try Docling first
            
        Returns:
            List of dictionaries with page text and metadata
        """
        # Find PDF if not specified
        if pdf_path is None:
            pdf_files = self.find_pdf_files()
            pdf_path = pdf_files[0]
            if len(pdf_files) > 1:
                print(f"⚠️  Multiple PDFs found, using: {pdf_path.name}")
        
        # Choose extraction method
        if use_docling and DOCLING_AVAILABLE:
            pages_data = self.extract_text_docling(pdf_path, start_page, end_page)
        else:
            if use_docling and not DOCLING_AVAILABLE:
                print("⚠️  Docling not installed, using PyPDF")
            pages_data = self.extract_text_pypdf(pdf_path, start_page, end_page)
        
        return pages_data
    
    def save_extracted_text(self, pages_data: List[Dict], 
                           output_filename: str = "extracted_text.json"):
        """
        Save extracted text to JSON file.
        
        Args:
            pages_data: List of page data dictionaries
            output_filename: Name of output file
        """
        output_dir = self.project_root / "data" / "processed"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / output_filename
        
        # Add metadata
        output_data = {
            'metadata': {
                'extraction_date': datetime.now().isoformat(),
                'total_pages': len(pages_data),
                'total_chars': sum(p['char_count'] for p in pages_data),
                'total_words': sum(p['word_count'] for p in pages_data),
            },
            'pages': pages_data
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Saved extracted text to: {output_path}")
        print(f"📊 Statistics:")
        print(f"   - Pages: {output_data['metadata']['total_pages']}")
        print(f"   - Words: {output_data['metadata']['total_words']:,}")
        print(f"   - Characters: {output_data['metadata']['total_chars']:,}")
        
        return output_path


def main():
    """Main entry point for PDF processing."""
    
    parser = argparse.ArgumentParser(
        description="Extract text from Swiss History PDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test mode - process first 10 pages only
  python pdf_processor.py --test
  
  # Test mode starting from page 5 (skip empty cover pages)
  python pdf_processor.py --test --start-page 5
  
  # Custom page range (e.g., pages 5-25)
  python pdf_processor.py --start-page 5 --end-page 25
  
  # Full mode - process all pages
  python pdf_processor.py --full
  
  # Full mode starting from page 5
  python pdf_processor.py --full --start-page 5
  
  # Use PyPDF instead of Docling
  python pdf_processor.py --test --no-docling
        """
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test mode: process 10 pages (use --start-page to skip cover pages)'
    )
    
    parser.add_argument(
        '--full',
        action='store_true',
        help='Full mode: process all pages'
    )
    
    parser.add_argument(
        '--start-page',
        type=int,
        default=1,
        help='Starting page number (1-indexed, default: 1)'
    )
    
    parser.add_argument(
        '--end-page',
        type=int,
        help='Ending page number (1-indexed, processes to end if not specified)'
    )
    
    parser.add_argument(
        '--no-docling',
        action='store_true',
        help='Use PyPDF instead of Docling'
    )
    
    parser.add_argument(
        '--pdf',
        type=str,
        help='Path to specific PDF file (optional)'
    )
    
    args = parser.parse_args()
    
    # Determine page range to process
    start_page = args.start_page
    
    if args.end_page:
        # Explicit end page specified
        end_page = args.end_page
        mode = f"Pages {start_page}-{end_page}"
    elif args.test:
        # Test mode: 10 pages starting from start_page
        end_page = start_page + 9
        mode = f"TEST (pages {start_page}-{end_page})"
    elif args.full:
        # Full mode: all pages from start_page to end
        end_page = None
        mode = f"FULL (from page {start_page} to end)" if start_page > 1 else "FULL (all pages)"
    else:
        # Default to test mode
        end_page = start_page + 9
        mode = f"TEST (pages {start_page}-{end_page}) - default"
        print(f"ℹ️  No mode specified, defaulting to test mode")
        print(f"   Processing pages {start_page}-{end_page}")
        print("   Use --full to process all pages\n")
    
    print("=" * 60)
    print("🇨🇭 Swiss History RAG - PDF Text Extraction")
    print("=" * 60)
    print(f"Mode: {mode}")
    print(f"Extraction method: {'Docling' if not args.no_docling else 'PyPDF'}")
    print("=" * 60)
    print()
    
    try:
        # Initialize processor
        processor = PDFProcessor()
        
        # Extract text
        pdf_path = Path(args.pdf) if args.pdf else None
        pages_data = processor.extract_text(
            pdf_path=pdf_path,
            start_page=start_page,
            end_page=end_page,
            use_docling=not args.no_docling
        )
        
        # Save results
        if args.test or (end_page and end_page - start_page <= 20):
            output_filename = "test_extracted_text.json"
        else:
            output_filename = "extracted_text.json"
        
        processor.save_extracted_text(pages_data, output_filename)
        
        print("\n" + "=" * 60)
        print("✅ Text extraction complete!")
        print("=" * 60)
        
        if args.test or (end_page and end_page - start_page <= 20):
            print("\n📋 Next steps:")
            print("1. Review the extracted text: data/processed/test_extracted_text.json")
            print("2. Create chunks: python src/ingestion/chunker.py --test")
            print("3. Analyze chunks: python src/ingestion/chunk_analyzer.py --test")
            print("4. If satisfied, run: python src/ingestion/pdf_processor.py --full")
            if start_page > 1:
                print(f"   (Full mode will also start from page {start_page})")
        else:
            print("\n📋 Next step:")
            print("   Create chunks: python src/ingestion/chunker.py --full")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
