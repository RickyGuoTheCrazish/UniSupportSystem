"""
Course tools for the Course Advisor Agent in the University Support System.
These functions provide course-related information and recommendations.

This module now uses semantic vector embeddings for more flexible matching of course information.
"""

from typing import Dict, Any, List, Optional, Tuple
import random
import os
import numpy as np
from utils.embedding_utils import EmbeddingIndex

# Sample course data - In a real implementation, this would connect to a database
COURSES = {
    "CS101": {
        "title": "Introduction to Computer Science",
        "description": "Fundamentals of programming, algorithms, and computer systems",
        "credits": 3,
        "prerequisites": [],
        "difficulty": "Beginner",
        "topics": ["programming", "algorithms", "computer systems"]
    },
    "CS201": {
        "title": "Data Structures",
        "description": "Implementation and analysis of fundamental data structures",
        "credits": 4,
        "prerequisites": ["CS101"],
        "difficulty": "Intermediate",
        "topics": ["data structures", "algorithms", "efficiency"]
    },
    "DS200": {
        "title": "Introduction to Data Science",
        "description": "Foundations of data analysis, statistics, and machine learning",
        "credits": 3,
        "prerequisites": ["CS101", "MATH150"],
        "difficulty": "Intermediate",
        "topics": ["data analysis", "statistics", "machine learning"]
    },
    "MATH150": {
        "title": "Calculus I",
        "description": "Limits, derivatives, and integrals of single-variable functions",
        "credits": 4,
        "prerequisites": [],
        "difficulty": "Intermediate",
        "topics": ["calculus", "mathematics", "functions"]
    },
    "MATH250": {
        "title": "Linear Algebra",
        "description": "Vector spaces, matrices, and linear transformations",
        "credits": 3,
        "prerequisites": ["MATH150"],
        "difficulty": "Intermediate",
        "topics": ["linear algebra", "matrices", "mathematics"]
    },
    "ENG101": {
        "title": "Academic Writing",
        "description": "Principles of effective academic writing and communication",
        "credits": 3,
        "prerequisites": [],
        "difficulty": "Beginner",
        "topics": ["writing", "communication", "research"]
    },
    "BIO101": {
        "title": "Introduction to Biology",
        "description": "Fundamentals of biological systems and processes",
        "credits": 4,
        "prerequisites": [],
        "difficulty": "Beginner",
        "topics": ["biology", "life sciences", "cells"]
    },
    "PSYCH101": {
        "title": "Introduction to Psychology",
        "description": "Survey of basic principles in psychology and behavior",
        "credits": 3,
        "prerequisites": [],
        "difficulty": "Beginner",
        "topics": ["psychology", "behavior", "mental processes"]
    },
    "AI400": {
        "title": "Advanced Machine Learning",
        "description": "Advanced techniques in machine learning and artificial intelligence",
        "credits": 4,
        "prerequisites": ["CS201", "DS200", "MATH250"],
        "difficulty": "Advanced",
        "topics": ["machine learning", "artificial intelligence", "neural networks"]
    },
    "CS300": {
        "title": "Database Systems",
        "description": "Design and implementation of database management systems",
        "credits": 3,
        "prerequisites": ["CS201"],
        "difficulty": "Intermediate",
        "topics": ["databases", "SQL", "data modeling"]
    },
    "FIN201": {
        "title": "Introduction to Finance",
        "description": "Principles of financial management, investment analysis, and capital markets",
        "credits": 3,
        "prerequisites": ["MATH150"],
        "difficulty": "Intermediate",
        "topics": ["finance", "investment", "capital markets"]
    },
    "FIN301": {
        "title": "Corporate Finance",
        "description": "Analysis of financial decision-making within the firm and its impact on shareholders",
        "credits": 3,
        "prerequisites": ["FIN201"],
        "difficulty": "Advanced",
        "topics": ["finance", "corporate strategy", "valuation"]
    },
    "BUS101": {
        "title": "Introduction to Business",
        "description": "Overview of business principles, management, marketing, and economics",
        "credits": 3,
        "prerequisites": [],
        "difficulty": "Beginner",
        "topics": ["business", "management", "marketing"]
    },
    "BUS220": {
        "title": "Business Analytics",
        "description": "Application of data analysis techniques to business decision-making",
        "credits": 3,
        "prerequisites": ["BUS101", "MATH150"],
        "difficulty": "Intermediate",
        "topics": ["business", "analytics", "decision-making"]
    },
    "ECON101": {
        "title": "Principles of Economics",
        "description": "Introduction to micro and macroeconomic principles and policies",
        "credits": 3,
        "prerequisites": [],
        "difficulty": "Beginner",
        "topics": ["economics", "markets", "policy"]
    }
}

