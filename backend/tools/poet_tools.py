"""
Poetry tools for the University Poet Agent to generate poetry about campus locations and traditions.

This module now uses semantic vector embeddings for more natural language understanding.
"""

from typing import Dict, Any, List, Optional, Tuple
import random
import os
import numpy as np
from utils.embedding_utils import EmbeddingIndex

# Sample campus locations and their poetic descriptions
CAMPUS_LOCATIONS = {
    "library": {
        "description": "Vast halls of knowledge with towering shelves and quiet study nooks",
        "themes": ["knowledge", "silence", "focus", "books", "learning", "discovery"]
    },
    "quad": {
        "description": "Open grassy area surrounded by academic buildings and pathways",
        "themes": ["nature", "community", "relaxation", "seasons", "gathering", "sunshine"]
    },
    "student center": {
        "description": "Buzzing hub of activity with lounges, food, and meeting spaces",
        "themes": ["community", "energy", "friendship", "food", "activity", "conversation"]
    },
    "cafeteria": {
        "description": "Lively space filled with aromas, conversations, and diverse cuisines",
        "themes": ["food", "community", "diversity", "energy", "sustenance", "gathering"]
    },
    "dormitory": {
        "description": "Homely buildings where students build community and memories",
        "themes": ["home", "friendship", "growth", "late nights", "community", "memories"]
    },
    "lecture hall": {
        "description": "Tiered seating facing a podium where knowledge is shared",
        "themes": ["learning", "wisdom", "attention", "enlightenment", "notes", "questions"]
    },
    "laboratory": {
        "description": "Room filled with equipment where discovery and experimentation happen",
        "themes": ["discovery", "curiosity", "science", "exploration", "precision", "breakthrough"]
    },
    "sports field": {
        "description": "Open area where athletic achievement and team spirit flourish",
        "themes": ["competition", "teamwork", "strength", "victory", "determination", "fitness"]
    },
    "art studio": {
        "description": "Creative space filled with colors, textures, and artistic expression",
        "themes": ["creativity", "expression", "beauty", "inspiration", "color", "perspective"]
    },
    "campus garden": {
        "description": "Tranquil green space with seasonal blooms and quiet contemplation spots",
        "themes": ["nature", "peace", "growth", "beauty", "seasons", "reflection"]
    }
}

# Sample university traditions and events
UNIVERSITY_TRADITIONS = {
    "freshman orientation": {
        "description": "Week-long introduction to university life for new students",
        "themes": ["beginnings", "community", "excitement", "nervousness", "potential"]
    },
    "graduation ceremony": {
        "description": "Formal celebration of academic achievement and transition",
        "themes": ["accomplishment", "endings", "beginnings", "pride", "transition"]
    },
    "homecoming": {
        "description": "Annual celebration welcoming alumni back to campus",
        "themes": ["tradition", "community", "celebration", "nostalgia", "school spirit"]
    },
    "final exams": {
        "description": "Intensive period of academic assessment and late-night studying",
        "themes": ["stress", "determination", "knowledge", "caffeine", "focus"]
    },
    "spring break": {
        "description": "Week-long pause in academic calendar for rest and rejuvenation",
        "themes": ["freedom", "relaxation", "adventure", "escape", "sunshine"]
    },
    "campus concert": {
        "description": "Musical performances that bring the campus community together",
        "themes": ["music", "unity", "expression", "energy", "memory-making"]
    },
    "midnight breakfast": {
        "description": "Late-night meal served by faculty during finals week",
        "themes": ["comfort", "support", "community", "stress relief", "unexpected joy"]
    },
    "research symposium": {
        "description": "Event where students present original research and discoveries",
        "themes": ["discovery", "achievement", "knowledge", "presentation", "pride"]
    }
}

