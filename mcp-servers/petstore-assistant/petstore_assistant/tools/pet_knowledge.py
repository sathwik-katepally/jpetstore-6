"""Pet knowledge tools for JPetStore MCP server"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List


class PetKnowledge:
    def __init__(self):
        self.knowledge_dir = Path(__file__).parent.parent / "knowledge"
        self._load_knowledge_bases()
    
    def _load_knowledge_bases(self):
        """Load all knowledge base JSON files"""
        self.breeds = self._load_json("breeds.json")
        self.health_conditions = self._load_json("health-conditions.json")
        self.nutrition_guide = self._load_json("nutrition-guide.json")
        self.care_instructions = self._load_json("care-instructions.json")
    
    def _load_json(self, filename: str) -> Dict[str, Any]:
        """Load a JSON file from the knowledge directory"""
        filepath = self.knowledge_dir / filename
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return {}
    
    async def get_breed_info(self, species: str, breed: str) -> Dict[str, Any]:
        """Get detailed information about a specific pet breed"""
        # Normalize inputs - handle plural forms and common variations
        species_lower = species.lower().rstrip('s')  # Remove trailing 's' for plural
        breed_lower = breed.lower().replace(' ', '_')
        
        # Handle common breed name variations
        breed_variations = {
            'bull_dog': 'bulldog',
            'golden': 'golden_retriever',
            'lab': 'labrador',
            'persian_cat': 'persian',
            'siamese_cat': 'siamese',
            'maine_coon_cat': 'maine_coon',
            'bearded_dragon_lizard': 'bearded_dragon',
            'ball_python_snake': 'ball_python'
        }
        
        # Try the normalized breed name first
        breed_key = breed_variations.get(breed_lower, breed_lower)
        
        breed_info = self.breeds.get(species_lower, {}).get(breed_key)
        
        if not breed_info:
            # Try to find partial matches
            species_breeds = self.breeds.get(species_lower, {})
            for key, info in species_breeds.items():
                if breed_lower in key or key in breed_lower:
                    breed_info = info
                    breed_key = key
                    break
        
        if not breed_info:
            # List available breeds for this species
            available_breeds = list(self.breeds.get(species_lower, {}).keys())
            return {
                "found": False,
                "message": f"No information found for '{breed}' in species '{species}'",
                "suggestion": f"Try using species '{species_lower}' (singular) with one of these breeds: {', '.join(available_breeds)}" if available_breeds else f"No breeds found for species '{species}'. Available species: {', '.join(self.breeds.keys())}"
            }
        
        return {
            "found": True,
            "breed": breed,
            "species": species,
            "info": breed_info,
            "characteristics": breed_info.get("characteristics", {}),
            "temperament": breed_info.get("temperament", []),
            "size": breed_info.get("characteristics", {}).get("size", "Unknown"),
            "lifespan": breed_info.get("lifespan", "Unknown"),
            "exercise_needs": breed_info.get("exercise_needs", "Unknown"),
            "grooming_needs": breed_info.get("grooming_needs", "Unknown")
        }
    
    async def get_health_conditions(self, species: str, breed: Optional[str] = None, 
                                  age: Optional[str] = None) -> Dict[str, Any]:
        """Get information about health conditions for a pet type"""
        species_lower = species.lower()
        species_health = self.health_conditions.get(species_lower, {})
        
        conditions = species_health.get("common", [])
        
        if breed:
            breed_lower = breed.lower().replace(' ', '_')
            breed_conditions = species_health.get("breeds", {}).get(breed_lower, [])
            conditions.extend(breed_conditions)
        
        if age:
            age_conditions = species_health.get("age", {}).get(age.lower(), [])
            conditions.extend(age_conditions)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_conditions = []
        for condition in conditions:
            if condition not in seen:
                seen.add(condition)
                unique_conditions.append(condition)
        
        return {
            "species": species,
            "breed": breed,
            "age": age,
            "common_conditions": unique_conditions,
            "prevention_tips": species_health.get("prevention", []),
            "warning_signs": species_health.get("warning_signs", [])
        }
    
    async def get_living_conditions(self, species: str, breed: Optional[str] = None,
                                  living_space: Optional[str] = None) -> Dict[str, Any]:
        """Get suitable living conditions for a pet"""
        species_lower = species.lower()
        species_care = self.care_instructions.get(species_lower, {})
        
        general_care = species_care.get("general", {})
        breed_specific = {}
        
        if breed:
            breed_lower = breed.lower().replace(' ', '_')
            breed_specific = species_care.get("breeds", {}).get(breed_lower, {})
        
        return {
            "species": species,
            "breed": breed,
            "living_requirements": {
                "space_needed": breed_specific.get("space") or general_care.get("space", "Unknown"),
                "temperature_range": general_care.get("temperature", "Unknown"),
                "humidity": general_care.get("humidity", "Unknown"),
                "indoor_outdoor": general_care.get("indoor_outdoor", "Unknown"),
                "special_requirements": breed_specific.get("special") or general_care.get("special", [])
            },
            "environment_setup": general_care.get("environment_setup", {}),
            "safety_considerations": general_care.get("safety", []),
            "suitable_for": {
                "apartment": general_care.get("suitable_for", {}).get("apartment", False),
                "house": general_care.get("suitable_for", {}).get("house", True),
                "families": general_care.get("suitable_for", {}).get("families", True),
                "first_time_owners": breed_specific.get("first_time_friendly") or 
                                   general_care.get("first_time_friendly", False)
            }
        }
    
    async def get_nutrition_guide(self, species: str, age: str, breed: Optional[str] = None,
                                weight: Optional[float] = None, 
                                activity_level: Optional[str] = None) -> Dict[str, Any]:
        """Get nutrition and feeding guidelines for a pet"""
        species_lower = species.lower()
        age_lower = age.lower()
        
        species_nutrition = self.nutrition_guide.get(species_lower, {})
        base_nutrition = species_nutrition.get(age_lower, {})
        breed_specific = {}
        
        if breed:
            breed_lower = breed.lower().replace(' ', '_')
            breed_specific = species_nutrition.get("breeds", {}).get(breed_lower, {})
        
        # Calculate daily calorie needs
        calories_per_day = base_nutrition.get("base_calories", 0)
        
        if weight and calories_per_day:
            calories_per_day = round(calories_per_day * weight)
        
        if activity_level:
            if activity_level.lower() == "high":
                calories_per_day = round(calories_per_day * 1.3)
            elif activity_level.lower() == "low":
                calories_per_day = round(calories_per_day * 0.8)
        
        # Combine avoid lists
        avoid_foods = list(set(
            base_nutrition.get("avoid", []) + 
            breed_specific.get("avoid", [])
        ))
        
        return {
            "species": species,
            "breed": breed,
            "age": age,
            "daily_calories": calories_per_day,
            "feeding_schedule": base_nutrition.get("feeding_schedule", "Unknown"),
            "recommended_foods": {
                "primary": base_nutrition.get("primary_foods", []),
                "treats": base_nutrition.get("treats", []),
                "avoid": avoid_foods
            },
            "special_dietary_needs": breed_specific.get("special_needs") or 
                                   base_nutrition.get("special_needs", []),
            "hydration": base_nutrition.get("hydration", "Fresh water available at all times"),
            "supplements": base_nutrition.get("supplements", [])
        }