# Sample career paths with recommended courses
CAREER_PATHS = {
    "data science": ["CS101", "MATH150", "DS200", "MATH250", "AI400"],
    "software engineering": ["CS101", "CS201", "MATH150", "CS300"],
    "research": ["CS101", "MATH150", "MATH250", "BIO101", "ENG101"],
    "business analytics": ["BUS220", "CS101", "DS200", "MATH150", "BUS101"],
    "psychology": ["PSYCH101", "BIO101", "ENG101", "DS200"],
    "finance": ["FIN201", "FIN301", "ECON101", "MATH150", "BUS101"],
    "business": ["BUS101", "ECON101", "ENG101", "BUS220"],
    "economics": ["ECON101", "MATH150", "DS200", "FIN201"]
}


def get_course_info(course_code: str) -> dict:
    """
    Get detailed information about a specific course.
    
    Args:
        course_code: The course code (e.g., "CS101")
        
    Returns:
        Dictionary with course information or error message
    """
    course_code = course_code.upper()
    if course_code in COURSES:
        course = COURSES[course_code]
        # Add prerequisite titles
        prereq_info = []
        for prereq in course["prerequisites"]:
            if prereq in COURSES:
                prereq_info.append(f"{prereq}: {COURSES[prereq]['title']}")
            else:
                prereq_info.append(prereq)
        
        return {
            "success": True,
            "course_code": course_code,
            "title": course["title"],
            "description": course["description"],
            "credits": course["credits"],
            "prerequisites": prereq_info,
            "difficulty": course["difficulty"],
            "topics": course["topics"]
        }
    
    return {
        "success": False,
        "error": f"Course {course_code} not found in catalog."
    }


# Initialize course embeddings
_course_index = None

def _get_course_index():
    """Get or initialize the course embedding index"""
    global _course_index
    
    if _course_index is None:
        _course_index = EmbeddingIndex("courses", cache_dir="/tmp")
        
        # Create items for embedding
        course_items = []
        for code, course in COURSES.items():
            # Create a rich text representation that captures all relevant course info
            text = f"{course['title']}. {course['description']}. Topics: {', '.join(course['topics'])}"
            
            item = {
                'id': code,
                'text': text,
                'course': course,
                'code': code
            }
            course_items.append(item)
            
        # Create embeddings
        _course_index.load_or_create(course_items, text_key='text', id_key='id', force_rebuild=True)
    
    return _course_index

def recommend_courses(interest: str, count: int = 3) -> str:
    """
    Recommend courses based on a student's interest using semantic search.
    
    Args:
        interest: The student's interest area (e.g., "data science", "algorithms")
        count: Number of courses to recommend (default: 3)
        
    Returns:
        String with recommended courses information
    """
    print(f"recommend_courses called with interest: {interest}, count: {count}")
    interest = interest.lower()
    
    # Check if interest matches a career path exactly
    if interest in CAREER_PATHS:
        print(f"[COURSE DEBUG] Found exact career path match for '{interest}'")
        path_courses = CAREER_PATHS[interest]
        recommended = path_courses[:count]
        
        result = f"Based on your interest in {interest}, here are some recommended courses:\n\n"
        
        for code in recommended:
            if code in COURSES:
                course = COURSES[code]
                print(f"[COURSE DEBUG] Recommending course: {code}")
                result += f"- {code}: {course['title']}\n  {course['description']}\n  Difficulty: {course['difficulty']}, Credits: {course['credits']}\n\n"
        
        print(f"[COURSE DEBUG] Returning {len(recommended)} recommendations")
        return result
    
    # Try to find partial matches in career paths
    for career_path in CAREER_PATHS:
        if interest.lower() in career_path.lower() or career_path.lower() in interest.lower():
            print(f"[COURSE DEBUG] Found partial career path match for '{interest}' -> '{career_path}'")
            path_courses = CAREER_PATHS[career_path]
            recommended = path_courses[:count]
            
            result = f"Based on your interest in {interest}, here are some recommended courses related to {career_path}:\n\n"
            
            for code in recommended:
                if code in COURSES:
                    course = COURSES[code]
                    print(f"[COURSE DEBUG] Recommending course: {code}")
                    result += f"- {code}: {course['title']}\n  {course['description']}\n  Difficulty: {course['difficulty']}, Credits: {course['credits']}\n\n"
            
            print(f"[COURSE DEBUG] Returning {len(recommended)} recommendations from partial match")
            return result
    
    # Use semantic search to find relevant courses
    print(f"[COURSE DEBUG] No exact or partial match for '{interest}', using semantic search")
    course_index = _get_course_index()
    search_results = course_index.search(
        query=interest,
        top_k=count,
        threshold=0.3  # Lower threshold for more recall
    )
    
    if search_results:
        print(f"[COURSE DEBUG] Semantic search found {len(search_results)} matches")
        # Make the interest term more explicit, especially for biology and specific fields
        if "bio" in interest.lower():
            result = f"Based on your interest in BIOLOGY, here are some recommended courses:\n\n"
        else:
            result = f"Based on your interest in {interest.upper()}, here are some recommended courses:\n\n"
        
        # Include similarity scores for debugging
        for item, score in search_results:
            code = item['code']
            course = item['course']
            print(f"[COURSE DEBUG] Recommending course: {code} with similarity score: {score:.4f}")
            # Include the interest field in the course description for better matching
            if "bio" in interest.lower() and code == "BIO101":
                result += f"- {code}: {course['title']} (BIOLOGY course, match score: {score:.2f})\n  {course['description']}\n  Difficulty: {course['difficulty']}, Credits: {course['credits']}\n\n"
            else:
                result += f"- {code}: {course['title']} (match: {score:.2f})\n  {course['description']}\n  Difficulty: {course['difficulty']}, Credits: {course['credits']}\n\n"
        
        print(f"[COURSE DEBUG] Returning semantic search results with {len(search_results)} recommendations")
        return result
    
    return f"I couldn't find specific courses for '{interest}'. Would you like recommendations for popular areas like data science, programming, or mathematics instead?"


