"""
RAGAS Evaluation for Swiss History RAG
Evaluates RAG system quality using faithfulness, answer relevance, and context precision.
"""
import sys
from pathlib import Path
from typing import List, Dict
import pandas as pd
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    Faithfulness,
    AnswerRelevancy,
    ContextPrecision,
    ContextRecall
)
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

from src.retrieval.rag_chain import SwissHistoryRAG
from src.utils import load_config, get_env_variable


# Test questions for Swiss History
TEST_QUESTIONS = [
    {
        "question": "Wann wurde die Schweiz gegründet?",
        "ground_truth": "Die Schweiz wurde 1291 gegründet, als Uri, Schwyz und Unterwalden den ewigen Bund schlossen."
    },
    {
        "question": "Wer war Wilhelm Tell?",
        "ground_truth": "Wilhelm Tell war eine legendäre Figur der Schweizer Geschichte, der den Apfel vom Kopf seines Sohnes schoss und später den Vogt Gessler erschoss."
    },
    {
        "question": "Was war die Schlacht am Morgarten?",
        "ground_truth": "Die Schlacht am Morgarten fand 1315 statt, wo die Eidgenossen die Österreicher besiegten und den ewigen Bund in Brunnen erneuerten."
    },
    {
        "question": "Welche Orte gehörten zum Bund der acht alten Orte?",
        "ground_truth": "Die acht alten Orte waren Uri, Schwyz, Unterwalden, Luzern, Zürich, Glarus, Zug und Bern."
    },
    {
        "question": "Was war der Sonderbundskrieg?",
        "ground_truth": "Der Sonderbundskrieg war 1847 ein kurzer Bürgerkrieg zwischen katholischen und liberalen Kantonen, der zur Gründung des Bundesstaates 1848 führte."
    },
    {
        "question": "Wann trat die erste Bundesverfassung in Kraft?",
        "ground_truth": "Die erste Bundesverfassung der Schweiz trat 1848 in Kraft und wandelte den Staatenbund in einen Bundesstaat um."
    },
    {
        "question": "Was war die Schlacht bei Sempach?",
        "ground_truth": "Die Schlacht bei Sempach fand 1386 statt, wo die Eidgenossen unter großen Verlusten die Österreicher besiegten."
    },
    {
        "question": "Wer war Karl Borromäus?",
        "ground_truth": "Karl Borromäus war ein Kardinal und Erzbischof von Mailand (1538-1584), der die Gegenreformation in der Schweiz förderte."
    },
    {
        "question": "Was waren die Freischarenzüge?",
        "ground_truth": "Die Freischarenzüge waren 1844 und 1845 bewaffnete Züge liberaler Kräfte gegen den Kanton Luzern wegen der Jesuitenberufung."
    },
    {
        "question": "Wann wurde die Schweizer Neutralität anerkannt?",
        "ground_truth": "Die immerwährende Neutralität der Schweiz wurde 1815 am Wiener Kongress anerkannt."
    }
]


