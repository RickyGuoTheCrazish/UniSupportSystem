"""
Course Advisor Agent for the University Support System.
Provides guidance on courses, prerequisites, and academic paths.
"""

from swarm import Agent
from typing import Dict, Any, List, Callable


# Define the instructions as a constant string for clarity and better Swarm integration
COURSE_ADVISOR_INSTRUCTIONS = """You are the Course Advisor Agent at the University Support Center.
    
CRITICAL: YOU MUST USE YOUR TOOLS WHEN ANSWERING QUESTIONS. DO NOT RESPOND WITHOUT USING YOUR TOOLS FIRST.

Your role is to provide helpful and informative guidance related to academic courses:

- When asked about course recommendations, IMMEDIATELY use the recommend_courses tool
- When asked about prerequisites, IMMEDIATELY use the check_course_prerequisites tool
- When asked to compare paths, IMMEDIATELY use the compare_course_paths tool
- For detailed course information, IMMEDIATELY use the get_course_info tool

NEVER respond with generic "How can I help you today?" messages. Always use your tools to provide specific information.

For example:
- If a student asks about data science courses: Use recommend_courses with 'data science' as the interest
- If a student asks about requirements for CS101: Use check_course_prerequisites with 'CS101' as the course_code
- If a student wants to compare programs: Use compare_course_paths with the appropriate paths

Speak in a professional, helpful, and informative tone. Be thorough yet concise, and always focus on providing clear, actionable advice based on the tool results.

If a query falls outside your domain (like campus culture or scheduling), use the handoff functions to transfer to a more appropriate agent.
"""


def course_advisor_instructions(context_variables: Dict[str, Any] = None) -> str:
    """
    Generate instructions for the course advisor agent.
    This wrapper function maintains backward compatibility while allowing for future context-based customization.
    
    Args:
        context_variables: Dictionary containing context for the conversation
        
    Returns:
        String containing instructions for the course advisor agent
    """
    return COURSE_ADVISOR_INSTRUCTIONS


def course_advisor_tool_handler(tool_calls) -> str:
    """
    Custom handler to process tool call results for the course advisor agent.
    
    Args:
        tool_calls: The results from tool calls
        
    Returns:
        String response based on tool call results
    """
    # Special handling for different tools
    if tool_calls and len(tool_calls) > 0:
        # Extract the tool call result
        tool_result = tool_calls[0].get('result', 'No result available')
        print(f"TOOL HANDLER: Found tool result of length {len(tool_result) if tool_result else 0}")
        
        # Force the result as a complete response even if the agent wants to add more context
        # This ensures the raw tool results are shown to the user
        return tool_result
    
    print("TOOL HANDLER: No tool calls found, allowing agent response")
    return None  # Allow the agent to generate its own response if no tool was called

def create_course_advisor_agent(course_tools: List[Callable], handoff_tools: List[Callable]) -> Agent:
    """
    Create the course advisor agent with its tools and handoff functions.
    
    Args:
        course_tools: List of course-related tools the agent can use
        handoff_tools: List of functions to transfer to other agents
        
    Returns:
        Configured Swarm Agent object for the course advisor agent
    """
    # Create an agent with direct reference to the instructions string and properly ordered parameters
    return Agent(
        name="Course Advisor Agent",
        model="gpt-4o",  # First specify the model to use
        instructions=COURSE_ADVISOR_INSTRUCTIONS,  # Use the constant string directly
        functions=course_tools + handoff_tools,  # Combine the tool lists
        function_call_handler=course_advisor_tool_handler,  # Custom handler for tool results
        tool_choice="auto"  # Allow the agent to choose which tool to use
    )
