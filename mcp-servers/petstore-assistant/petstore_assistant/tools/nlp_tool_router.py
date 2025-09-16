"""NLP-based tool router that automatically selects and executes tools based on user input"""

import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import re


@dataclass
class ToolMapping:
    """Mapping between intent types and tool functions"""
    tool_name: str
    required_params: List[str]
    optional_params: List[str]
    param_extractors: Dict[str, Any]


class NLPToolRouter:
    """Routes user messages to appropriate tools using NLP analysis"""
    
    def __init__(self, openrouter_client, cart_ops, pet_knowledge, product_search, order_mgmt):
        self.openrouter = openrouter_client
        self.cart_ops = cart_ops
        self.pet_knowledge = pet_knowledge
        self.product_search = product_search
        self.order_mgmt = order_mgmt
        
        # Define tool mappings for each intent type
        self.tool_mappings = {
            "cart_operation": {
                "add_to_cart": ToolMapping(
                    tool_name="add_to_cart",
                    required_params=["user_id", "item_id", "quantity"],
                    optional_params=[],
                    param_extractors={
                        "item_id": self._extract_item_id,
                        "quantity": self._extract_quantity
                    }
                ),
                "view_cart": ToolMapping(
                    tool_name="view_cart",
                    required_params=["user_id"],
                    optional_params=[],
                    param_extractors={}
                ),
                "remove_from_cart": ToolMapping(
                    tool_name="remove_from_cart",
                    required_params=["user_id", "item_id"],
                    optional_params=[],
                    param_extractors={
                        "item_id": self._extract_item_id
                    }
                ),
                "update_cart": ToolMapping(
                    tool_name="update_cart",
                    required_params=["user_id", "item_id", "quantity"],
                    optional_params=[],
                    param_extractors={
                        "item_id": self._extract_item_id,
                        "quantity": self._extract_quantity
                    }
                )
            },
            "pet_info": {
                "breed_info": ToolMapping(
                    tool_name="get_breed_info",
                    required_params=["species", "breed"],
                    optional_params=[],
                    param_extractors={
                        "species": self._extract_species,
                        "breed": self._extract_breed
                    }
                ),
                "health_conditions": ToolMapping(
                    tool_name="get_health_conditions",
                    required_params=["species"],
                    optional_params=["breed", "age"],
                    param_extractors={
                        "species": self._extract_species,
                        "breed": self._extract_breed,
                        "age": self._extract_age
                    }
                ),
                "nutrition_guide": ToolMapping(
                    tool_name="get_nutrition_guide",
                    required_params=["species", "age"],
                    optional_params=["breed", "weight", "activity_level"],
                    param_extractors={
                        "species": self._extract_species,
                        "age": self._extract_age,
                        "breed": self._extract_breed,
                        "weight": self._extract_weight,
                        "activity_level": self._extract_activity_level
                    }
                )
            },
            "product_search": {
                "search": ToolMapping(
                    tool_name="search_products",
                    required_params=["query"],
                    optional_params=["category", "limit"],
                    param_extractors={
                        "query": self._extract_search_query,
                        "category": self._extract_category
                    }
                )
            },
            "order_management": {
                "create_order": ToolMapping(
                    tool_name="create_order",
                    required_params=["user_id"],
                    optional_params=["shipping_address", "payment_method"],
                    param_extractors={}
                ),
                "check_status": ToolMapping(
                    tool_name="check_order_status",
                    required_params=["order_id"],
                    optional_params=[],
                    param_extractors={
                        "order_id": self._extract_order_id
                    }
                )
            }
        }
    
    async def route_message(self, message: str, user_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Route a user message to the appropriate tool and execute it"""
        try:
            # Analyze intent using AI
            intent_analysis = await self.openrouter.analyze_intent(message)
            
            # Extract intent type and parameters
            intent_type = intent_analysis.get("type", "general")
            intent_params = intent_analysis.get("parameters", {})
            confidence = intent_analysis.get("confidence", 0.5)
            
            # Debug logging
            print(f"DEBUG: Intent analysis result: {intent_analysis}")
            
            # Handle general queries
            if intent_type == "general" or confidence < 0.5:
                return await self._handle_general_query(message, context)
            
            # Get the appropriate tool mapping
            operation = intent_params.get("operation", "search" if intent_type == "product_search" else None)
            if not operation:
                operation = intent_params.get("infoType", "breed_info" if intent_type == "pet_info" else None)
            
            if intent_type not in self.tool_mappings or (operation and operation not in self.tool_mappings[intent_type]):
                return await self._handle_general_query(message, context)
            
            # Get tool mapping
            if operation:
                tool_mapping = self.tool_mappings[intent_type][operation]
            else:
                # For product search, default to search
                tool_mapping = list(self.tool_mappings[intent_type].values())[0]
            
            # Extract parameters from message
            extracted_params = await self._extract_parameters(message, tool_mapping, intent_params)
            extracted_params["user_id"] = user_id
            
            # Check if all required parameters are present
            missing_params = [p for p in tool_mapping.required_params if p not in extracted_params or not extracted_params[p]]
            
            if missing_params:
                return await self._request_missing_parameters(tool_mapping.tool_name, missing_params, extracted_params)
            
            # Execute the tool
            result = await self._execute_tool(tool_mapping.tool_name, extracted_params)
            
            # Format the response
            return await self._format_response(tool_mapping.tool_name, result, extracted_params)
            
        except Exception as e:
            import traceback
            print(f"ERROR in route_message: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "message": "I encountered an error while processing your request. Please try again."
            }
    
    async def _extract_parameters(self, message: str, tool_mapping: ToolMapping, intent_params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract parameters from the message using custom extractors"""
        extracted = {}
        
        # First, use any parameters from intent analysis
        # Convert camelCase to snake_case for consistency
        for key, value in intent_params.items():
            # Convert itemId to item_id, orderId to order_id, etc.
            snake_key = re.sub(r'([a-z])([A-Z])', r'\1_\2', key).lower()
            extracted[snake_key] = value
        
        # Then use custom extractors for missing parameters
        for param, extractor in tool_mapping.param_extractors.items():
            if param not in extracted or not extracted[param]:
                value = extractor(message)
                if value:
                    extracted[param] = value
        
        return extracted
    
    def _extract_item_id(self, message: str) -> Optional[str]:
        """Extract item ID from message"""
        # Look for patterns like "item EST-1", "product EST-1", "EST-1"
        patterns = [
            r'item\s+([A-Z]{2,}-\d+)',
            r'product\s+([A-Z]{2,}-\d+)',
            r'([A-Z]{2,}-\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        return None
    
    def _extract_quantity(self, message: str) -> int:
        """Extract quantity from message"""
        # Look for number patterns
        patterns = [
            r'(\d+)\s+(?:items?|pieces?|units?)',
            r'quantity\s+(?:of\s+)?(\d+)',
            r'add\s+(\d+)',
            r'(\d+)\s+(?:of|to)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        # Default to 1 if no quantity specified
        return 1
    
    def _extract_species(self, message: str) -> Optional[str]:
        """Extract pet species from message"""
        species_keywords = {
            "dog": ["dog", "puppy", "canine", "pup"],
            "cat": ["cat", "kitten", "feline", "kitty"],
            "fish": ["fish", "goldfish", "tropical fish", "aquarium"],
            "bird": ["bird", "parrot", "canary", "parakeet"],
            "reptile": ["reptile", "snake", "lizard", "turtle", "iguana"]
        }
        
        message_lower = message.lower()
        for species, keywords in species_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return species
        return None
    
    def _extract_breed(self, message: str) -> Optional[str]:
        """Extract breed from message"""
        # Common breed patterns
        breed_patterns = [
            r'(?:breed|type)\s+(?:is\s+)?([a-zA-Z\s]+?)(?:\s+(?:dog|cat|fish|bird|reptile))?',
            r'([a-zA-Z\s]+?)\s+(?:breed|type)',
            r'(?:about|for)\s+(?:a\s+)?([a-zA-Z\s]+?)(?:\s+(?:dog|cat|fish|bird|reptile))?'
        ]
        
        for pattern in breed_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                breed = match.group(1).strip()
                # Filter out common words that aren't breeds
                if breed.lower() not in ['the', 'a', 'an', 'my', 'our', 'their']:
                    return breed.title()
        
        # Look for specific breed names
        common_breeds = [
            "labrador", "golden retriever", "german shepherd", "bulldog", "poodle",
            "persian", "siamese", "maine coon", "ragdoll", "british shorthair",
            "goldfish", "betta", "angelfish", "guppy", "tetra"
        ]
        
        message_lower = message.lower()
        for breed in common_breeds:
            if breed in message_lower:
                return breed.title()
        
        return None
    
    def _extract_age(self, message: str) -> Optional[str]:
        """Extract age category from message"""
        age_patterns = {
            "puppy": ["puppy", "puppies", "young dog"],
            "kitten": ["kitten", "kittens", "young cat"],
            "adult": ["adult", "grown", "mature"],
            "senior": ["senior", "old", "elderly", "aged"],
            "young": ["young", "baby", "juvenile"],
        }
        
        message_lower = message.lower()
        for age_category, keywords in age_patterns.items():
            if any(keyword in message_lower for keyword in keywords):
                return age_category
        
        # Look for specific age mentions
        age_match = re.search(r'(\d+)\s*(?:year|month|week)s?\s*old', message_lower)
        if age_match:
            age_num = int(age_match.group(1))
            unit = "year" if "year" in age_match.group(0) else ("month" if "month" in age_match.group(0) else "week")
            
            if unit == "year":
                if age_num < 1:
                    return "young"
                elif age_num < 7:
                    return "adult"
                else:
                    return "senior"
            elif unit == "month":
                if age_num < 12:
                    return "young"
                else:
                    return "adult"
        
        return None
    
    def _extract_weight(self, message: str) -> Optional[float]:
        """Extract weight from message"""
        weight_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:kg|kilogram)',
            r'(\d+(?:\.\d+)?)\s*(?:lb|pound)',
            r'weighs?\s+(\d+(?:\.\d+)?)'
        ]
        
        for pattern in weight_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                weight = float(match.group(1))
                # Convert pounds to kg if needed
                if 'lb' in match.group(0).lower() or 'pound' in match.group(0).lower():
                    weight = weight * 0.453592
                return weight
        return None
    
    def _extract_activity_level(self, message: str) -> Optional[str]:
        """Extract activity level from message"""
        activity_levels = {
            "low": ["low", "sedentary", "inactive", "lazy", "couch"],
            "moderate": ["moderate", "normal", "average", "regular"],
            "high": ["high", "active", "energetic", "athletic", "working"]
        }
        
        message_lower = message.lower()
        for level, keywords in activity_levels.items():
            if any(keyword in message_lower for keyword in keywords):
                return level
        return None
    
    def _extract_search_query(self, message: str) -> str:
        """Extract search query from message"""
        # Remove common search phrases
        search_phrases = [
            "search for", "find", "show me", "looking for", "i want", "i need",
            "can you find", "please find", "search", "products for", "items for"
        ]
        
        query = message.lower()
        for phrase in search_phrases:
            query = query.replace(phrase, "")
        
        # Clean up the query
        query = " ".join(query.split())
        return query.strip()
    
    def _extract_category(self, message: str) -> Optional[str]:
        """Extract product category from message"""
        categories = {
            "food": ["food", "feed", "nutrition", "diet"],
            "toys": ["toy", "toys", "play", "entertainment"],
            "accessories": ["accessories", "accessory", "collar", "leash", "bowl"],
            "health": ["health", "medicine", "medication", "vitamin", "supplement"],
            "grooming": ["grooming", "groom", "shampoo", "brush", "nail"]
        }
        
        message_lower = message.lower()
        for category, keywords in categories.items():
            if any(keyword in message_lower for keyword in keywords):
                return category
        return None
    
    def _extract_order_id(self, message: str) -> Optional[str]:
        """Extract order ID from message"""
        # Look for order ID patterns
        patterns = [
            r'order\s+#?(\d+)',
            r'#(\d+)',
            r'order\s+(?:number|id)\s+(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    async def _execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Execute the specified tool with parameters"""
        # Map tool names to actual functions
        tool_functions = {
            "add_to_cart": self.cart_ops.add_to_cart,
            "view_cart": self.cart_ops.view_cart,
            "remove_from_cart": self.cart_ops.remove_from_cart,
            "update_cart": self.cart_ops.update_cart_item,
            "get_breed_info": self.pet_knowledge.get_breed_info,
            "get_health_conditions": self.pet_knowledge.get_health_conditions,
            "get_nutrition_guide": self.pet_knowledge.get_nutrition_guide,
            "search_products": self.product_search.search_products,
            "create_order": self.order_mgmt.create_order,
            "check_order_status": self.order_mgmt.get_order_status
        }
        
        if tool_name not in tool_functions:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        # Get the function and filter parameters
        func = tool_functions[tool_name]
        
        # Get the function signature to know which parameters to pass
        import inspect
        sig = inspect.signature(func)
        expected_params = set(sig.parameters.keys())
        
        # Filter out None values and only include parameters the function expects
        filtered_params = {
            k: v for k, v in params.items() 
            if v is not None and k in expected_params
        }
        
        # Execute the function
        return await func(**filtered_params)
    
    async def _handle_general_query(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle general queries using AI chat"""
        try:
            # Create a system message with context about available tools
            system_message = """You are a helpful pet store assistant. You can help users with:
            1. Shopping cart operations (add items, view cart, checkout)
            2. Pet information (breeds, health, nutrition, care)
            3. Product search and recommendations
            4. Order management and tracking
            
            Provide helpful, friendly responses and guide users on how to use these features."""
            
            response = await self.openrouter.chat(
                model="anthropic/claude-3-haiku",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": message}
                ],
                context=context
            )
            
            return {
                "success": True,
                "type": "general_response",
                "message": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "I'm here to help! You can ask me about pet products, pet care information, or manage your shopping cart."
            }
    
    async def _request_missing_parameters(self, tool_name: str, missing_params: List[str], current_params: Dict[str, Any]) -> Dict[str, Any]:
        """Request missing parameters from the user"""
        param_questions = {
            "item_id": "Which item would you like to add? Please provide the item ID (e.g., EST-1).",
            "quantity": "How many would you like?",
            "species": "What type of pet is this for? (dog, cat, fish, bird, or reptile)",
            "breed": "What breed are you interested in?",
            "age": "What is the age of your pet? (puppy/kitten, adult, or senior)",
            "weight": "What is your pet's weight in kg?",
            "activity_level": "What is your pet's activity level? (low, moderate, or high)",
            "order_id": "What is your order number?",
            "query": "What would you like to search for?"
        }
        
        questions = []
        for param in missing_params:
            if param in param_questions:
                questions.append(param_questions[param])
            else:
                questions.append(f"Please provide {param.replace('_', ' ')}")
        
        return {
            "success": False,
            "type": "missing_parameters",
            "missing": missing_params,
            "current_params": current_params,
            "tool_name": tool_name,
            "message": "I need a bit more information to help you:\n" + "\n".join(f"• {q}" for q in questions)
        }
    
    async def _format_response(self, tool_name: str, result: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """Format the tool execution result into a user-friendly response"""
        try:
            # Generate a natural language response based on the tool and result
            prompt = f"""Format this {tool_name} result into a friendly response:
            Tool: {tool_name}
            Parameters: {json.dumps(params)}
            Result: {json.dumps(result)}
            
            Make it conversational and helpful. If it's a list, format it nicely.
            If there's an error, explain it clearly and suggest what to do."""
            
            formatted_message = await self.openrouter.chat(
                model="anthropic/claude-3-haiku",
                messages=[
                    {"role": "system", "content": "You are a friendly pet store assistant. Format responses to be helpful and conversational."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                "success": True,
                "type": "tool_result",
                "tool_name": tool_name,
                "result": result,
                "message": formatted_message
            }
        except Exception:
            # Fallback to simple formatting
            return {
                "success": True,
                "type": "tool_result", 
                "tool_name": tool_name,
                "result": result,
                "message": self._simple_format_response(tool_name, result)
            }
    
    def _simple_format_response(self, tool_name: str, result: Any) -> str:
        """Simple response formatting as fallback"""
        if tool_name == "view_cart":
            if isinstance(result, dict) and "items" in result:
                items = result["items"]
                if not items:
                    return "Your cart is currently empty."
                return f"Your cart contains {len(items)} item(s):\n" + \
                       "\n".join(f"• {item.get('name', 'Unknown')} - Quantity: {item.get('quantity', 1)}" for item in items)
        
        elif tool_name == "add_to_cart":
            return "Item successfully added to your cart!"
        
        elif tool_name == "search_products":
            if isinstance(result, list):
                if not result:
                    return "No products found matching your search."
                return f"Found {len(result)} product(s):\n" + \
                       "\n".join(f"• {p.get('name', 'Unknown')} - ${p.get('price', 'N/A')}" for p in result[:5])
        
        # Default response
        return f"Operation completed successfully: {json.dumps(result, indent=2)}"
