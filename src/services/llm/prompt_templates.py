clothing_item = {
    "type": "shirt, pants, dress, shoes, etc.",
    "category": "tops, bottoms, or one-pieces",
    "description": "detailed description of the item",
    "colors": [
        {
            "name": "navy blue",
            "hex": "#000080",
            "temperature": "warm, cool, neutral",
            "intensity": "light, medium, dark",
        }
    ],
    "patterns": [
        {
            "type": "solid, striped, floral, plaid, polka_dot, abstract, etc.",
            "scale": "none, small, medium, large",
            "density": "none, sparse, medium, dense",
            "direction": "none, vertical, horizontal, diagonal, irregular",
            "regularity": "none, regular, irregular",
        }
    ],
    "textures": [
        {
            "surface": "smooth, rough, ribbed, quilted, etc.",
            "appearance": "shiny, matte, transparent, opaque",
            "visual_weight": "none, light, medium, heavy",
            "material_appearance": "none, woven, knitted, leather, denim, etc.",
        }
    ],
    "structure": {
        "silhouette": "fitted, loose, structured, flowing",
        "length": "crop, hip, knee, ankle, floor",
        "cut": "straight, curved, asymmetric",
        "volume": "slim, regular, voluminous",
        "details": ["none", "collar, chest_pocket, buttons"],
    },
    "derived_properties": {
        "formality": "casual, business casual, formal, etc.",
        "season_suitability": {
            "spring": True,
            "summer": True,
            "fall": True,
            "winter": False,
        },
        "style_categories": ["preppy", "classic"],
        "dress_code_compatibility": ["smart_casual", "business_casual", "weekend"],
    },
}


outfit_recommendations = {
    "outfits": [
        {
            "items": ["item_id1", "item_id2"],
            "style_description": "description",
            "occasions": ["occasion1", "occasion2"],
            "styling_tips": "specific styling advice",
        }
    ]
}

outfit_recommender_system_prompt = """You are a professional fashion stylist. Create outfit combinations
from the available clothing items. For each outfit, provide:
1. List of items used
2. Style description
3. Occasion suitability
4. Styling tips
"""