# Sample haiku templates with placeholders
HAIKU_TEMPLATES = [
    [
        "{theme} awaits",
        "Knowledge {verb} like {noun}",
        "{season} {verb}s all"
    ],
    [
        "{noun}s gently {verb}",
        "{adjective} {location} views",
        "{theme} finds its way"
    ],
    [
        "{season} on campus",
        "{noun}s {verb} through {location}",
        "Wisdom takes new form"
    ],
    [
        "Minds seek {theme} here",
        "{adjective} thoughts {verb} freely",
        "Learning never ends"
    ],
    [
        "{location} dreams",
        "{adjective} {noun}s unite us",
        "{theme} guides our path"
    ]
]

# Word banks for haiku generation
HAIKU_WORDS = {
    "noun": ["leaf", "book", "thought", "dream", "path", "mind", "friend", "light", "pen", "star", 
             "word", "bell", "tree", "bird", "wind", "note", "page", "hope", "dawn", "dusk"],
    "verb": ["flows", "drifts", "glows", "grows", "sings", "flies", "turns", "blooms", "shines", 
             "sparks", "writes", "reads", "learns", "seeks", "finds", "shares", "guides", "dreams"],
    "adjective": ["quiet", "bright", "wise", "deep", "swift", "warm", "cool", "keen", "bold", 
                 "soft", "clear", "fresh", "gentle", "eager", "hopeful", "thoughtful", "curious"],
    "season": ["autumn", "winter", "spring", "summer", "morning", "evening", "daybreak", "twilight"],
    "theme": ["wisdom", "growth", "friendship", "learning", "discovery", "courage", "harmony", 
              "balance", "truth", "knowledge", "creativity", "wonder", "insight", "connection"]
}

# Initialize our embedding indices
_location_index = None
_tradition_index = None

def _get_location_index():
    """Get or initialize the location embedding index"""
    global _location_index
    
    if _location_index is None:
        _location_index = EmbeddingIndex("campus_locations", cache_dir="/tmp")
        
        # Create items for embedding
        location_items = []
        for name, location in CAMPUS_LOCATIONS.items():
            # Create a rich text representation
            text = f"{name}: {location['description']}. Themes: {', '.join(location['themes'])}"
            
            item = {
                'id': name,
                'text': text,
                'location': location,
                'name': name,
                'type': 'location'
            }
            location_items.append(item)
            
        # Create embeddings
        _location_index.load_or_create(location_items, text_key='text', id_key='id', force_rebuild=True)
    
    return _location_index

def _get_tradition_index():
    """Get or initialize the tradition embedding index"""
    global _tradition_index
    
    if _tradition_index is None:
        _tradition_index = EmbeddingIndex("university_traditions", cache_dir="/tmp")
        
        # Create items for embedding
        tradition_items = []
        for name, tradition in UNIVERSITY_TRADITIONS.items():
            # Create a rich text representation
            text = f"{name}: {tradition['description']}. Themes: {', '.join(tradition['themes'])}"
            
            item = {
                'id': name,
                'text': text,
                'tradition': tradition,
                'name': name,
                'type': 'tradition'
            }
            tradition_items.append(item)
            
        # Create embeddings
        _tradition_index.load_or_create(tradition_items, text_key='text', id_key='id', force_rebuild=True)
    
    return _tradition_index

def _search_all_indices(query: str, top_k: int = 1) -> Optional[Tuple[Dict[str, Any], float]]:
    """Search across all indices and return the best match"""
    location_index = _get_location_index()
    tradition_index = _get_tradition_index()
    
    # Search both indices
    location_results = location_index.search(query, top_k=top_k, threshold=0.4)
    tradition_results = tradition_index.search(query, top_k=top_k, threshold=0.4)
    
    # Combine results
    all_results = location_results + tradition_results
    
    # Sort by similarity score
    all_results.sort(key=lambda x: x[1], reverse=True)
    
    # Return the best match if any
    return all_results[0] if all_results else None

