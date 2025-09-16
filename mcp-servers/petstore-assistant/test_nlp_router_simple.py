"""Simple test script to demonstrate NLP-based tool routing without API calls"""

import asyncio
import os
from dotenv import load_dotenv
from petstore_assistant.utils.openrouter import OpenRouterClient
from petstore_assistant.tools.nlp_tool_router import NLPToolRouter


# Mock classes that simulate the tool operations without actual API calls
class MockCartOperations:
    async def add_to_cart(self, user_id: str, item_id: str, quantity: int):
        return {"success": True, "message": f"Added {quantity} of {item_id} to cart"}
    
    async def view_cart(self, user_id: str):
        return {"success": True, "cart": {"items": [{"name": "Dog Food", "quantity": 2}]}}
    
    async def remove_from_cart(self, user_id: str, item_id: str):
        return {"success": True, "message": f"Removed {item_id} from cart"}
    
    async def update_cart_item(self, user_id: str, item_id: str, quantity: int):
        return {"success": True, "message": f"Updated {item_id} quantity to {quantity}"}


class MockPetKnowledge:
    async def get_breed_info(self, species: str, breed: str):
        return {"success": True, "info": f"Information about {breed} {species}"}
    
    async def get_health_conditions(self, species: str, breed=None, age=None):
        return {"success": True, "conditions": f"Health info for {species}"}
    
    async def get_nutrition_guide(self, species: str, age: str, breed=None, weight=None, activity_level=None):
        return {"success": True, "guide": f"Nutrition guide for {age} {species}"}


class MockProductSearch:
    async def search_products(self, query: str, category=None, limit=10):
        return [{"name": f"Product matching '{query}'", "price": 19.99}]


class MockOrderManagement:
    async def create_order(self, user_id: str):
        return {"success": True, "order_id": "12345"}
    
    async def get_order_status(self, order_id: str):
        return {"success": True, "status": "shipped", "order_id": order_id}


async def test_nlp_routing():
    """Test various natural language inputs"""
    # Load environment variables
    load_dotenv()
    
    # Initialize components with mocks
    openrouter = OpenRouterClient(os.getenv("OPENROUTER_API_KEY"))
    
    # Use mock handlers instead of real ones
    cart_ops = MockCartOperations()
    pet_knowledge = MockPetKnowledge()
    product_search = MockProductSearch()
    order_mgmt = MockOrderManagement()
    
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
    print("NLP-BASED TOOL ROUTING TEST (MOCK MODE)")
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
            
            # Show the message (truncated if too long)
            message = result.get('message', 'No message')
            if len(message) > 200:
                message = message[:200] + "..."
            print(f"Response: {message}")
            
            if result.get('missing'):
                print(f"Missing Parameters: {', '.join(result['missing'])}")
                
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print("=" * 80)
    
    # Close the client
    await openrouter.client.aclose()


if __name__ == "__main__":
    asyncio.run(test_nlp_routing())
