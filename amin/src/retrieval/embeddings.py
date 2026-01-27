"""
Embeddings module for Swiss History RAG Project
Handles embedding generation for chunks using multilingual models.
"""

import sys
from pathlib import Path
from typing import Dict, Optional

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from langchain_community.embeddings import HuggingFaceEmbeddings
from src.utils import load_config


def get_embeddings(config: Optional[Dict] = None, model_name: Optional[str] = None):
    """
    Get embeddings model for text vectorization.
    
    Args:
        config: Configuration dictionary
        model_name: Override model name from config
        
    Returns:
        Embeddings model instance
    """
    if config is None:
        config = load_config()
    
    # Get embedding configuration
    embedding_config = config.get('embeddings', {})
    
    # Determine which model to use
    if model_name is None:
        model_name = embedding_config.get(
            'model_name',
            'sentence-transformers/paraphrase-multilingual-mpnet-base-v2'
        )
    
    model_type = embedding_config.get('model_type', 'huggingface')
    
    print(f"🔤 Initializing embeddings model: {model_name}")
    print(f"   Type: {model_type}")
    
    if model_type == 'huggingface':
        # Use HuggingFace sentence transformers (supports German)
        embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},  # Use 'cuda' if GPU available
            encode_kwargs={'normalize_embeddings': True}
        )
        
        print(f"✅ Embeddings model loaded successfully")
        return embeddings
    
    elif model_type == 'openai':
        # Use OpenAI embeddings (requires API key)
        try:
            from langchain_openai import OpenAIEmbeddings
            from src.utils import get_env_variable
            
            api_key = get_env_variable('OPENAI_API_KEY')
            embeddings = OpenAIEmbeddings(
                model='text-embedding-3-small',
                openai_api_key=api_key
            )
            
            print(f"✅ OpenAI embeddings loaded successfully")
            return embeddings
            
        except Exception as e:
            print(f"❌ Error loading OpenAI embeddings: {e}")
            print("   Falling back to HuggingFace...")
            
            embeddings = HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            return embeddings
    
    else:
        raise ValueError(f"Unknown embedding model type: {model_type}")


if __name__ == "__main__":
    # Test embeddings
    print("Testing embeddings...")
    
    embeddings = get_embeddings()
    
    # Test with German text
    test_texts = [
        "Die Schweiz ist ein Land in Europa.",
        "Wilhelm Tell ist eine legendäre Figur der Schweizer Geschichte.",
        "Die Eidgenossenschaft wurde 1291 gegründet."
    ]
    
    print("\n📝 Testing with sample German texts...")
    for text in test_texts:
        embedding = embeddings.embed_query(text)
        print(f"   '{text[:50]}...'")
        print(f"   Embedding dimension: {len(embedding)}")
    
    print("\n✅ Embeddings test complete!")
