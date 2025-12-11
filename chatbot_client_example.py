"""Example client for testing the chatbot API."""

import requests
import json
import uuid

# API base URL
BASE_URL = "http://localhost:8000"


def send_message(query: str, thread_id: str) -> dict:
    """Send a message to the chatbot."""
    response = requests.post(
        f"{BASE_URL}/chat",
        json={
            "query": query,
            "thread_id": thread_id
        }
    )
    return response.json()


def get_history(thread_id: str) -> dict:
    """Get conversation history for a thread."""
    response = requests.get(f"{BASE_URL}/thread/{thread_id}/history")
    return response.json()


def delete_thread(thread_id: str) -> dict:
    """Delete a conversation thread."""
    response = requests.delete(f"{BASE_URL}/thread/{thread_id}")
    return response.json()


def example_conversation():
    """Run an example conversation."""
    # Generate a unique thread ID for this conversation
    thread_id = str(uuid.uuid4())
    print(f"Starting conversation with thread_id: {thread_id}\n")
    
    # Conversation flow
    messages = [
        "Hi, I need insurance quote",
        "I want to add new flood insurance",
        "My name is John Doe, I live at 123 Main Street, Miami, FL 33101, and my email is john.doe@example.com",
        "Yes, please submit the quote request"
    ]
    
    for user_message in messages:
        print(f"User: {user_message}")
        
        # Send message
        response = send_message(user_message, thread_id)
        
        print(f"Assistant: {response['response']}\n")
        print("-" * 80 + "\n")
    
    # Get conversation history
    print("\n=== Conversation History ===")
    history = get_history(thread_id)
    print(f"Total messages: {history['message_count']}")
    
    # Optional: Delete thread when done
    # delete_result = delete_thread(thread_id)
    # print(f"\n{delete_result['message']}")


def interactive_mode():
    """Interactive chatbot mode."""
    thread_id = input("Enter thread_id (or press Enter for new conversation): ").strip()
    
    if not thread_id:
        thread_id = str(uuid.uuid4())
        print(f"Created new conversation with thread_id: {thread_id}")
    else:
        print(f"Continuing conversation: {thread_id}")
    
    print("\nChatbot ready! Type 'quit' to exit, 'history' to view conversation, 'new' for new thread.\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
        
        if user_input.lower() == 'history':
            history = get_history(thread_id)
            print(f"\n=== Conversation History (Thread: {thread_id}) ===")
            for msg in history['messages']:
                if msg['role'] == 'user':
                    print(f"User: {msg['content']}")
                elif msg['role'] == 'assistant':
                    print(f"Assistant: {msg['content']}")
            print("=" * 60 + "\n")
            continue
        
        if user_input.lower() == 'new':
            thread_id = str(uuid.uuid4())
            print(f"Started new conversation with thread_id: {thread_id}\n")
            continue
        
        try:
            response = send_message(user_input, thread_id)
            print(f"Bot: {response['response']}\n")
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    print("Insurance Chatbot Client")
    print("=" * 60)
    print("\n1. Run example conversation")
    print("2. Interactive mode")
    
    choice = input("\nSelect option (1 or 2): ").strip()
    
    if choice == "1":
        example_conversation()
    elif choice == "2":
        interactive_mode()
    else:
        print("Invalid option")

