"""Test script for MCP server functionality"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_mcp_server():
    """Test the MCP server with various tool calls"""
    
    # Server parameters for running the MCP server
    server_params = StdioServerParameters(
        command="python3",
        args=["-m", "petstore_assistant.server"],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            init_result = await session.initialize()
            
            print("=" * 80)
            print("MCP SERVER TEST")
            print("=" * 80)
            print(f"\nServer: {init_result.serverInfo.name}")
            print(f"Version: {init_result.serverInfo.version}")
            
            # List available tools
            tools = await session.list_tools()
            print(f"\nAvailable tools ({len(tools.tools)}):")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            print("\n" + "=" * 80)
            print("TESTING TOOLS")
            print("=" * 80)
            
            # Test cases
            test_cases = [
                {
                    "name": "Test 1: Natural Language Chat - Add to Cart",
                    "tool": "chat",
                    "args": {
                        "message": "I want to add 3 items of product EST-1 to my cart",
                        "user_id": "test_user_123"
                    }
                },
                {
                    "name": "Test 2: Get Breed Information",
                    "tool": "get_breed_info",
                    "args": {
                        "species": "dog",
                        "breed": "golden retriever"
                    }
                },
                {
                    "name": "Test 3: Search Products",
                    "tool": "search_products",
                    "args": {
                        "query": "dog food",
                        "limit": 5
                    }
                },
                {
                    "name": "Test 4: View Cart",
                    "tool": "view_cart",
                    "args": {
                        "user_id": "test_user_123"
                    }
                },
                {
                    "name": "Test 5: Get Health Conditions",
                    "tool": "get_health_conditions",
                    "args": {
                        "species": "cat",
                        "age": "senior"
                    }
                },
                {
                    "name": "Test 6: Natural Language Chat - General Query",
                    "tool": "chat",
                    "args": {
                        "message": "What kind of food should I feed my 2-year-old labrador?",
                        "user_id": "test_user_123"
                    }
                }
            ]
            
            # Execute test cases
            for test in test_cases:
                print(f"\n{test['name']}")
                print("-" * 40)
                print(f"Tool: {test['tool']}")
                print(f"Arguments: {json.dumps(test['args'], indent=2)}")
                
                try:
                    result = await session.call_tool(test['tool'], test['args'])
                    
                    # Parse the result
                    if result.content and len(result.content) > 0:
                        content = result.content[0]
                        if hasattr(content, 'text'):
                            response = json.loads(content.text)
                            print(f"\nResult:")
                            print(json.dumps(response, indent=2))
                        else:
                            print(f"\nResult: {content}")
                    else:
                        print("\nResult: No content returned")
                        
                except Exception as e:
                    print(f"\nError: {str(e)}")
                
                print("=" * 80)
            
            print("\nAll tests completed!")


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
