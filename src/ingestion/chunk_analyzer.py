"""
Chunk Analyzer for Swiss History RAG Project
Analyzes chunk quality and provides statistics to help tune parameters.
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Optional
import argparse
from collections import Counter

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils import get_project_root


class ChunkAnalyzer:
    """Analyze chunks and provide quality metrics."""
    
    def __init__(self):
        """Initialize chunk analyzer."""
        self.project_root = get_project_root()
    
    def load_chunks(self, filename: str = "test_chunks.json") -> Dict:
        """
        Load chunks from JSON file.
        
        Args:
            filename: Name of chunks file to load
            
        Returns:
            Dictionary with chunks data
        """
        input_path = self.project_root / "data" / "processed" / filename
        
        if not input_path.exists():
            # Try without 'test_' prefix
            alt_filename = filename.replace("test_", "")
            input_path = self.project_root / "data" / "processed" / alt_filename
            
            if not input_path.exists():
                raise FileNotFoundError(
                    f"Chunks file not found. Please run chunker.py first.\n"
                    f"Looking for: {filename} or {alt_filename}"
                )
        
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data
    
    def analyze_size_distribution(self, chunks: List[Dict]) -> Dict:
        """
        Analyze the distribution of chunk sizes.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            Statistics dictionary
        """
        sizes = [c['char_count'] for c in chunks]
        
        if not sizes:
            return {}
        
        sizes_sorted = sorted(sizes)
        n = len(sizes_sorted)
        
        return {
            'min': min(sizes),
            'max': max(sizes),
            'mean': sum(sizes) / n,
            'median': sizes_sorted[n // 2],
            'q1': sizes_sorted[n // 4],
            'q3': sizes_sorted[3 * n // 4],
        }
    
    def analyze_page_distribution(self, chunks: List[Dict]) -> Dict:
        """
        Analyze how chunks are distributed across pages.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            Page distribution statistics
        """
        page_counts = Counter(c['page_number'] for c in chunks)
        chunks_per_page = list(page_counts.values())
        
        return {
            'total_pages': len(page_counts),
            'chunks_per_page_min': min(chunks_per_page) if chunks_per_page else 0,
            'chunks_per_page_max': max(chunks_per_page) if chunks_per_page else 0,
            'chunks_per_page_avg': sum(chunks_per_page) / len(chunks_per_page) if chunks_per_page else 0,
            'page_distribution': dict(page_counts)
        }
    
    def get_sample_chunks(self, chunks: List[Dict], num_samples: int = 3) -> List[Dict]:
        """
        Get sample chunks for review.
        
        Args:
            chunks: List of chunk dictionaries
            num_samples: Number of samples to return
            
        Returns:
            List of sample chunks
        """
        if not chunks:
            return []
        
        # Get chunks from different parts of the document
        indices = [
            0,  # First chunk
            len(chunks) // 2,  # Middle chunk
            len(chunks) - 1,  # Last chunk
        ]
        
        # Add random chunks if we want more samples
        import random
        if num_samples > 3:
            additional = random.sample(range(len(chunks)), min(num_samples - 3, len(chunks) - 3))
            indices.extend(additional)
        
        return [chunks[i] for i in indices[:num_samples]]
    
    def print_analysis(self, data: Dict):
        """
        Print comprehensive analysis of chunks.
        
        Args:
            data: Dictionary with chunks and metadata
        """
        metadata = data['metadata']
        chunks = data['chunks']
        
        print("=" * 70)
        print("📊 CHUNK ANALYSIS REPORT")
        print("=" * 70)
        print()
        
        # Overall statistics
        print("📈 Overall Statistics:")
        print(f"   Total chunks: {metadata['total_chunks']}")
        print(f"   Total pages: {metadata['pages_processed']}")
        print(f"   Total words: {metadata['total_words']:,}")
        print(f"   Total characters: {metadata['total_chars']:,}")
        print(f"   Average chunk size: {metadata['avg_chunk_size']:.0f} chars")
        print()
        
        # Configuration
        print("⚙️  Configuration Used:")
        print(f"   Chunk size: {metadata['chunk_size_config']} chars")
        print(f"   Chunk overlap: {metadata['chunk_overlap_config']} chars")
        print()
        
        # Size distribution
        size_stats = self.analyze_size_distribution(chunks)
        print("📏 Chunk Size Distribution:")
        print(f"   Minimum: {size_stats['min']} chars")
        print(f"   Q1 (25%): {size_stats['q1']:.0f} chars")
        print(f"   Median: {size_stats['median']:.0f} chars")
        print(f"   Q3 (75%): {size_stats['q3']:.0f} chars")
        print(f"   Maximum: {size_stats['max']} chars")
        print(f"   Mean: {size_stats['mean']:.0f} chars")
        print()
        
        # Page distribution
        page_stats = self.analyze_page_distribution(chunks)
        print("📄 Page Distribution:")
        print(f"   Chunks per page (min): {page_stats['chunks_per_page_min']}")
        print(f"   Chunks per page (avg): {page_stats['chunks_per_page_avg']:.1f}")
        print(f"   Chunks per page (max): {page_stats['chunks_per_page_max']}")
        print()
        
        # Show distribution by page
        print("📋 Chunks by Page:")
        for page_num in sorted(page_stats['page_distribution'].keys())[:10]:
            count = page_stats['page_distribution'][page_num]
            print(f"   Page {page_num:2d}: {count} chunk{'s' if count != 1 else ''}")
        if len(page_stats['page_distribution']) > 10:
            print(f"   ... and {len(page_stats['page_distribution']) - 10} more pages")
        print()
        
        # Quality assessment
        print("✅ Quality Assessment:")
        
        # Check if chunks are too small or too large
        if size_stats['mean'] < 300:
            print("   ⚠️  Chunks are quite small - consider increasing chunk_size")
        elif size_stats['mean'] > 2000:
            print("   ⚠️  Chunks are quite large - consider decreasing chunk_size")
        else:
            print("   ✓ Chunk sizes look good")
        
        # Check distribution
        size_range = size_stats['max'] - size_stats['min']
        if size_range > metadata['chunk_size_config'] * 1.5:
            print("   ⚠️  Wide variation in chunk sizes - might want to adjust parameters")
        else:
            print("   ✓ Chunk sizes are relatively consistent")
        
        # Check overlap effectiveness
        overlap_ratio = metadata['chunk_overlap_config'] / metadata['chunk_size_config']
        if overlap_ratio < 0.1:
            print("   ⚠️  Overlap is quite small - consider increasing for better context")
        elif overlap_ratio > 0.3:
            print("   ⚠️  Overlap is quite large - might create redundancy")
        else:
            print("   ✓ Overlap ratio looks good")
        
        print()
        
        # Sample chunks
        print("=" * 70)
        print("📝 SAMPLE CHUNKS")
        print("=" * 70)
        print()
        
        samples = self.get_sample_chunks(chunks, num_samples=3)
        
        for i, chunk in enumerate(samples, 1):
            print(f"Sample {i}: Chunk #{chunk['chunk_id']} (Page {chunk['page_number']})")
            print(f"Size: {chunk['char_count']} chars, {chunk['word_count']} words")
            print("-" * 70)
            
            # Show first 400 characters of the chunk
            preview = chunk['text'][:400]
            if len(chunk['text']) > 400:
                preview += "..."
            
            print(preview)
            print()
            print("=" * 70)
            print()
    
    def save_report(self, data: Dict, output_filename: str = "chunk_analysis.txt"):
        """
        Save analysis report to a text file.
        
        Args:
            data: Dictionary with chunks and metadata
            output_filename: Name of output file
        """
        output_dir = self.project_root / "data" / "processed"
        output_path = output_dir / output_filename
        
        # Redirect print to file
        import io
        import contextlib
        
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            self.print_analysis(data)
        
        report_text = f.getvalue()
        
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(report_text)
        
        print(f"💾 Analysis report saved to: {output_path}")
        
        return output_path


def main():
    """Main entry point for chunk analysis."""
    
    parser = argparse.ArgumentParser(
        description="Analyze chunks from Swiss History PDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze test chunks (first 10 pages)
  python chunk_analyzer.py --test
  
  # Analyze full chunks
  python chunk_analyzer.py --full
  
  # Save report to file
  python chunk_analyzer.py --test --save
        """
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Analyze test chunks (first 10 pages)'
    )
    
    parser.add_argument(
        '--full',
        action='store_true',
        help='Analyze full chunks'
    )
    
    parser.add_argument(
        '--save',
        action='store_true',
        help='Save analysis report to file'
    )
    
    parser.add_argument(
        '--input',
        type=str,
        help='Input chunks file (default: auto-detect)'
    )
    
    args = parser.parse_args()
    
    # Determine input file
    if args.input:
        input_file = args.input
        mode = "CUSTOM"
    elif args.test:
        input_file = "test_chunks.json"
        mode = "TEST (10 pages)"
    elif args.full:
        input_file = "chunks.json"
        mode = "FULL (all pages)"
    else:
        # Default to test mode
        input_file = "test_chunks.json"
        mode = "TEST (10 pages) - default"
    
    print()
    print("=" * 70)
    print("🇨🇭 Swiss History RAG - Chunk Analysis")
    print("=" * 70)
    print(f"Mode: {mode}")
    print(f"Input: {input_file}")
    print("=" * 70)
    print()
    
    try:
        # Initialize analyzer
        analyzer = ChunkAnalyzer()
        
        # Load chunks
        print(f"📖 Loading chunks from: {input_file}")
        data = analyzer.load_chunks(input_file)
        print(f"✅ Loaded {len(data['chunks'])} chunks")
        print()
        
        # Print analysis
        analyzer.print_analysis(data)
        
        # Save report if requested
        if args.save:
            output_file = "test_chunk_analysis.txt" if args.test else "chunk_analysis.txt"
            analyzer.save_report(data, output_file)
            print()
        
        print("=" * 70)
        print("✅ Analysis complete!")
        print("=" * 70)
        print()
        print("💡 Next steps:")
        print("1. Review the sample chunks above")
        print("2. If chunks look good, proceed to process full PDF")
        print("3. If not, adjust parameters in config/config.yaml:")
        print("   - chunk_size: Make chunks larger/smaller")
        print("   - chunk_overlap: Adjust context preservation")
        print("4. Re-run: python src/ingestion/chunker.py --test")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
