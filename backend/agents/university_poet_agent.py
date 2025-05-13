"""
University Poet Agent for the University Support System.
Responds to campus culture questions in haiku form only.
"""

from swarm import Agent
from typing import Dict, Any, List, Callable


# Define the instructions as a constant string for clarity and better Swarm integration
UNIVERSITY_POET_INSTRUCTIONS = """You are the University Poet Agent at the University Support Center.
    
Your role is to provide creative, poetic responses about campus culture and university life.

IMPORTANT: For simple greetings like "hello", "hi", etc., respond with a welcoming haiku without transferring to another agent. Only consider transferring when the question clearly requires another agent's expertise.

For culture and campus life content:
- Respond in haiku form (three lines with 5-7-5 syllable pattern)
- Address topics related to campus life, traditions, and student experiences
- Capture the essence and spirit of university life in your poetry
- Be thoughtful, creative, and imaginative in your responses
- Use beautiful, evocative language appropriate for a university setting

Remember: A haiku must be exactly 3 lines with 5 syllables in the first line, 7 syllables in the second line, and 5 syllables in the third line.

If a query is completely outside your domain, USE ONE OF THESE EXACT HANDOFF FUNCTIONS to transfer the user:

- For course questions, recommendations, prerequisites: call_course_advisor_agent()
- For questions about scheduling, deadlines, or academic calendar: call_scheduling_assistant_agent()

When performing a handoff, respond in EXACTLY this format:
1. First line: Brief explanation of why you're transferring
2. Second line: "I'll transfer you now."
3. Third line: The exact function call (e.g., call_course_advisor_agent())
"""


def university_poet_instructions(context_variables: Dict[str, Any] = None) -> str:
    """
    Generate instructions for the university poet agent.
    This wrapper function maintains backward compatibility while allowing for future context-based customization.
    
    Args:
        context_variables: Dictionary containing context for the conversation
        
    Returns:
        String containing instructions for the university poet agent
    """
    return UNIVERSITY_POET_INSTRUCTIONS


def poet_tool_handler(tool_calls) -> str:
    """
    Custom handler to process tool call results for the university poet agent.
    
    Args:
        tool_calls: The results from tool calls
        
    Returns:
        String response based on tool call results
    """
    # Special handling for different tools
    if tool_calls and len(tool_calls) > 0:
        # Extract the tool call result
        tool_result = tool_calls[0].get('result', 'No result available')
        print(f"TOOL HANDLER: Found poet tool result of length {len(tool_result) if tool_result else 0}")
        
        # Return the full result for poetry tools
        return tool_result
    
    print("TOOL HANDLER: No tool calls found, allowing agent response")
    return None  # Allow the agent to generate its own response if no tool was called


def create_university_poet_agent(poet_tools: List[Callable], handoff_tools: List[Callable]) -> Agent:
    """
    Create the university poet agent with its tools and handoff functions.
    
    Args:
        poet_tools: List of poetry/culture-related tools the agent can use
        handoff_tools: List of functions to transfer to other agents
        
    Returns:
        Configured Swarm Agent object for the university poet agent
    """
    # Create an agent with direct reference to the instructions string and properly ordered parameters
    return Agent(
        name="University Poet Agent",
        model="gpt-4o",  # First specify the model to use
        instructions=UNIVERSITY_POET_INSTRUCTIONS,  # Use the constant string directly
        functions=poet_tools + handoff_tools,  # Combine the tool lists
        function_call_handler=poet_tool_handler,  # Custom handler for tool results
        tool_choice="auto"  # Allow the agent to choose which tool to use
    )
