"""HTTP wrapper for the MCP server to enable REST API communication"""

import asyncio
import json
import logging
from typing import Any, Dict
from aiohttp import web
import subprocess
import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import the MCP server modules
sys.path.insert(0, str(Path(__file__).parent))

from petstore_assistant.tools.cart_operations import CartOperations
from petstore_assistant.tools.pet_knowledge import PetKnowledge
from petstore_assistant.tools.product_search import ProductSearch
from petstore_assistant.tools.order_management import OrderManagement
from petstore_assistant.tools.nlp_tool_router import NLPToolRouter
from petstore_assistant.utils.openrouter import OpenRouterClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    openrouter = OpenRouterClient(os.getenv("OPENROUTER_API_KEY"))
    api_url = os.getenv("JPETSTORE_API_URL", "http://localhost:8081")
    
    # Initialize tool handlers
    cart_ops = CartOperations(api_url)
    pet_knowledge = PetKnowledge()
    product_search = ProductSearch(api_url)
    order_mgmt = OrderManagement(api_url)
    
    # Initialize NLP router with all handlers
    nlp_router = NLPToolRouter(openrouter, cart_ops, pet_knowledge, product_search, order_mgmt)
    
    logger.info("All handlers initialized successfully")


async def handle_chat(request: web.Request) -> web.Response:
    """Handle chat requests"""
    try:
        data = await request.json()
        tool = data.get('tool', 'chat')
        arguments = data.get('arguments', {})
        
        logger.info(f"Received request for tool: {tool} with arguments: {arguments}")
        
        result = None
        
        if tool == 'chat':
            # Use the NLP router to process natural language input
            result = await nlp_router.route_message(
                arguments.get("message", ""),
                arguments.get("user_id", "guest"),
                arguments.get("context", {})
            )
        elif tool == 'get_breed_info':
            result = await pet_knowledge.get_breed_info(
                arguments.get("species", ""), 
                arguments.get("breed", "")
            )
        elif tool == 'get_health_conditions':
            result = await pet_knowledge.get_health_conditions(
                arguments.get("species", ""),
                arguments.get("breed"),
                arguments.get("age")
            )
        elif tool == 'get_nutrition_guide':
            result = await pet_knowledge.get_nutrition_guide(
                arguments.get("species", ""),
                arguments.get("age", ""),
                arguments.get("breed"),
                arguments.get("weight"),
                arguments.get("activity_level")
            )
        elif tool == 'search_products':
            result = await product_search.search_products(
                arguments.get("query", ""),
                arguments.get("category"),
                arguments.get("limit", 10)
            )
        elif tool == 'add_to_cart':
            result = await cart_ops.add_to_cart(
                arguments.get("user_id", ""), 
                arguments.get("item_id", ""), 
                arguments.get("quantity", 1)
            )
        elif tool == 'view_cart':
            result = await cart_ops.view_cart(arguments.get("user_id", ""))
        else:
            result = {"error": f"Unknown tool: {tool}"}
        
        logger.info(f"Result: {result}")
        
        return web.json_response({
            "success": True,
            "result": result
        })
        
    except Exception as e:
        logger.error(f"Error handling request: {str(e)}", exc_info=True)
        return web.json_response({
            "success": False,
            "error": str(e)
        }, status=500)


async def handle_health(request: web.Request) -> web.Response:
    """Health check endpoint"""
    return web.json_response({"status": "healthy", "service": "petstore-assistant"})


async def init_app() -> web.Application:
    """Initialize the web application"""
    app = web.Application()
    
    # Add CORS middleware
    async def cors_middleware(app, handler):
        async def middleware_handler(request):
            if request.method == 'OPTIONS':
                response = web.Response()
            else:
                response = await handler(request)
            
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            return response
        return middleware_handler
    
    app.middlewares.append(cors_middleware)
    
    # Add routes
    app.router.add_post('/chat', handle_chat)
    app.router.add_get('/health', handle_health)
    
    # Initialize handlers on startup
    async def startup_handler(app):
        initialize_handlers()
    
    app.on_startup.append(startup_handler)
    
    return app


async def main():
    """Main entry point"""
    app = await init_app()
    port = int(os.getenv('MCP_HTTP_PORT', '3001'))
    
    logger.info(f"Starting HTTP wrapper on port {port}")
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    logger.info(f"HTTP wrapper running on http://0.0.0.0:{port}")
    
    # Keep the server running
    await asyncio.Event().wait()


if __name__ == '__main__':
    asyncio.run(main())