def compare_course_paths(path1: str, path2: str) -> str:
    """
    Compare two different academic or career paths.
    
    Args:
        path1: First career/academic path to compare
        path2: Second career/academic path to compare
        
    Returns:
        String comparison of the two paths
    """
    print(f"compare_course_paths called with path1: {path1}, path2: {path2}")
    path1 = path1.lower()
    path2 = path2.lower()
    
    # Check if paths exist in career paths
    path1_exists = path1 in CAREER_PATHS
    path2_exists = path2 in CAREER_PATHS
    
    if not path1_exists and not path2_exists:
        return f"I don't have specific information about either '{path1}' or '{path2}' career paths. Would you like to know about our available paths like data science, software engineering, research, business analytics, or psychology?"
    
    if not path1_exists:
        return f"I don't have information about '{path1}'. Would you like to compare '{path2}' with another available path like data science, software engineering, research, business analytics, or psychology?"
    
    if not path2_exists:
        return f"I don't have information about '{path2}'. Would you like to compare '{path1}' with another available path like data science, software engineering, research, business analytics, or psychology?"
    
    # Both paths exist, do the comparison
    path1_courses = CAREER_PATHS[path1]
    path2_courses = CAREER_PATHS[path2]
    
    # Find common courses
    common_courses = set(path1_courses) & set(path2_courses)
    
    # Unique courses for each path
    unique_path1 = set(path1_courses) - set(path2_courses)
    unique_path2 = set(path2_courses) - set(path1_courses)
    
    result = f"Comparison between {path1.title()} and {path2.title()}:\n\n"
    
    # Compare course counts
    result += f"{path1.title()} requires {len(path1_courses)} courses.\n"
    result += f"{path2.title()} requires {len(path2_courses)} courses.\n\n"
    
    # List common courses
    result += f"Common courses ({len(common_courses)}):\n"
    for code in common_courses:
        if code in COURSES:
            result += f"- {code}: {COURSES[code]['title']}\n"
    
    # List unique courses for path1
    result += f"\nCourses unique to {path1.title()} ({len(unique_path1)}):\n"
    for code in unique_path1:
        if code in COURSES:
            result += f"- {code}: {COURSES[code]['title']}\n"
    
    # List unique courses for path2
    result += f"\nCourses unique to {path2.title()} ({len(unique_path2)}):\n"
    for code in unique_path2:
        if code in COURSES:
            result += f"- {code}: {COURSES[code]['title']}\n"
    
    return result


def check_course_prerequisites(course_code: str) -> str:
    """
    Check prerequisites for a specific course.
    
    Args:
        course_code: The course code to check
        
    Returns:
        String with prerequisite information
    """
    course_code = course_code.upper()
    
    if course_code not in COURSES:
        return f"Course {course_code} was not found in the catalog."
    
    course = COURSES[course_code]
    prereqs = course["prerequisites"]
    
    if not prereqs:
        return f"{course_code}: {course['title']} has no prerequisites. It's open to all students."
    
    # Build the prerequisite tree
    result = f"Prerequisites for {course_code}: {course['title']}:\n\n"
    
    for prereq_code in prereqs:
        if prereq_code in COURSES:
            prereq = COURSES[prereq_code]
            result += f"- {prereq_code}: {prereq['title']}\n"
            
            # Check if this prerequisite has its own prerequisites
            if prereq["prerequisites"]:
                result += "  └─ which requires:\n"
                for sub_prereq in prereq["prerequisites"]:
                    if sub_prereq in COURSES:
                        result += f"     - {sub_prereq}: {COURSES[sub_prereq]['title']}\n"
    
    return result
