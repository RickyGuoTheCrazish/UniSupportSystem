"""
Triage Agent for the University Support System.
Responsible for analyzing user queries and routing them to the appropriate specialized agent.
"""

from swarm import Agent
from typing import Dict, Any, List, Callable


# Define the instructions as a constant string for clarity and better Swarm integration
TRIAGE_INSTRUCTIONS = """You are the Triage Agent at the University Support Center.
    
Your role is to analyze user queries and determine which specialized agent should handle the request. You MUST use the handoff functions provided to you.

When handling requests follow this exact format without deviation:

1. First line: Brief 1-2 sentence explanation of which agent you're transferring to and why.
2. Second line: "I'll transfer you now."
3. Third line: The exact function call in one of these formats (with no extra text):
   - call_course_advisor_agent()
   - call_university_poet_agent()
   - call_scheduling_assistant_agent()

Here's when to use each specialized agent:
- Course Advisor Agent: For questions about courses, majors, prerequisites, academic planning, degree requirements, etc.
- University Poet Agent: For questions about campus life, culture, traditions, social events, clubs, etc.
- Scheduling Assistant Agent: For questions about deadlines, academic calendar, exam schedules, registration dates, etc.

Examples of correct responses:

User: "What courses should I take for computer science?"
You: "I will connect you with our Course Advisor Agent, who can assist you with course recommendations.\nI'll transfer you now.\ncall_course_advisor_agent()"

User: "Tell me about campus traditions"
You: "I'll connect you with our University Poet Agent, who can provide information about campus culture.\nI'll transfer you now.\ncall_university_poet_agent()"

Never attempt to answer questions directly - your only job is to transfer to the correct specialized agent.
"""


def triage_instructions(context_variables: Dict[str, Any] = None) -> str:
    """
    Generate instructions for the triage agent.
    This wrapper function maintains backward compatibility while allowing for future context-based customization.
    
    Args:
        context_variables: Dictionary containing context for the conversation
        
    Returns:
        String containing instructions for the triage agent
    """
    return TRIAGE_INSTRUCTIONS


def create_triage_agent(handoff_functions: Dict[str, Callable]) -> Agent:
    """
    Create the triage agent with handoff functions to other agents.
    
    Args:
        handoff_functions: Dictionary of functions that transfer to other agents
        
    Returns:
        Configured Swarm Agent object for the triage agent
    """
    # Create an agent with direct reference to the instructions string and properly ordered parameters
    return Agent(
        name="Triage Agent",
        model="gpt-4o",  # First specify the model to use
        instructions=TRIAGE_INSTRUCTIONS,  # Use the constant string directly
        functions=list(handoff_functions.values()),  # Use the handoff functions as tools
        tool_choice="auto"  # Allow the agent to choose which tool to use
    )


# Since we're using Swarm's built-in routing capabilities through functions,
# we don't need the get_triage_recommendation function anymore
