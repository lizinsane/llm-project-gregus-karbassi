"""
Vector Store module for Swiss History RAG Project
Manages ChromaDB for storing and retrieving document embeddings.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from src.utils import load_config, get_project_root
from src.retrieval.embeddings import get_embeddings


class VectorStore:
    """Manage vector database for document retrieval."""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize vector store.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or load_config()
        self.project_root = get_project_root()
        
        # Get vector store configuration
        vs_config = self.config.get('vector_store', {})
        self.collection_name = vs_config.get('collection_name', 'swiss_history')
        
        # Setup persist directory
        persist_dir = vs_config.get('persist_directory', './data/chroma_db')
        self.persist_directory = str(self.project_root / persist_dir.lstrip('./'))
        
        # Create directory if it doesn't exist
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize embeddings
        self.embeddings = get_embeddings(self.config)
        
        # Initialize ChromaDB
        self.vectorstore = None
        
    def load_chunks_from_file(self, filename: str = "chunks.json") -> List[Document]:
        """
        Load chunks from JSON file and convert to LangChain Documents.
        
        Args:
            filename: Name of chunks file
            
        Returns:
            List of Document objects
        """
        chunks_path = self.project_root / "data" / "processed" / filename
        
        if not chunks_path.exists():
            raise FileNotFoundError(f"Chunks file not found: {chunks_path}")
        
        print(f"📖 Loading chunks from: {filename}")
        
        with open(chunks_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        chunks = data['chunks']
        print(f"   Found {len(chunks)} chunks")
        
        # Convert to LangChain Documents
        documents = []
        for chunk in chunks:
            doc = Document(
                page_content=chunk['text'],
                metadata={
                    'chunk_id': chunk['chunk_id'],
                    'page_number': chunk['page_number'],
                    'chunk_index': chunk['chunk_index'],
                    'char_count': chunk['char_count'],
                    'word_count': chunk['word_count'],
                }
            )
            documents.append(doc)
        
        return documents
    
    def create_vectorstore(self, documents: List[Document]) -> Chroma:
        """
        Create vector store from documents.
        
        Args:
            documents: List of Document objects
            
        Returns:
            Chroma vector store
        """
        print(f"\n🔨 Creating vector store...")
        print(f"   Collection: {self.collection_name}")
        print(f"   Persist directory: {self.persist_directory}")
        print(f"   Documents: {len(documents)}")
        
        # Create ChromaDB vector store
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            collection_name=self.collection_name,
            persist_directory=self.persist_directory
        )
        
        print(f"✅ Vector store created successfully")
        
        self.vectorstore = vectorstore
        return vectorstore
    
    def load_vectorstore(self) -> Chroma:
        """
        Load existing vector store from disk.
        
        Returns:
            Chroma vector store
        """
        print(f"\n📂 Loading existing vector store...")
        print(f"   Collection: {self.collection_name}")
        print(f"   Persist directory: {self.persist_directory}")
        
        vectorstore = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )
        
        # Check if collection has data
        collection = vectorstore._collection
        count = collection.count()
        
        if count == 0:
            raise ValueError("Vector store is empty. Please create it first.")
        
        print(f"✅ Vector store loaded successfully")
        print(f"   Documents in store: {count}")
        
        self.vectorstore = vectorstore
        return vectorstore
    
    def search(self, query: str, k: int = 5) -> List[Document]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of relevant documents
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized. Call create_vectorstore or load_vectorstore first.")
        
        results = self.vectorstore.similarity_search(query, k=k)
        return results
    
    def search_with_scores(self, query: str, k: int = 5) -> List[tuple]:
        """
        Search for similar documents with similarity scores.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of (document, score) tuples
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized.")
        
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        return results


def main():
    """Main entry point for vector store creation."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Create and manage vector store for Swiss History RAG"
    )
    
    parser.add_argument(
        '--create',
        action='store_true',
        help='Create new vector store from chunks'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test vector store with sample queries'
    )
    
    parser.add_argument(
        '--chunks-file',
        type=str,
        default='chunks.json',
        help='Chunks file to use (default: chunks.json)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🇨🇭 Swiss History RAG - Vector Store")
    print("=" * 60)
    print()
    
    try:
        # Initialize vector store
        vs = VectorStore()
        
        if args.create:
            # Load chunks
            documents = vs.load_chunks_from_file(args.chunks_file)
            
            # Create vector store
            vs.create_vectorstore(documents)
            
            print("\n✅ Vector store created successfully!")
            print(f"   Location: {vs.persist_directory}")
            print(f"   Collection: {vs.collection_name}")
            
        else:
            # Load existing vector store
            vs.load_vectorstore()
        
        if args.test:
            print("\n" + "=" * 60)
            print("🔍 Testing vector store with sample queries")
            print("=" * 60)
            print()
            
            test_queries = [
                "Wann wurde die Schweiz gegründet?",
                "Wer war Wilhelm Tell?",
                "Was ist die Eidgenossenschaft?"
            ]
            
            for query in test_queries:
                print(f"\nQuery: {query}")
                print("-" * 60)
                
                results = vs.search_with_scores(query, k=3)
                
                for i, (doc, score) in enumerate(results, 1):
                    print(f"\n  Result {i} (score: {score:.4f}):")
                    print(f"  Page: {doc.metadata['page_number']}")
                    print(f"  Text: {doc.page_content[:200]}...")
            
            print("\n✅ Test complete!")
        
        print("\n" + "=" * 60)
        print("Next steps:")
        if args.create:
            print("  Test: python src/retrieval/vector_store.py --test")
        print("  Build RAG chain: Coming in next step!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
