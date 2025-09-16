"""Test script to demonstrate NLP-based tool routing"""

import asyncio
import os
from dotenv import load_dotenv
from petstore_assistant.utils.openrouter import OpenRouterClient
from petstore_assistant.tools.nlp_tool_router import NLPToolRouter
from petstore_assistant.tools.cart_operations import CartOperations
from petstore_assistant.tools.pet_knowledge import PetKnowledge
from petstore_assistant.tools.product_search import ProductSearch
from petstore_assistant.tools.order_management import OrderManagement


async def test_nlp_routing():
    """Test various natural language inputs"""
    # Load environment variables
    load_dotenv()
    
    # Initialize components
    openrouter = OpenRouterClient(os.getenv("OPENROUTER_API_KEY"))
    api_url = os.getenv("JPETSTORE_API_URL", "http://localhost:8081/api")
    
    # Initialize tool handlers
    cart_ops = CartOperations(api_url)
    pet_knowledge = PetKnowledge()
    product_search = ProductSearch(api_url)
    order_mgmt = OrderManagement(api_url)
    
    # Initialize NLP router
    nlp_router = NLPToolRouter(openrouter, cart_ops, pet_knowledge, product_search, order_mgmt)
    
    # Test cases with natural language inputs
    test_cases = [
        {
            "message": "I want to add 2 items of EST-1 to my cart",
            "description": "Adding items to cart with quantity"
        },
        {
            "message": "Show me what's in my shopping cart",
            "description": "Viewing cart contents"
        },
        {
            "message": "Tell me about Golden Retriever dogs",
            "description": "Getting breed information"
        },
        {
            "message": "What health issues do senior cats have?",
            "description": "Health conditions query"
        },
        {
            "message": "I need food for my adult labrador who weighs 30kg",
            "description": "Nutrition guide with details"
        },
        {
            "message": "Search for dog toys",
            "description": "Product search"
        },
        {
            "message": "Find fish food products",
            "description": "Category-specific product search"
        },
        {
            "message": "What's the status of order #12345?",
            "description": "Order status check"
        },
        {
            "message": "Hello, how can you help me?",
            "description": "General greeting"
        }
    ]
    
    # Run test cases
    user_id = "test_user_123"
    
    print("=" * 80)
    print("NLP-BASED TOOL ROUTING TEST")
    print("=" * 80)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['description']}")
        print(f"Input: \"{test['message']}\"")
        print("-" * 40)
        
        try:
            result = await nlp_router.route_message(
                test["message"],
                user_id
            )
            
            print(f"Success: {result.get('success', False)}")
            print(f"Type: {result.get('type', 'unknown')}")
            
            if result.get('tool_name'):
                print(f"Tool Used: {result['tool_name']}")
            
            print(f"Response: {result.get('message', 'No message')[:200]}...")
            
            if result.get('missing'):
                print(f"Missing Parameters: {', '.join(result['missing'])}")
                
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print("=" * 80)
    
    # Close the client
    await openrouter.client.aclose()


async def interactive_test():
    """Interactive test mode"""
    # Load environment variables
    load_dotenv()
    
    # Initialize components
    openrouter = OpenRouterClient(os.getenv("OPENROUTER_API_KEY"))
    api_url = os.getenv("JPETSTORE_API_URL", "http://localhost:8081/api")
    
    # Initialize tool handlers
    cart_ops = CartOperations(api_url)
    pet_knowledge = PetKnowledge()
    product_search = ProductSearch(api_url)
    order_mgmt = OrderManagement(api_url)
    
    # Initialize NLP router
    nlp_router = NLPToolRouter(openrouter, cart_ops, pet_knowledge, product_search, order_mgmt)
    
    user_id = "interactive_user"
    context = {}
    
    print("\n" + "=" * 80)
    print("INTERACTIVE NLP CHATBOT TEST")
    print("=" * 80)
    print("Type your message in natural language. Type 'quit' to exit.")
    print("Examples:")
    print("- 'Add EST-1 to my cart'")
    print("- 'Tell me about Persian cats'")
    print("- 'Search for dog food'")
    print("- 'What's in my cart?'")
    print("=" * 80 + "\n")
    
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\nGoodbye!")
                break
            
            if not user_input:
                continue
            
            # Process the message
            print("\nAssistant: ", end="", flush=True)
            result = await nlp_router.route_message(
                user_input,
                user_id,
                context
            )
            
            # Display the response
            print(result.get('message', 'I encountered an error processing your request.'))
            
            # Update context if needed
            if result.get('success') and result.get('type') == 'tool_result':
                context['last_tool'] = result.get('tool_name')
                context['last_result'] = result.get('result')
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
    
    # Close the client
    await openrouter.client.aclose()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        asyncio.run(interactive_test())
    else:
        asyncio.run(test_nlp_routing())