def get_poetry_inspiration(topic: str) -> str:
    """
    Get poetic inspiration about a campus location or tradition using semantic search.
    
    Args:
        topic: The topic to get inspiration about
        
    Returns:
        String with poetic description and themes
    """
    # Use semantic search to find the best match
    result = _search_all_indices(topic)
    
    if not result:
        return f"I don't have specific inspiration for '{topic}'. Would you like me to write about another campus location or tradition instead?"
    
    item, score = result
    
    if item['type'] == 'location':
        location = item['location']
        return f"Inspiration for {item['name']} (match: {score:.2f}):\n{location['description']}\n\nThemes: {', '.join(location['themes'])}"
    else:  # tradition
        tradition = item['tradition']
        return f"Inspiration for {item['name']} (match: {score:.2f}):\n{tradition['description']}\n\nThemes: {', '.join(tradition['themes'])}"

def generate_haiku(topic: str) -> str:
    """
    Generate a haiku about a university topic using semantic matching.
    
    Args:
        topic: The topic for the haiku
        
    Returns:
        String with the generated haiku
    """
    # Use semantic search to find the best match
    result = _search_all_indices(topic)
    
    # Variables to store themes for haiku generation
    themes = []
    matched_name = topic  # default to the original topic
    
    if result:
        item, score = result
        matched_name = item['name']
        
        if item['type'] == 'location':
            themes = item['location']['themes']
        else:  # tradition
            themes = item['tradition']['themes']
    
    # If no match or no themes, use generic themes
    if not themes:
        themes = ["learning", "growth", "wisdom", "discovery", "journey"]
    
    # Select random theme and build haiku
    theme = random.choice(themes)
    verbs = ["flows", "grows", "shines", "waits", "breathes"]
    nouns = ["river", "mountain", "wind", "star", "flower"]
    
    template = random.choice(HAIKU_TEMPLATES)
    
    # Fill in the template
    haiku_lines = [
        line.format(
            theme=theme,
            topic=matched_name,
            verb=random.choice(verbs),
            noun=random.choice(nouns)
        ) for line in template
    ]
    
    return "\n".join(haiku_lines)

def generate_random_haiku(context_variables: Dict[str, Any], theme: Optional[str] = None) -> str:
    """
    Generate a random haiku about university life.
    
    Args:
        context_variables: Context variables for the conversation
        theme: Optional theme to focus the haiku on
        
    Returns:
        String with a generated haiku
    """
    # Select a template
    template = random.choice(HAIKU_TEMPLATES)
    
    # Fill in the placeholders
    haiku_lines = []
    
    # If theme is provided, use it; otherwise pick random
    haiku_theme = theme.lower() if theme else random.choice(HAIKU_WORDS["theme"])
    
    # Get a random location
    locations = list(CAMPUS_LOCATIONS.keys())
    location = random.choice(locations)
    
    for line in template:
        # Replace placeholders with random words from appropriate categories
        filled_line = line.format(
            noun=random.choice(HAIKU_WORDS["noun"]),
            verb=random.choice(HAIKU_WORDS["verb"]),
            adjective=random.choice(HAIKU_WORDS["adjective"]),
            season=random.choice(HAIKU_WORDS["season"]),
            theme=haiku_theme,
            location=location
        )
        haiku_lines.append(filled_line)
    
    # Return the complete haiku
    return "\n".join(haiku_lines)


def describe_campus_tradition(context_variables: Dict[str, Any], tradition: str) -> str:
    """
    Describe a university tradition poetically.
    
    Args:
        context_variables: Context variables for the conversation
        tradition: The tradition to describe
        
    Returns:
        String with poetic description of the tradition
    """
    tradition_lower = tradition.lower()
    
    if tradition_lower in UNIVERSITY_TRADITIONS:
        tradition_info = UNIVERSITY_TRADITIONS[tradition_lower]
        themes = tradition_info["themes"]
        
        # Generate three haiku lines about this tradition
        haiku_lines = [
            f"{random.choice(themes)} blooms",
            f"{tradition_info['description'][:7]}...",
            f"Memories remain"
        ]
        
        return "\n".join(haiku_lines)
    
    # If tradition not found, return a generic haiku
    return "Unknown customs speak\nHidden stories of campus\nAsk for what you seek"
