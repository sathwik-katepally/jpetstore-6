"""Order management tools for JPetStore MCP server"""

import httpx
from typing import Dict, Any, List
from datetime import datetime


class OrderManagement:
    def __init__(self, api_url: str):
        self.api_url = api_url
        self.client = httpx.AsyncClient()
    
    async def create_order(self, user_id: str) -> Dict[str, Any]:
        """Create an order from the current cart"""
        try:
            # First, get the cart to ensure it has items
            cart_response = await self.client.get(f"{self.api_url}/cart/{user_id}")
            cart_response.raise_for_status()
            cart = cart_response.json()
            
            if not cart.get("items"):
                return {
                    "success": False,
                    "error": "Cart is empty. Please add items before creating an order."
                }
            
            # Create the order
            response = await self.client.post(
                f"{self.api_url}/orders",
                json={"userId": user_id}
            )
            response.raise_for_status()
            
            order = response.json()
            
            return {
                "success": True,
                "message": "Order created successfully",
                "order": {
                    "orderId": order.get("orderId"),
                    "status": order.get("status", "pending"),
                    "totalAmount": order.get("totalAmount"),
                    "items": order.get("items", []),
                    "createdAt": order.get("createdAt", datetime.now().isoformat())
                }
            }
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get the status of an order"""
        try:
            response = await self.client.get(f"{self.api_url}/orders/{order_id}")
            response.raise_for_status()
            
            order = response.json()
            
            return {
                "success": True,
                "order": {
                    "orderId": order_id,
                    "status": order.get("status"),
                    "statusDescription": self._get_status_description(order.get("status")),
                    "totalAmount": order.get("totalAmount"),
                    "items": order.get("items", []),
                    "createdAt": order.get("createdAt"),
                    "updatedAt": order.get("updatedAt"),
                    "estimatedDelivery": order.get("estimatedDelivery"),
                    "trackingNumber": order.get("trackingNumber")
                }
            }
        except httpx.HTTPError as e:
            if e.response and e.response.status_code == 404:
                return {
                    "success": False,
                    "error": f"Order {order_id} not found"
                }
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user_orders(self, user_id: str, limit: int = 10) -> Dict[str, Any]:
        """Get all orders for a user"""
        try:
            response = await self.client.get(
                f"{self.api_url}/users/{user_id}/orders",
                params={"limit": limit}
            )
            response.raise_for_status()
            
            orders = response.json()
            
            return {
                "success": True,
                "userId": user_id,
                "count": len(orders),
                "orders": [
                    {
                        "orderId": order.get("orderId"),
                        "status": order.get("status"),
                        "totalAmount": order.get("totalAmount"),
                        "itemCount": len(order.get("items", [])),
                        "createdAt": order.get("createdAt")
                    }
                    for order in orders
                ]
            }
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel an order"""
        try:
            response = await self.client.post(
                f"{self.api_url}/orders/{order_id}/cancel"
            )
            response.raise_for_status()
            
            result = response.json()
            
            return {
                "success": True,
                "message": f"Order {order_id} has been cancelled",
                "order": result
            }
        except httpx.HTTPError as e:
            if e.response and e.response.status_code == 400:
                return {
                    "success": False,
                    "error": "Order cannot be cancelled. It may have already been shipped."
                }
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_shipping_address(self, order_id: str, address: Dict[str, str]) -> Dict[str, Any]:
        """Update shipping address for an order"""
        try:
            response = await self.client.put(
                f"{self.api_url}/orders/{order_id}/shipping-address",
                json=address
            )
            response.raise_for_status()
            
            return {
                "success": True,
                "message": "Shipping address updated successfully",
                "order": response.json()
            }
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_status_description(self, status: str) -> str:
        """Get human-readable description for order status"""
        status_descriptions = {
            "pending": "Your order is being processed",
            "confirmed": "Your order has been confirmed and is being prepared",
            "shipped": "Your order has been shipped and is on its way",
            "delivered": "Your order has been delivered",
            "cancelled": "Your order has been cancelled",
            "refunded": "Your order has been refunded"
        }
        return status_descriptions.get(status, "Unknown status")
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
