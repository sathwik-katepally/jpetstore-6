"""Product search tools for JPetStore MCP server"""

import httpx
from typing import Dict, Any, Optional, List


class ProductSearch:
    def __init__(self, api_url: str):
        # Remove /api suffix if present and use /catalog prefix
        self.base_url = api_url.rstrip('/').replace('/api', '')
        self.catalog_url = f"{self.base_url}/catalog"
        self.client = httpx.AsyncClient()
    
    async def search_products(self, query: str, category: Optional[str] = None, 
                            limit: int = 10) -> Dict[str, Any]:
        """Search for products in the pet store"""
        try:
            # Use the catalog search endpoint
            response = await self.client.get(
                f"{self.catalog_url}/products/search",
                params={"keyword": query}
            )
            response.raise_for_status()
            
            products = response.json()
            
            # Filter by category if specified
            if category and products:
                products = [p for p in products if p.get('category', '').lower() == category.lower()]
            
            # Apply limit
            products = products[:limit] if products else []
            
            return {
                "success": True,
                "query": query,
                "category": category,
                "count": len(products),
                "products": products
            }
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_product_details(self, product_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific product"""
        try:
            # Get product details
            response = await self.client.get(
                f"{self.catalog_url}/products/{product_id}"
            )
            response.raise_for_status()
            
            product = response.json()
            
            # Get items for this product
            items_response = await self.client.get(
                f"{self.catalog_url}/products/{product_id}/items"
            )
            items_response.raise_for_status()
            items = items_response.json()
            
            # Get related items if available
            related_items = await self._get_related_items(product_id, product.get("categoryId"))
            
            return {
                "success": True,
                "product": product,
                "items": items,
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
            # First get the category ID
            category_id = await self._get_category_id(category)
            if not category_id:
                return {
                    "success": False,
                    "error": f"Category '{category}' not found"
                }
            
            # Get products for this category
            response = await self.client.get(
                f"{self.catalog_url}/categories/{category_id}/products"
            )
            response.raise_for_status()
            
            products = response.json()
            
            # Apply limit
            products = products[:limit] if products else []
            
            return {
                "success": True,
                "category": category,
                "categoryId": category_id,
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
            # Since there's no recommendations endpoint, search for products by species
            # and filter based on breed/age in the results
            products_result = await self.search_products(species)
            
            if not products_result.get("success"):
                return products_result
            
            products = products_result.get("products", [])
            
            # Filter products based on breed and age if provided
            if breed:
                # Try to find products that mention the breed
                breed_products = [p for p in products if breed.lower() in p.get("name", "").lower() 
                                or breed.lower() in p.get("description", "").lower()]
                if breed_products:
                    products = breed_products
            
            if age:
                # Try to find products suitable for the age
                age_keywords = {
                    "puppy": ["puppy", "junior", "young"],
                    "kitten": ["kitten", "junior", "young"],
                    "adult": ["adult", "mature"],
                    "senior": ["senior", "old", "mature"]
                }
                
                if age.lower() in age_keywords:
                    keywords = age_keywords[age.lower()]
                    age_products = []
                    for p in products:
                        for keyword in keywords:
                            if keyword in p.get("name", "").lower() or keyword in p.get("description", "").lower():
                                age_products.append(p)
                                break
                    if age_products:
                        products = age_products
            
            return {
                "success": True,
                "species": species,
                "breed": breed,
                "age": age,
                "recommendations": products[:10]  # Limit to 10 recommendations
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_related_items(self, product_id: str, category_id: Optional[str]) -> List[Dict[str, Any]]:
        """Get related items for a product"""
        if not category_id:
            return []
        
        try:
            # Get other products in the same category
            response = await self.client.get(
                f"{self.catalog_url}/categories/{category_id}/products"
            )
            response.raise_for_status()
            
            products = response.json()
            # Exclude the current product and limit to 5
            related = [p for p in products if p.get("productId") != product_id][:5]
            
            return related
        except:
            return []
    
    async def _get_category_id(self, category_name: str) -> Optional[str]:
        """Get category ID from category name"""
        try:
            # Get all categories
            response = await self.client.get(f"{self.catalog_url}/categories")
            response.raise_for_status()
            
            categories = response.json()
            
            # Find matching category (case-insensitive)
            for cat in categories:
                if cat.get("name", "").lower() == category_name.lower():
                    return cat.get("categoryId")
            
            # Try to match by category ID if it's already an ID
            for cat in categories:
                if cat.get("categoryId", "").lower() == category_name.lower():
                    return cat.get("categoryId")
            
            return None
        except:
            return None
    
    async def get_all_categories(self) -> Dict[str, Any]:
        """Get all available categories"""
        try:
            response = await self.client.get(f"{self.catalog_url}/categories")
            response.raise_for_status()
            
            categories = response.json()
            
            return {
                "success": True,
                "categories": categories
            }
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_item_details(self, item_id: str) -> Dict[str, Any]:
        """Get details for a specific item"""
        try:
            response = await self.client.get(
                f"{self.catalog_url}/items/{item_id}"
            )
            response.raise_for_status()
            
            item = response.json()
            
            return {
                "success": True,
                "item": item
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