class RAGASEvaluator:
    """Evaluate RAG system using RAGAS metrics."""
    
    def __init__(self):
        """Initialize evaluator."""
        print("🔧 Initializing RAGAS Evaluator...")
        self.rag = SwissHistoryRAG()
    
        # Initialize LLM and embeddings for RAGAS
        api_key = get_env_variable('OPENAI_API_KEY')
        self.llm = ChatOpenAI(
            model="gpt-4o-mini", 
            openai_api_key=api_key,
            temperature=0.7,  # Add temperature for variety
            model_kwargs={"n": 3}  # Request 3 generations
        )   
        self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    
        print("✅ RAG system loaded")    
    
    def run_evaluation(self, test_questions: List[Dict] = None) -> Dict:
        """
        Run RAGAS evaluation on test questions.
        
        Args:
            test_questions: List of dicts with 'question' and 'ground_truth'
            
        Returns:
            Evaluation results
        """
        if test_questions is None:
            test_questions = TEST_QUESTIONS
        
        print(f"\n📊 Running evaluation on {len(test_questions)} questions...")
        print("=" * 60)
        
        # Collect data for RAGAS
        questions = []
        answers = []
        contexts = []
        ground_truths = []
        
        for i, item in enumerate(test_questions, 1):
            question = item['question']
            ground_truth = item['ground_truth']
            
            print(f"\n{i}. {question}")
            
            # Query RAG system
            result = self.rag.query(question, return_sources=True)
            answer = result['answer']
            sources = result['sources']
            
            # Extract contexts from sources
            context_list = [doc.page_content for doc in sources]
            
            questions.append(question)
            answers.append(answer)
            contexts.append(context_list)
            ground_truths.append(ground_truth)
            
            print(f"   ✓ Processed")
        
        # Create dataset for RAGAS
        data = {
            'question': questions,
            'answer': answers,
            'contexts': contexts,
            'ground_truth': ground_truths
        }
        
        dataset = Dataset.from_dict(data)
        
        print("\n" + "=" * 60)
        print("🔍 Computing RAGAS metrics...")
        print("=" * 60)
        
        # Evaluate with RAGAS
        result = evaluate(
            dataset,
            metrics=[
                Faithfulness(),
                AnswerRelevancy(),
                ContextPrecision(),
                ContextRecall()
            ],
            llm=self.llm,
            embeddings=self.embeddings
        )
        
        return result
    
    def display_results(self, result):
        """Display evaluation results."""
        print("\n" + "=" * 60)
        print("📈 RAGAS Evaluation Results")
        print("=" * 60)
    
        # Convert to DataFrame first
        df = result.to_pandas()
    
        # Calculate overall scores (mean of each metric)
        print("\n🎯 Overall Scores:")
        print(f"  Faithfulness:        {df['faithfulness'].mean():.4f}")
        print(f"  Answer Relevancy:    {df['answer_relevancy'].mean():.4f}")
        print(f"  Context Precision:   {df['context_precision'].mean():.4f}")
        print(f"  Context Recall:      {df['context_recall'].mean():.4f}")
    
        print("\n📊 Detailed Results:")
        # Show only the relevant columns with better formatting
        display_df = df[['user_input', 'response', 'faithfulness', 'answer_relevancy', 'context_precision', 'context_recall']].copy()
        display_df['user_input'] = display_df['user_input'].str[:50] + '...'  # Truncate long questions
        display_df['response'] = display_df['response'].str[:100] + '...'  # Truncate long answers
        print(display_df.to_string(index=False))
    
        return df
        
    def save_results(self, df: pd.DataFrame, filename: str = None):
        """Save results to CSV."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ragas_evaluation_{timestamp}.csv"
        
        output_dir = Path(__file__).parent.parent.parent / "data" / "evaluation"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / filename
        df.to_csv(output_path, index=False)
        
        print(f"\n💾 Results saved to: {output_path}")
        return output_path


def main():
    """Run RAGAS evaluation."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Evaluate Swiss History RAG with RAGAS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Metrics:
  - Faithfulness: Does the answer align with retrieved context?
  - Answer Relevancy: Does the answer address the question?
  - Context Precision: Are retrieved contexts relevant?
  - Context Recall: Are all relevant contexts retrieved?

Examples:
  # Run full evaluation
  python ragas_eval.py
  
  # Run with custom test file
  python ragas_eval.py --test-file my_questions.json
        """
    )
    
    parser.add_argument(
        '--test-file',
        type=str,
        help='JSON file with custom test questions'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output CSV filename'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🇨🇭 RAGAS Evaluation - Swiss History RAG")
    print("=" * 60)
    print()
    
    try:
        evaluator = RAGASEvaluator()
        
        # Load custom test questions if provided
        test_questions = None
        if args.test_file:
            import json
            with open(args.test_file, 'r', encoding='utf-8') as f:
                test_questions = json.load(f)
            print(f"📄 Loaded {len(test_questions)} questions from {args.test_file}")
        
        # Run evaluation
        result = evaluator.run_evaluation(test_questions)
        
        # Display results
        df = evaluator.display_results(result)
        
        # Save results
        evaluator.save_results(df, args.output)
        
        print("\n" + "=" * 60)
        print("✅ Evaluation complete!")
        print("=" * 60)
        
        # Interpretation guide
        print("\n📚 Score Interpretation:")
        print("  0.8 - 1.0: Excellent")
        print("  0.6 - 0.8: Good")
        print("  0.4 - 0.6: Fair")
        print("  0.0 - 0.4: Needs improvement")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
