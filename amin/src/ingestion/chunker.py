"""
Text Chunker for Swiss History RAG Project
Splits extracted text into chunks with overlap and metadata.
"""

import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Optional
import argparse
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.utils import load_config, get_project_root


class TextChunker:
    """Split text into chunks for RAG."""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize text chunker.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or load_config()
        self.project_root = get_project_root()
        
        # Get chunking parameters from config
        pdf_config = self.config.get('pdf_processing', {})
        self.chunk_size = pdf_config.get('chunk_size', 1000)
        self.chunk_overlap = pdf_config.get('chunk_overlap', 200)
        self.min_chunk_size = pdf_config.get('min_chunk_size', 100)
        
    def create_splitter(self) -> RecursiveCharacterTextSplitter:
        """
        Create a text splitter with configured parameters.
        
        Returns:
            RecursiveCharacterTextSplitter instance
        """
        # Separators optimized for German text and book structure
        separators = [
            "\n\n\n",  # Multiple blank lines (chapter/section breaks)
            "\n\n",    # Paragraph breaks
            "\n",      # Line breaks
            ". ",      # Sentence endings
            ", ",      # Clause breaks
            " ",       # Word breaks
            ""         # Character breaks (last resort)
        ]
        
        return RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=separators,
            is_separator_regex=False
        )
    
    def load_markdown_file(self, filename: str = "extracted_content_geschichtsbuch.md") -> List[Dict]:
        """
        Load extracted text from Markdown file and parse into pages.
        
        Args:
            filename: Name of the Markdown file to load
            
        Returns:
            List of page dictionaries with text
        """
        input_path = self.project_root / "data" / "processed" / filename
        
        if not input_path.exists():
            raise FileNotFoundError(
                f"Markdown file not found: {input_path}\n"
                f"Please run the extraction script first."
            )
        
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse markdown into pages using ## Page X headers
        pages_data = []
        
        # Split by page headers (## Page X)
        page_pattern = r'## Page (\d+)\n\n(.*?)(?=## Page \d+|$)'
        matches = re.findall(page_pattern, content, re.DOTALL)
        
        for page_num_str, page_text in matches:
            page_number = int(page_num_str)
            text = page_text.strip()
            
            if text:
                pages_data.append({
                    'page_number': page_number,
                    'text': text,
                    'char_count': len(text),
                    'word_count': len(text.split())
                })
        
        print(f"📖 Parsed {len(pages_data)} pages from Markdown file")
        
        return pages_data
    
    def load_extracted_text(self, filename: str = "test_extracted_text.json") -> Dict:
        """
        Load extracted text from JSON file.
        
        Args:
            filename: Name of the JSON file to load
            
        Returns:
            Dictionary with extracted text data
        """
        input_path = self.project_root / "data" / "processed" / filename
        
        if not input_path.exists():
            # Try without 'test_' prefix
            alt_filename = filename.replace("test_", "")
            input_path = self.project_root / "data" / "processed" / alt_filename
            
            if not input_path.exists():
                raise FileNotFoundError(
                    f"Extracted text not found. Please run pdf_processor.py first.\n"
                    f"Looking for: {filename} or {alt_filename}"
                )
        
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data
    
    def chunk_pages(self, pages_data: List[Dict]) -> List[Dict]:
        """
        Split pages into chunks with metadata.
        
        Args:
            pages_data: List of page dictionaries with text
            
        Returns:
            List of chunk dictionaries
        """
        splitter = self.create_splitter()
        chunks = []
        chunk_id = 0
        
        print(f"🔪 Chunking with parameters:")
        print(f"   - Chunk size: {self.chunk_size} characters")
        print(f"   - Overlap: {self.chunk_overlap} characters")
        print(f"   - Min chunk size: {self.min_chunk_size} characters")
        print()
        
        for page in pages_data:
            page_number = page['page_number']
            page_text = page['text']
            
            # Skip pages with very little text
            if len(page_text) < self.min_chunk_size:
                print(f"⚠️  Skipping page {page_number} (too short: {len(page_text)} chars)")
                continue
            
            # Split page text into chunks
            page_chunks = splitter.split_text(page_text)
            
            # Add metadata to each chunk
            for i, chunk_text in enumerate(page_chunks):
                if len(chunk_text) >= self.min_chunk_size:
                    chunks.append({
                        'chunk_id': chunk_id,
                        'page_number': page_number,
                        'chunk_index': i,
                        'text': chunk_text,
                        'char_count': len(chunk_text),
                        'word_count': len(chunk_text.split()),
                    })
                    chunk_id += 1
        
        return chunks
    
    def save_chunks(self, chunks: List[Dict], 
                   output_filename: str = "chunks.json",
                   metadata: Optional[Dict] = None):
        """
        Save chunks to JSON file.
        
        Args:
            chunks: List of chunk dictionaries
            output_filename: Name of output file
            metadata: Optional metadata dictionary
        """
        output_dir = self.project_root / "data" / "processed"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / output_filename
        
        # Calculate statistics
        total_chars = sum(c['char_count'] for c in chunks)
        total_words = sum(c['word_count'] for c in chunks)
        avg_chunk_size = total_chars / len(chunks) if chunks else 0
        
        # Prepare output data
        output_data = {
            'metadata': {
                'creation_date': datetime.now().isoformat(),
                'total_chunks': len(chunks),
                'total_chars': total_chars,
                'total_words': total_words,
                'avg_chunk_size': round(avg_chunk_size, 2),
                'chunk_size_config': self.chunk_size,
                'chunk_overlap_config': self.chunk_overlap,
                'pages_processed': len(set(c['page_number'] for c in chunks)),
            },
            'chunks': chunks
        }
        
        # Add custom metadata if provided
        if metadata:
            output_data['metadata'].update(metadata)
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Saved {len(chunks)} chunks to: {output_path}")
        print(f"\n📊 Chunk Statistics:")
        print(f"   - Total chunks: {output_data['metadata']['total_chunks']}")
        print(f"   - Total words: {output_data['metadata']['total_words']:,}")
        print(f"   - Total characters: {output_data['metadata']['total_chars']:,}")
        print(f"   - Average chunk size: {output_data['metadata']['avg_chunk_size']:.0f} chars")
        print(f"   - Pages processed: {output_data['metadata']['pages_processed']}")
        
        return output_path


