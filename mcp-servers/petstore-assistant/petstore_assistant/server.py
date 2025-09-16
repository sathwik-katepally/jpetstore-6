"""Main MCP server implementation for JPetStore assistant"""

import os
import json
import asyncio
from typing import Any, Dict, List
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

from .tools.cart_operations import CartOperations
from .tools.pet_knowledge import PetKnowledge
from .tools.product_search import ProductSearch
from .tools.order_management import OrderManagement
from .tools.nlp_tool_router import NLPToolRouter
from .utils.openrouter import OpenRouterClient


# Create the server instance
server = Server("petstore-assistant")

# Initialize handlers
openrouter = None
api_url = None
cart_ops = None
pet_knowledge = None
product_search = None
order_mgmt = None
nlp_router = None


def initialize_handlers():
    """Initialize all handlers"""
    global openrouter, api_url, cart_ops, pet_knowledge, product_search, order_mgmt, nlp_router
    
    openrouter = OpenRouterClient(os.getenv("OPENROUTER_API_KEY"))
    api_url = os.getenv("JPETSTORE_API_URL", "http://localhost:8081/api")
    
    # Initialize tool handlers
    cart_ops = CartOperations(api_url)
    pet_knowledge = PetKnowledge()
    product_search = ProductSearch(api_url)
    order_mgmt = OrderManagement(api_url)
    
    # Initialize NLP router with all handlers
    nlp_router = NLPToolRouter(openrouter, cart_ops, pet_knowledge, product_search, order_mgmt)


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List all available tools"""
    return [
        types.Tool(
            name="chat",
            description="Process natural language input and automatically select and execute the appropriate tool based on user intent",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "The user's natural language message"},
                    "user_id": {"type": "string", "description": "User ID for context"},
                    "context": {"type": "object", "description": "Optional context from previous interactions"}
                },
                "required": ["message", "user_id"]
            }
        ),
        types.Tool(
            name="get_breed_info",
            description="Get detailed information about a specific pet breed",
            inputSchema={
                "type": "object",
                "properties": {
                    "species": {"type": "string", "description": "Pet species (dog, cat, etc.)"},
                    "breed": {"type": "string", "description": "Breed name"}
                },
                "required": ["species", "breed"]
            }
        ),
        types.Tool(
            name="get_health_conditions",
            description="Get information about health conditions for a pet type",
            inputSchema={
                "type": "object",
                "properties": {
                    "species": {"type": "string", "description": "Pet species"},
                    "breed": {"type": "string", "description": "Breed name (optional)"},
                    "age": {"type": "string", "description": "Age category (optional)"}
                },
                "required": ["species"]
            }
        ),
        types.Tool(
            name="get_nutrition_guide",
            description="Get nutrition and feeding guidelines for a pet",
            inputSchema={
                "type": "object",
                "properties": {
                    "species": {"type": "string", "description": "Pet species"},
                    "age": {"type": "string", "description": "Age category"},
                    "breed": {"type": "string", "description": "Breed name (optional)"},
                    "weight": {"type": "number", "description": "Weight in kg (optional)"},
                    "activity_level": {"type": "string", "description": "Activity level (optional)"}
                },
                "required": ["species", "age"]
            }
        ),
        types.Tool(
            name="search_products",
            description="Search for products in the pet store",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "category": {"type": "string", "description": "Product category (optional)"},
                    "limit": {"type": "integer", "description": "Max results (default: 10)"}
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="add_to_cart",
            description="Add an item to the shopping cart",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID"},
                    "item_id": {"type": "string", "description": "Item ID"},
                    "quantity": {"type": "integer", "description": "Quantity to add"}
                },
                "required": ["user_id", "item_id", "quantity"]
            }
        ),
        types.Tool(
            name="view_cart",
            description="View current cart contents",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID"}
                },
                "required": ["user_id"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls"""
    if not arguments:
        raise ValueError("Missing arguments")
    
    try:
        result = None
        
        if name == "chat":
            # Use the NLP router to process natural language input
            result = await nlp_router.route_message(
                arguments["message"],
                arguments["user_id"],
                arguments.get("context")
            )
        elif name == "get_breed_info":
            result = await pet_knowledge.get_breed_info(
                arguments["species"], 
                arguments["breed"]
            )
        elif name == "get_health_conditions":
            result = await pet_knowledge.get_health_conditions(
                arguments["species"],
                arguments.get("breed"),
                arguments.get("age")
            )
        elif name == "get_nutrition_guide":
            result = await pet_knowledge.get_nutrition_guide(
                arguments["species"],
                arguments["age"],
                arguments.get("breed"),
                arguments.get("weight"),
                arguments.get("activity_level")
            )
        elif name == "search_products":
            result = await product_search.search_products(
                arguments["query"],
                arguments.get("category"),
                arguments.get("limit", 10)
            )
        elif name == "add_to_cart":
            result = await cart_ops.add_to_cart(
                arguments["user_id"], 
                arguments["item_id"], 
                arguments["quantity"]
            )
        elif name == "view_cart":
            result = await cart_ops.view_cart(arguments["user_id"])
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]


async def main():
    """Main entry point for the MCP server"""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Initialize handlers
    initialize_handlers()
    
    # Run the server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="petstore-assistant",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
