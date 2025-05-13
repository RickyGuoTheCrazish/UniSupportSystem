"""
Simplified Swarm client for the University Support System.
"""

from swarm import Swarm, Agent
import json
import logging
import traceback
import sys

# Import agent modules with correct create_* functions
from agents.triage_agent import create_triage_agent
from agents.course_advisor_agent import create_course_advisor_agent, course_advisor_tool_handler
from agents.university_poet_agent import create_university_poet_agent
from agents.scheduling_assistant_agent import create_scheduling_assistant_agent

# Import tool modules
from tools.course_tools import recommend_courses, check_course_prerequisites, compare_course_paths, get_course_info

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Swarm client
swarm_client = Swarm()

def get_agent_by_name(agent_name):
    """Returns the appropriate agent based on name."""
    
    # Define actual callable functions for handoffs
    def call_course_advisor_agent():
        """Transfer to the Course Advisor Agent."""
        return "Transferring to Course Advisor Agent"
    
    def call_university_poet_agent():
        """Transfer to the University Poet Agent."""
        return "Transferring to University Poet Agent"
    
    def call_scheduling_assistant_agent():
        """Transfer to the Scheduling Assistant Agent."""
        return "Transferring to Scheduling Assistant Agent"
    
    # Define course tools as actual callable functions
    def recommend_courses_func(interest, count=3):
        """Recommend courses based on student interest."""
        return recommend_courses(interest, count)
    
    def check_prerequisites_func(course_code):
        """Check prerequisites for a course."""
        return check_course_prerequisites(course_code)
    
    def compare_paths_func(path1, path2):
        """Compare two academic paths."""
        return compare_course_paths(path1, path2)
    
    def get_course_info_func(course_code):
        """Get detailed course info."""
        return get_course_info(course_code)
    
    # Create a dictionary mapping function names to the actual callable functions
    # This matches what create_triage_agent expects
    handoff_functions = {
        "course_advisor": call_course_advisor_agent,
        "university_poet": call_university_poet_agent,
        "scheduling_assistant": call_scheduling_assistant_agent
    }
    
    course_tools = [
        recommend_courses_func,
        check_prerequisites_func,
        compare_paths_func,
        get_course_info_func
    ]
    
    # For the poet agent, we don't have specific tools, so use an empty list
    poet_tools = []
    
    # For scheduling assistant, we don't have specific tools yet either
    scheduling_tools = []
    
    # Return the appropriate agent
    if agent_name == "triage_agent":
        return create_triage_agent(handoff_functions)
    elif agent_name == "course_advisor_agent":
        return create_course_advisor_agent(course_tools, list(handoff_functions.values()))
    elif agent_name == "university_poet_agent":
        return create_university_poet_agent(poet_tools, list(handoff_functions.values()))
    elif agent_name == "scheduling_assistant_agent":
        return create_scheduling_assistant_agent(scheduling_tools, list(handoff_functions.values()))
    else:
        # Default to triage agent if unknown
        return create_triage_agent(handoff_functions)

def get_agent_display_name(agent_name):
    """Returns a user-friendly display name for the agent."""
    if agent_name == "triage_agent":
        return "Triage Agent"
    elif agent_name == "course_advisor_agent":
        return "Course Advisor Agent"
    elif agent_name == "university_poet_agent":
        return "University Poet Agent"
    elif agent_name == "scheduling_assistant_agent":
        return "Scheduling Assistant Agent"
    else:
        return "Agent"

