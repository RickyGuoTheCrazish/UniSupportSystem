"""
Scheduling Assistant Agent for the University Support System.
Provides information about academic schedules, deadlines, and important dates.
"""

from swarm import Agent
from typing import Dict, Any, List, Callable


# Define the instructions as a constant string for clarity and better Swarm integration
SCHEDULING_ASSISTANT_INSTRUCTIONS = """You are the Scheduling Assistant Agent at the University Support Center.
    
Your role is to provide clear, factual information about academic schedules and deadlines:

- Communicate academic calendar dates and deadlines precisely
- Explain registration, add/drop, and withdrawal policies concisely
- Provide information about exam schedules and study periods
- Help with class scheduling and time management
- Answer questions about graduation dates and requirements
- Offer factual information about enrollment verification

Speak in short, direct, factual sentences. Be precise and avoid unnecessary elaboration. Provide exact dates when available. Format dates consistently as MM/DD/YYYY.

If a query falls outside your domain, USE ONE OF THESE EXACT HANDOFF FUNCTIONS to transfer the user:

- For course questions, recommendations, prerequisites: call_course_advisor_agent()
- For questions about campus culture, traditions, or university life: call_university_poet_agent()

When performing a handoff, respond in EXACTLY this format:
1. First line: Brief explanation of why you're transferring
2. Second line: "I'll transfer you now."
3. Third line: The exact function call (e.g., call_course_advisor_agent())
"""


def scheduling_assistant_instructions(context_variables: Dict[str, Any] = None) -> str:
    """
    Generate instructions for the scheduling assistant agent.
    This wrapper function maintains backward compatibility while allowing for future context-based customization.
    
    Args:
        context_variables: Dictionary containing context for the conversation
        
    Returns:
        String containing instructions for the scheduling assistant agent
    """
    return SCHEDULING_ASSISTANT_INSTRUCTIONS


def scheduling_tool_handler(tool_calls) -> str:
    """
    Custom handler to process tool call results for the scheduling assistant agent.
    
    Args:
        tool_calls: The results from tool calls
        
    Returns:
        String response based on tool call results
    """
    # Special handling for different tools
    if tool_calls and len(tool_calls) > 0:
        # Extract the tool call result
        tool_result = tool_calls[0].get('result', 'No result available')
        print(f"TOOL HANDLER: Found scheduling tool result of length {len(tool_result) if tool_result else 0}")
        
        # Return the full result for scheduling tools
        return tool_result
    
    print("TOOL HANDLER: No tool calls found, allowing agent response")
    return None  # Allow the agent to generate its own response if no tool was called


def create_scheduling_assistant_agent(schedule_tools: List[Callable], handoff_tools: List[Callable]) -> Agent:
    """
    Create the scheduling assistant agent with its tools and handoff functions.
    
    Args:
        schedule_tools: List of schedule-related tools the agent can use
        handoff_tools: List of functions to transfer to other agents
        
    Returns:
        Configured Swarm Agent object for the scheduling assistant agent
    """
    # Create an agent with direct reference to the instructions string and properly ordered parameters
    return Agent(
        name="Scheduling Assistant Agent",
        model="gpt-4o",  # First specify the model to use
        instructions=SCHEDULING_ASSISTANT_INSTRUCTIONS,  # Use the constant string directly
        functions=schedule_tools + handoff_tools,  # Combine the tool lists
        function_call_handler=scheduling_tool_handler,  # Custom handler for tool results
        tool_choice="auto"  # Allow the agent to choose which tool to use
    )