def main():
    """Main entry point for text chunking."""
    
    parser = argparse.ArgumentParser(
        description="Chunk extracted text from Swiss History PDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Chunk from markdown file (default)
  python chunker.py
  
  # Chunk from specific markdown file
  python chunker.py --input extracted_content_geschichtsbuch.md
  
  # Custom chunk parameters
  python chunker.py --chunk-size 1500 --overlap 300
  
  # Use JSON input (legacy mode)
  python chunker.py --json --input extracted_text.json
        """
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Use JSON input instead of Markdown (legacy mode)'
    )
    
    parser.add_argument(
        '--chunk-size',
        type=int,
        help='Override chunk size from config'
    )
    
    parser.add_argument(
        '--overlap',
        type=int,
        help='Override chunk overlap from config'
    )
    
    parser.add_argument(
        '--input',
        type=str,
        help='Input file (default: extracted_content_geschichtsbuch.md)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='chunks.json',
        help='Output JSON file (default: chunks.json)'
    )
    
    args = parser.parse_args()
    
    # Determine input file
    if args.input:
        input_file = args.input
    elif args.json:
        input_file = "extracted_text.json"
    else:
        input_file = "extracted_content_geschichtsbuch.md"
    
    input_type = "JSON" if args.json or input_file.endswith('.json') else "MARKDOWN"
    
    print("=" * 60)
    print("🇨🇭 Swiss History RAG - Text Chunking")
    print("=" * 60)
    print(f"Input type: {input_type}")
    print(f"Input file: {input_file}")
    print(f"Output file: {args.output}")
    print("=" * 60)
    print()
    
    try:
        # Initialize chunker
        chunker = TextChunker()
        
        # Override config if specified
        if args.chunk_size:
            chunker.chunk_size = args.chunk_size
            print(f"⚙️  Override chunk_size: {args.chunk_size}")
        if args.overlap:
            chunker.chunk_overlap = args.overlap
            print(f"⚙️  Override chunk_overlap: {args.overlap}")
        
        print()
        
        # Load extracted text based on input type
        if input_type == "MARKDOWN":
            print(f"📖 Loading Markdown file: {input_file}")
            pages_data = chunker.load_markdown_file(input_file)
            total_words = sum(p['word_count'] for p in pages_data)
        else:
            print(f"📖 Loading JSON file: {input_file}")
            extracted_data = chunker.load_extracted_text(input_file)
            pages_data = extracted_data['pages']
            total_words = extracted_data['metadata']['total_words']
        
        print(f"✅ Loaded {len(pages_data)} pages")
        print(f"   Total words: {total_words:,}")
        print()
        
        # Create chunks
        chunks = chunker.chunk_pages(pages_data)
        
        # Save chunks
        chunker.save_chunks(chunks, args.output)
        
        print("\n" + "=" * 60)
        print("✅ Chunking complete!")
        print("=" * 60)
        
        print("\n📋 Next steps:")
        print("1. Analyze chunks: python src/ingestion/chunk_analyzer.py")
        print("2. Create vector store: python src/retrieval/vector_store.py --create")
        print("3. Test RAG: python src/retrieval/rag_chain.py --test")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
