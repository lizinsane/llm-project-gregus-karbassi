"""
RAG Chain for Swiss History RAG Project
Retrieval-Augmented Generation using LangChain, ChromaDB, and OpenAI.
"""
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

from src.utils import load_config, get_env_variable
from src.retrieval.vector_store import VectorStore


class SwissHistoryRAG:
    """RAG system for Swiss History questions."""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize RAG chain.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or load_config()
        
        # Load vector store
        print("📂 Loading vector store...")
        self.vector_store = VectorStore(self.config)
        self.vectorstore = self.vector_store.load_vectorstore()
        
        # Initialize LLM
        print("🤖 Initializing LLM...")
        llm_config = self.config.get('llm', {})
        
        api_key = get_env_variable('OPENAI_API_KEY')
        model_name = llm_config.get('model_name', 'gpt-4o-mini')
        temperature = llm_config.get('temperature', 0.1)
        
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=api_key
        )
        
        print(f"   Model: {model_name}")
        print(f"   Temperature: {temperature}")
        
        # Create RAG chain
        print("🔗 Building RAG chain...")
        self.chain = self._create_chain()
        
        print("✅ RAG system ready!")
    
    def _create_prompt_template(self) -> ChatPromptTemplate:
        """
        Create prompt template for Swiss History RAG.
        
        Returns:
            ChatPromptTemplate for the RAG chain
        """
        template = """Du bist ein Experte für Schweizer Geschichte. Beantworte die folgende Frage basierend auf dem gegebenen Kontext.

Kontext:
{context}

Frage: {question}

Anweisungen:
- Antworte auf Deutsch
- Verwende nur Informationen aus dem gegebenen Kontext
- Wenn die Antwort nicht im Kontext steht, sage: "Diese Information ist im verfügbaren Text nicht vorhanden."
- Sei präzise und sachlich
- Zitiere relevante Details aus dem Kontext

Antwort:"""
        
        return ChatPromptTemplate.from_template(template)
    
    def _create_chain(self):
        """
        Create RAG chain using LCEL.
        
        Returns:
            Runnable chain
        """
        prompt = self._create_prompt_template()
        
        # Get retrieval configuration
        retrieval_config = self.config.get('retrieval', {})
        k = retrieval_config.get('top_k', 5)
        
        # Create retriever
        retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": k}
        )
        
        print(f"   Retrieval: top {k} chunks")
        
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        # Create chain using LCEL
        chain = (
            {
                "context": retriever | format_docs,
                "question": RunnablePassthrough()
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        # Store retriever for getting sources
        self.retriever = retriever
        
        return chain
    
    def query(self, question: str, return_sources: bool = True, k: Optional[int] = None) -> Dict:
        """
        Query the RAG system.
        
        Args:
            question: Question in German
            return_sources: Whether to return source documents
            k: Number of sources to retrieve (overrides default)
            
        Returns:
            Dictionary with answer and optional sources
        """
        print(f"\n❓ Question: {question}")
        print("🔍 Searching...")
        
        # Determine k value
        if k is None:
            retrieval_config = self.config.get('retrieval', {})
            k = retrieval_config.get('top_k', 5)
        
        print(f"   Using {k} chunks for retrieval")
        
        # Get sources
        sources = self.vectorstore.similarity_search(question, k=k)
        
        # Format context from sources
        context = "\n\n".join(doc.page_content for doc in sources)
        
        # Get prompt and run LLM
        prompt = self._create_prompt_template()
        messages = prompt.format_messages(context=context, question=question)
        answer = self.llm.invoke(messages).content
        
        print(f"\n💡 Answer: {answer}")
        
        if return_sources and sources:
            print(f"\n📚 Sources ({len(sources)} chunks):")
            for i, doc in enumerate(sources, 1):
                page = doc.metadata.get('page_number', 'Unknown')
                preview = doc.page_content[:100].replace('\n', ' ')
                print(f"   {i}. Page {page}: {preview}...")
        
        return {
            'question': question,
            'answer': answer,
            'sources': sources if return_sources else []
        }
    
    def batch_query(self, questions: List[str]) -> List[Dict]:
        """
        Query multiple questions.
        
        Args:
            questions: List of questions
            
        Returns:
            List of results
        """
        results = []
        for question in questions:
            result = self.query(question)
            results.append(result)
            print("\n" + "="*60 + "\n")
        
        return results


def main():
    """Test the RAG system."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Query Swiss History RAG system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python rag_chain.py
  
  # Single question
  python rag_chain.py --question "Wann wurde die Schweiz gegründet?"
  
  # Test with sample questions
  python rag_chain.py --test
        """
    )
    
    parser.add_argument(
        '--question', '-q',
        type=str,
        help='Question to ask (in German)'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run test with sample questions'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🇨🇭 Swiss History RAG System")
    print("=" * 60)
    print()
    
    try:
        # Initialize RAG
        rag = SwissHistoryRAG()
        
        if args.test:
            # Test with sample questions
            print("\n" + "=" * 60)
            print("🧪 Testing with sample questions")
            print("=" * 60)
            
            test_questions = [
                "Wann wurde die Schweiz gegründet?",
                "Wer war Wilhelm Tell?",
                "Was ist die Eidgenossenschaft?",
                "Welche Rolle spielte die Schweiz im Zweiten Weltkrieg?",
            ]
            
            rag.batch_query(test_questions)
        
        elif args.question:
            # Single question
            rag.query(args.question)
        
        else:
            # Interactive mode
            print("\n💬 Interactive mode - ask questions about Swiss history")
            print("   (Type 'exit' or 'quit' to stop)\n")
            
            while True:
                try:
                    question = input("❓ Your question: ").strip()
                    
                    if not question:
                        continue
                    
                    if question.lower() in ['exit', 'quit', 'q']:
                        print("\n👋 Goodbye!")
                        break
                    
                    rag.query(question)
                    print("\n" + "="*60 + "\n")
                    
                except KeyboardInterrupt:
                    print("\n\n👋 Goodbye!")
                    break
        
        print("\n" + "=" * 60)
        print("✅ Session complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
