"""Cart operations tools for JPetStore MCP server"""

import httpx
from typing import Dict, Any, Optional


class CartOperations:
    def __init__(self, api_url: str):
        self.api_url = api_url
        self.client = httpx.AsyncClient()
    
    async def add_to_cart(self, user_id: str, item_id: str, quantity: int) -> Dict[str, Any]:
        """Add an item to the shopping cart"""
        try:
            response = await self.client.post(
                f"{self.api_url}/cart/{user_id}/items",
                json={"itemId": item_id, "quantity": quantity}
            )
            response.raise_for_status()
            
            cart_data = response.json()
            return {
                "success": True,
                "message": f"Added {quantity} item(s) to cart",
                "cart": cart_data
            }
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_cart_item(self, user_id: str, item_id: str, quantity: int) -> Dict[str, Any]:
        """Update quantity of an item in the cart"""
        try:
            if quantity == 0:
                # Remove item if quantity is 0
                return await self.remove_from_cart(user_id, item_id)
            
            response = await self.client.put(
                f"{self.api_url}/cart/{user_id}/items/{item_id}",
                json={"quantity": quantity}
            )
            response.raise_for_status()
            
            cart_data = response.json()
            return {
                "success": True,
                "message": f"Updated quantity to {quantity}",
                "cart": cart_data
            }
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def remove_from_cart(self, user_id: str, item_id: str) -> Dict[str, Any]:
        """Remove an item from the cart"""
        try:
            response = await self.client.delete(
                f"{self.api_url}/cart/{user_id}/items/{item_id}"
            )
            response.raise_for_status()
            
            cart_data = response.json()
            return {
                "success": True,
                "message": "Item removed from cart",
                "cart": cart_data
            }
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def view_cart(self, user_id: str) -> Dict[str, Any]:
        """View current cart contents"""
        try:
            response = await self.client.get(f"{self.api_url}/cart/{user_id}")
            response.raise_for_status()
            
            cart_data = response.json()
            total_items = sum(item.get("quantity", 0) for item in cart_data.get("items", []))
            
            return {
                "success": True,
                "cart": cart_data,
                "summary": {
                    "totalItems": total_items,
                    "totalPrice": cart_data.get("totalPrice", 0)
                }
            }
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
