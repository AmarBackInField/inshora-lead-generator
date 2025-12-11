"""
Test script to verify RAG service functionality before deploying the agent.
"""

import os
from dotenv import load_dotenv
from RAGService import RAGService

load_dotenv()

# Initialize RAG Service
rag_service = RAGService(
    qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"),
    qdrant_api_key=os.getenv("QDRANT_API_KEY", ""),
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

FAQ_COLLECTION = os.getenv("FAQ_COLLECTION_NAME", "faq_knowledge_base")
CRM_COLLECTION = os.getenv("CRM_COLLECTION_NAME", "crm_database")


def test_faq_search():
    """Test FAQ knowledge base search."""
    print("\n" + "=" * 60)
    print("Testing FAQ Search")
    print("=" * 60)
    
    test_queries = [
        "What are your business hours?",
        "How do I reset my password?",
        "What is your refund policy?",
        "Do you offer technical support?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        try:
            results = rag_service.retrieval_based_search(
                query=query,
                collection_name=FAQ_COLLECTION,
                top_k=3
            )
            
            if results:
                print(f"✓ Found {len(results)} results")
                print(f"  Top result (score: {results[0]['score']:.3f}):")
                print(f"  {results[0]['text'][:200]}...")
            else:
                print("✗ No results found")
                
        except Exception as e:
            print(f"✗ Error: {str(e)}")


def test_crm_lookup():
    """Test CRM database lookup."""
    print("\n" + "=" * 60)
    print("Testing CRM Lookup")
    print("=" * 60)
    
    test_identifiers = [
        "customer ID 12345",
        "john.doe@example.com",
        "+1-555-0123",
        "John Doe"
    ]
    
    for identifier in test_identifiers:
        print(f"\nLookup: {identifier}")
        try:
            results = rag_service.retrieval_based_search(
                query=identifier,
                collection_name=CRM_COLLECTION,
                top_k=1
            )
            
            if results:
                print(f"✓ Found customer (score: {results[0]['score']:.3f})")
                print(f"  {results[0]['text'][:200]}...")
            else:
                print("✗ No customer found")
                
        except Exception as e:
            print(f"✗ Error: {str(e)}")


def test_collection_status():
    """Check status of collections."""
    print("\n" + "=" * 60)
    print("Checking Collection Status")
    print("=" * 60)
    
    try:
        collections = rag_service.qdrant_client.get_collections().collections
        
        print(f"\nFound {len(collections)} collection(s):")
        for col in collections:
            print(f"  - {col.name}")
            
            # Get collection info
            info = rag_service.qdrant_client.get_collection(col.name)
            print(f"    Vectors: {info.vectors_count}")
            print(f"    Status: {info.status}")
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")


def test_connection():
    """Test connection to Qdrant."""
    print("\n" + "=" * 60)
    print("Testing Qdrant Connection")
    print("=" * 60)
    
    try:
        # Try to get collections
        collections = rag_service.qdrant_client.get_collections()
        print("✓ Successfully connected to Qdrant")
        return True
    except Exception as e:
        print(f"✗ Failed to connect to Qdrant: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Ensure Qdrant is running: docker run -p 6333:6333 qdrant/qdrant")
        print("2. Check QDRANT_URL in .env file")
        print("3. Verify QDRANT_API_KEY if using cloud Qdrant")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("RAG Service Test Suite")
    print("=" * 60)
    
    # Test connection first
    if not test_connection():
        print("\n⚠ Cannot proceed without Qdrant connection")
        return
    
    # Check collection status
    test_collection_status()
    
    # Test FAQ search
    print("\n⚠ Note: Tests will fail if collections are empty.")
    print("  Run 'python setup_rag.py' to load data first.\n")
    
    test_faq_search()
    test_crm_lookup()
    
    print("\n" + "=" * 60)
    print("Test Suite Complete")
    print("=" * 60)
    print("\nNext steps:")
    print("1. If collections are empty, run: python setup_rag.py")
    print("2. Add your FAQ and CRM data to setup_rag.py")
    print("3. Test agent with: python agent.py start")


if __name__ == "__main__":
    main()

