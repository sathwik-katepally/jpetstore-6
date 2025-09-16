"""OpenRouter integration for AI chat capabilities"""

import httpx
from typing import Dict, Any, List, Optional
import json


class OpenRouterClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.client = httpx.AsyncClient()
    
    async def chat(self, model: str, messages: List[Dict[str, str]], 
                   context: Optional[Dict[str, Any]] = None) -> str:
        """Send a chat request to OpenRouter API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://jpetstore.com",
                "X-Title": "JPetStore Assistant",
                "Content-Type": "application/json"
            }
            
            # Prepare the request payload
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000,
                "top_p": 1,
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "stream": False
            }
            
            # Add context to system message if provided
            if context and messages and messages[0]["role"] == "system":
                context_str = f"\n\nContext: {json.dumps(context)}"
                messages[0]["content"] += context_str
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except httpx.HTTPError as e:
            # Fallback to a simple response if API fails
            return self._generate_fallback_response(messages[-1]["content"] if messages else "")
        except Exception as e:
            return f"I apologize, but I'm having trouble processing your request. Error: {str(e)}"
    
    def _generate_fallback_response(self, user_message: str) -> str:
        """Generate a fallback response when API is unavailable"""
        user_message_lower = user_message.lower()
        
        # Cart-related queries
        if any(word in user_message_lower for word in ["cart", "add", "remove", "buy"]):
            return "I can help you manage your shopping cart. You can add items, update quantities, or remove items. What would you like to do?"
        
        # Pet information queries
        if any(word in user_message_lower for word in ["breed", "dog", "cat", "fish", "bird", "reptile"]):
            return "I can provide detailed information about various pet breeds, their characteristics, care requirements, and health considerations. Which pet are you interested in learning about?"
        
        # Product queries
        if any(word in user_message_lower for word in ["product", "food", "toy", "accessory"]):
            return "I can help you find the perfect products for your pet. What type of product are you looking for?"
        
        # Order queries
        if any(word in user_message_lower for word in ["order", "status", "delivery", "track"]):
            return "I can help you check your order status or create a new order from your cart. What would you like to know?"
        
        # Default response
        return "I'm here to help you with your pet store needs! I can assist with shopping, pet information, product recommendations, and order management. How can I help you today?"
    
    async def analyze_intent(self, message: str) -> Dict[str, Any]:
        """Analyze user intent from their message"""
        system_prompt = """You are an intent classifier for a pet store chatbot. 
        Analyze the user's message and return a JSON object with:
        - type: one of ['cart_operation', 'pet_info', 'product_search', 'order_management', 'general']
        - parameters: relevant parameters extracted from the message
        - confidence: confidence score (0-1)
        
        For cart operations, identify: operation (add_to_cart, remove_from_cart, update_cart, view_cart), itemId, quantity
        For pet info, identify: infoType (breed_info, health_conditions, living_conditions, nutrition_guide), species, breed
        For product search, identify: query, category
        For order management, identify: operation (create_order, check_status, cancel_order), orderId
        """
        
        try:
            response = await self.chat(
                model="anthropic/claude-3-haiku",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ]
            )
            
            # Try to parse the response as JSON
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # Fallback to simple pattern matching
                return self._simple_intent_analysis(message)
                
        except Exception:
            return self._simple_intent_analysis(message)
    
    def _simple_intent_analysis(self, message: str) -> Dict[str, Any]:
        """Simple pattern-based intent analysis as fallback"""
        message_lower = message.lower()
        
        # Cart operations
        if any(phrase in message_lower for phrase in ["add to cart", "add item", "buy"]):
            return {
                "type": "cart_operation",
                "parameters": {"operation": "add_to_cart"},
                "confidence": 0.7
            }
        
        if any(phrase in message_lower for phrase in ["remove from cart", "delete item"]):
            return {
                "type": "cart_operation",
                "parameters": {"operation": "remove_from_cart"},
                "confidence": 0.7
            }
        
        if any(phrase in message_lower for phrase in ["view cart", "show cart", "what's in my cart"]):
            return {
                "type": "cart_operation",
                "parameters": {"operation": "view_cart"},
                "confidence": 0.8
            }
        
        # Pet information
        if any(word in message_lower for word in ["breed", "breeds", "tell me about"]) and \
           any(pet in message_lower for pet in ["dog", "cat", "fish", "bird", "reptile"]):
            return {
                "type": "pet_info",
                "parameters": {"infoType": "breed_info"},
                "confidence": 0.7
            }
        
        if any(word in message_lower for word in ["health", "disease", "condition", "sick"]):
            return {
                "type": "pet_info",
                "parameters": {"infoType": "health_conditions"},
                "confidence": 0.7
            }
        
        if any(word in message_lower for word in ["food", "feed", "nutrition", "diet"]):
            return {
                "type": "pet_info",
                "parameters": {"infoType": "nutrition_guide"},
                "confidence": 0.7
            }
        
        # Product search
        if any(word in message_lower for word in ["product", "search", "find", "show me", "looking for"]):
            return {
                "type": "product_search",
                "parameters": {},
                "confidence": 0.6
            }
        
        # Order management
        if any(word in message_lower for word in ["order", "status", "track", "delivery"]):
            return {
                "type": "order_management",
                "parameters": {"operation": "check_status"},
                "confidence": 0.7
            }
        
        # Default to general
        return {
            "type": "general",
            "parameters": {},
            "confidence": 0.5
        }
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
