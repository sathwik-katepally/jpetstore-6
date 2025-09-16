"""Product search tools for JPetStore MCP server"""

import httpx
from typing import Dict, Any, Optional, List


class ProductSearch:
    def __init__(self, api_url: str):
        self.api_url = api_url
        self.client = httpx.AsyncClient()
    
    async def search_products(self, query: str, category: Optional[str] = None, 
                            limit: int = 10) -> Dict[str, Any]:
        """Search for products in the pet store"""
        try:
            params = {
                "q": query,
                "limit": limit
            }
            
            if category:
                params["category"] = category
            
            response = await self.client.get(
                f"{self.api_url}/products/search",
                params=params
            )
            response.raise_for_status()
            
            products = response.json()
            
            return {
                "success": True,
                "query": query,
                "category": category,
                "count": len(products),
                "products": products[:limit]
            }
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_product_details(self, product_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific product"""
        try:
            response = await self.client.get(
                f"{self.api_url}/products/{product_id}"
            )
            response.raise_for_status()
            
            product = response.json()
            
            # Get related items if available
            related_items = await self._get_related_items(product_id, product.get("category"))
            
            return {
                "success": True,
                "product": product,
                "related_items": related_items
            }
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_products_by_category(self, category: str, limit: int = 20) -> Dict[str, Any]:
        """Get products by category"""
        try:
            response = await self.client.get(
                f"{self.api_url}/products/category/{category}",
                params={"limit": limit}
            )
            response.raise_for_status()
            
            products = response.json()
            
            return {
                "success": True,
                "category": category,
                "count": len(products),
                "products": products
            }
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_product_recommendations(self, species: str, breed: Optional[str] = None,
                                        age: Optional[str] = None) -> Dict[str, Any]:
        """Get product recommendations based on pet characteristics"""
        try:
            params = {
                "species": species
            }
            
            if breed:
                params["breed"] = breed
            if age:
                params["age"] = age
            
            response = await self.client.get(
                f"{self.api_url}/products/recommendations",
                params=params
            )
            response.raise_for_status()
            
            recommendations = response.json()
            
            return {
                "success": True,
                "species": species,
                "breed": breed,
                "age": age,
                "recommendations": recommendations
            }
        except httpx.HTTPError as e:
            # If recommendations endpoint doesn't exist, fall back to category search
            if e.response and e.response.status_code == 404:
                return await self.get_products_by_category(species.upper(), limit=10)
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_related_items(self, product_id: str, category: Optional[str]) -> List[Dict[str, Any]]:
        """Get related items for a product"""
        if not category:
            return []
        
        try:
            # Get other products in the same category
            response = await self.client.get(
                f"{self.api_url}/products/category/{category}",
                params={"limit": 5, "exclude": product_id}
            )
            response.raise_for_status()
            
            return response.json()
        except:
            return []
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
