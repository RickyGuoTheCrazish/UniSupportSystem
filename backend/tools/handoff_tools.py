"""
Handoff tools for agent transitions in the University Support System.
These functions facilitate transferring control between different agents.
"""

from swarm import Agent
from typing import Dict, Any, Optional

# Custom Result class since it's no longer available in Swarm library
class Result:
    def __init__(self, value=None, agent=None, context_variables=None):
        self.value = value
        self.agent = agent
        self.context_variables = context_variables or {}


def call_course_advisor_agent(context_variables: Dict[str, Any] = None) -> Result:
    """
    Transfer conversation to the Course Advisor Agent.
    
    Args:
        context_variables: Dictionary containing conversation context
        
    Returns:
        Result object that tells Swarm to hand off to course advisor agent
    """
    from swarm_client.client import get_agent_by_name
    
    return Result(
        value="Transferring to Course Advisor Agent",
        agent=get_agent_by_name("course_advisor_agent"),
        context_variables={"current_agent": "course_advisor_agent"}
    )


def call_university_poet_agent(context_variables: Dict[str, Any] = None) -> Result:
    """
    Transfer conversation to the University Poet Agent.
    
    Args:
        context_variables: Dictionary containing conversation context
        
    Returns:
        Result object that tells Swarm to hand off to university poet agent
    """
    from swarm_client.client import get_agent_by_name
    
    return Result(
        value="Transferring to University Poet Agent",
        agent=get_agent_by_name("university_poet_agent"),
        context_variables={"current_agent": "university_poet_agent"}
    )


def call_scheduling_assistant_agent(context_variables: Dict[str, Any] = None) -> Result:
    """
    Transfer conversation to the Scheduling Assistant Agent.
    
    Args:
        context_variables: Dictionary containing conversation context
        
    Returns:
        Result object that tells Swarm to hand off to scheduling assistant agent
    """
    from swarm_client.client import get_agent_by_name
    
    return Result(
        value="Transferring to Scheduling Assistant Agent",
        agent=get_agent_by_name("scheduling_assistant_agent"),
        context_variables={"current_agent": "scheduling_assistant_agent"}
    )


def call_triage_agent(context_variables: Dict[str, Any] = None) -> Result:
    """
    Transfer conversation back to the Triage Agent.
    
    Args:
        context_variables: Dictionary containing conversation context
        
    Returns:
        Result object that tells Swarm to hand off to triage agent
    """
    from swarm_client.client import get_agent_by_name
    
    return Result(
        value="Transferring back to Triage Agent",
        agent=get_agent_by_name("triage_agent"),
        context_variables={"current_agent": "triage_agent"}
    )


# Dictionary mapping agent names to their handoff functions
HANDOFF_FUNCTIONS = {
    "course_advisor_agent": call_course_advisor_agent,
    "university_poet_agent": call_university_poet_agent,
    "scheduling_assistant_agent": call_scheduling_assistant_agent,
    "triage_agent": call_triage_agent
}