def process_query(user_query: str, session_messages: list, current_agent: str = None) -> dict:
    """
    Process a user query using the appropriate agent.
    
    Args:
        user_query: The user's query text
        session_messages: List of previous messages
        current_agent: The current agent handling the session
        
    Returns:
        dict containing:
            - messages: Updated list of messages
            - current_agent: The agent that handled the query (may have changed)
            - agent_display_name: Human-readable name of the agent
    """
    print(f"Processing query with agent: {current_agent}")
    
    try:
        # Initialize response
        response_messages = [{"role": "user", "content": user_query}]
        
        # Ensure we have a current agent
        if not current_agent:
            current_agent = "triage_agent"
        
        # Format messages for Swarm API
        filtered_messages = []
        for msg in session_messages:
            # Skip empty messages
            if not msg:
                continue
                
            # Create a copy to modify
            msg_copy = msg.copy()
                
            # Handle 'tool' role compatibility
            if msg_copy.get('role') == 'tool':
                msg_copy['role'] = 'function'
                
            # Ensure function messages have a name parameter
            if msg_copy.get('role') == 'function':
                if 'name' not in msg_copy:
                    # Try to get name from function_name
                    if msg_copy.get('function_name'):
                        msg_copy['name'] = msg_copy.get('function_name')
                    else:
                        # Default name if none is found
                        msg_copy['name'] = 'generic_function'
                    
            # Only add messages with actual content or function/tool calls
            if msg_copy.get('content') or msg_copy.get('function_call') or msg_copy.get('tool_calls'):
                filtered_messages.append(msg_copy)
        
        # Add the current user message
        filtered_messages.append({"role": "user", "content": user_query})
        
        # Get the agent
        agent = get_agent_by_name(current_agent)
        
        # Process with Swarm
        result = swarm_client.run(
            agent=agent,
            messages=filtered_messages
        )
        
        # Debug
        if hasattr(result, 'messages'):
            print(f"Agent returned {len(result.messages)} messages")
            for i, msg in enumerate(result.messages):
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                # Only try to slice content if it's not None
                content_preview = content[:100] + '...' if content else '(No content)'
                print(f"Message {i}: role={role}, preview={content_preview}")
        
        # Check for handoff
        new_agent = current_agent
        handoff_detected = False
        
        # Look for handoff indicators in messages
        if hasattr(result, 'messages'):
            for msg in result.messages:
                content = msg.get('content', '')
                
                # Check for handoff text indicators, but only if content is not None
                if content is not None:
                    # Check for explicit function calls
                    if 'call_course_advisor_agent' in content:
                        new_agent = "course_advisor_agent"
                        handoff_detected = True
                        print("Handoff detected to Course Advisor Agent")
                    elif 'call_university_poet_agent' in content:
                        new_agent = "university_poet_agent"
                        handoff_detected = True
                        print("Handoff detected to University Poet Agent")
                    elif 'call_scheduling_assistant_agent' in content:
                        new_agent = "scheduling_assistant_agent"
                        handoff_detected = True
                        print("Handoff detected to Scheduling Assistant Agent")
                    # Also check for more natural language references to culture or poetry
                    elif any(x in content.lower() for x in ['transfer to university poet', 'transfer to poet', 'university poet agent', 'culture agent']):
                        new_agent = "university_poet_agent"
                        handoff_detected = True
                        print("Handoff detected to University Poet Agent via natural language")
        
        # Handle handoff if detected
        if handoff_detected:
            print(f"Agent changed: {current_agent} -> {new_agent}")
            
            # Get the new agent
            new_agent_obj = get_agent_by_name(new_agent)
            
            # Create simplified message for new agent
            handoff_messages = [
                {"role": "system", "content": f"You are the {get_agent_display_name(new_agent)}."},
                {"role": "user", "content": user_query}
            ]
            
            # Get response from new agent
            handoff_result = swarm_client.run(
                agent=new_agent_obj,
                messages=handoff_messages
            )
            
            # Add handoff notification
            response_messages.append({
                "role": "assistant", 
                "content": f"I'll transfer you to the {get_agent_display_name(new_agent)}."
            })
            
            # Add messages from handoff result
            if hasattr(handoff_result, 'messages'):
                for msg in handoff_result.messages:
                    response_messages.append(msg)
            
            # Return with new agent
            return {
                'messages': response_messages,
                'current_agent': new_agent,
                'agent_display_name': get_agent_display_name(new_agent)
            }
        
        # No handoff - use current agent's response
        if hasattr(result, 'messages'):
            # Process the messages
            for msg in result.messages:
                # If this is a message with a tool or function result, make sure it's properly formatted
                if msg.get('role') == 'tool' or msg.get('role') == 'function':
                    # Ensure the message has valid content
                    if msg.get('content') is None:
                        # If the tool/function call doesn't have content, create a placeholder
                        if msg.get('name'):
                            msg['content'] = f"[Results from {msg.get('name')}]"
                        else:
                            msg['content'] = "[Function result]"
                
                # Add the message to our response
                response_messages.append(msg)
        
        # Return result
        return {
            'messages': response_messages, 
            'current_agent': current_agent,
            'agent_display_name': get_agent_display_name(current_agent)
        }
    
    except Exception as e:
        print(f"Error in process_query: {str(e)}")
        traceback.print_exc()
        
        # Return error response
        return {
            'messages': [
                {"role": "user", "content": user_query},
                {"role": "assistant", "content": f"I'm sorry, I encountered an error: {str(e)}"}
            ],
            'current_agent': current_agent or "triage_agent",
            'agent_display_name': get_agent_display_name(current_agent or "triage_agent")
        }
