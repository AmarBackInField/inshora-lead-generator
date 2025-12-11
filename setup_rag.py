"""
Setup script to initialize RAG collections and load sample data.
Run this script before starting the agent to populate the knowledge base.
"""

import os
import asyncio
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


def setup_faq_collection():
    """
    Setup FAQ knowledge base collection.
    Add your FAQ documents, PDFs, or websites here.
    """
    print("Setting up FAQ Knowledge Base...")
    
    # Example: Load from website
    # rag_service.load_data_to_qdrant(
    #     collection_name=FAQ_COLLECTION,
    #     url_link="https://your-company.com/faq"
    # )
    
    # Example: Load from PDF
    # rag_service.load_data_to_qdrant(
    #     collection_name=FAQ_COLLECTION,
    #     pdf_file="path/to/faq.pdf"
    # )
    
    # Example: Load from Excel
    # rag_service.load_data_to_qdrant(
    #     collection_name=FAQ_COLLECTION,
    #     excel_file="path/to/faq.xlsx"
    # )
    
    print(f"FAQ Collection '{FAQ_COLLECTION}' is ready.")


def setup_crm_collection():
    """
    Setup CRM database collection.
    Add your customer data here (ensure compliance with privacy regulations).
    """
    print("Setting up CRM Database...")
    
    # Example: Load customer data from Excel
    # rag_service.load_data_to_qdrant(
    #     collection_name=CRM_COLLECTION,
    #     excel_file="path/to/customer_data.xlsx"
    # )
    
    print(f"CRM Collection '{CRM_COLLECTION}' is ready.")


async def setup_async_example():
    """
    Example of loading multiple sources asynchronously.
    This is faster for loading multiple documents.
    """
    print("Loading multiple sources in parallel...")
    
    result = await rag_service.load_data_to_qdrant_async(
        collection_name=FAQ_COLLECTION,
        url_links=[
            # "https://your-company.com/faq",
            # "https://your-company.com/help"
        ],
        pdf_files=[
            # "path/to/faq1.pdf",
            # "path/to/faq2.pdf"
        ],
        excel_files=[
            # "path/to/data1.xlsx",
            # "path/to/data2.xlsx"
        ]
    )
    
    print(f"Loaded {result['total_chunks_loaded']} chunks from {result['sources_processed']} sources")


def main():
    """Main setup function."""
    print("=" * 60)
    print("RAG Knowledge Base Setup")
    print("=" * 60)
    
    try:
        # Create or verify collections
        rag_service.create_collection(FAQ_COLLECTION)
        rag_service.create_collection(CRM_COLLECTION)
        
        # Setup FAQ knowledge base
        setup_faq_collection()
        
        # Setup CRM database
        setup_crm_collection()
        
        # Optional: Use async loading for better performance
        # asyncio.run(setup_async_example())
        
        print("\n" + "=" * 60)
        print("Setup Complete!")
        print("=" * 60)
        print(f"\nCollections created:")
        print(f"  - {FAQ_COLLECTION} (FAQ Knowledge Base)")
        print(f"  - {CRM_COLLECTION} (CRM Database)")
        print("\nYou can now start the agent with: python agent.py start")
        
    except Exception as e:
        print(f"\nError during setup: {str(e)}")
        print("Please check your configuration and try again.")


if __name__ == "__main__":
    main()

