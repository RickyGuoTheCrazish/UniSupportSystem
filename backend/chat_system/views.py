"""
Views for the University Support System chat interface.
Uses improved role handling while maintaining original approach.
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging
import uuid
from typing import Dict, Any
from django.utils import timezone
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .models import UserSession, Message
from swarm_client.client import process_query

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def chat_endpoint(request):
    """Process user query and route to appropriate agent via Swarm."""
    try:
        # Parse the request body
        data = json.loads(request.body)
        user_query = data.get('query', '')
        session_id = data.get('session_id')
        
        if not user_query:
            return JsonResponse({'error': 'No query provided'}, status=400)
        
        # Get or create session
        if session_id:
            try:
                session = UserSession.objects.get(session_id=session_id)
            except (UserSession.DoesNotExist, ValueError):
                session = UserSession.objects.create()
        else:
            session = UserSession.objects.create()
        
        # Update session's last active time
        session.last_active = timezone.now()
        session.save(update_fields=['last_active'])
        
        # Save user message to DB
        Message.objects.create(
            session=session,
            role='user',
            content=user_query
        )
        
        # Get existing messages in a format Swarm can use
        existing_messages = []
        for msg in session.messages.all().order_by('timestamp'):
            # Create a message object with original role and content
            message_dict = {"role": msg.role, "content": msg.content}
            
            # Add function_call if applicable
            if msg.function_name:
                if msg.role == 'assistant':
                    message_dict["function_call"] = {
                        "name": msg.function_name,
                        "arguments": msg.function_arguments or {}
                    }
                elif msg.role == 'function':
                    message_dict["name"] = msg.function_name
            
            existing_messages.append(message_dict)
        
        # Process the query using the client
        try:
            # Store the response from process_query
            result = process_query(
                user_query=user_query,
                session_messages=existing_messages,
                current_agent=session.current_agent
            )
            
            # Get updated information from the response
            current_agent = result.get('current_agent', session.current_agent)
            agent_display_name = result.get('agent_display_name', 'Agent')
            all_messages = result.get('messages', [])
            
            # Save any new messages
            for msg in all_messages:
                # Only add messages that aren't already saved (the new ones)
                if msg.get('role') == 'user' and msg.get('content') == user_query:
                    # Skip the user message we just added as it's already saved
                    continue
                
                # Extract function call info if present
                function_name = None
                function_args = None
                
                if msg.get('function_call'):
                    function_name = msg.get('function_call').get('name')
                    function_args = msg.get('function_call').get('arguments')
                elif msg.get('tool_calls'):
                    for tool_call in msg.get('tool_calls'):
                        if tool_call.get('type') == 'function' and tool_call.get('function'):
                            function_name = tool_call.get('function').get('name')
                            function_args = tool_call.get('function').get('arguments')
                            break
                
                # For each new message, save it to the database with its original role
                # Make sure content is never NULL to avoid database constraint errors
                content = msg.get('content')
                if content is None:
                    # For function call messages with no content, create a description
                    if function_name:
                        content = f"[Function call: {function_name}]"
                    else:
                        content = "" # Empty string instead of NULL
                
                Message.objects.create(
                    session=session,
                    role=msg.get('role'),
                    content=content,
                    agent_name=agent_display_name if msg.get('role') == 'assistant' else None,
                    function_name=function_name,
                    function_arguments=function_args
                )
            
            # Update the session's current agent with the potentially new agent from the result
            # This ensures handoffs persist between requests
            new_current_agent = result.get('current_agent', current_agent)
            session.current_agent = new_current_agent
            session.save(update_fields=['current_agent'])
            
            # Find a suitable response content to return
            response_content = ""
            all_assistant_responses = []
            
            # Look for meaningful content in the messages
            # First check for tool responses which usually have most useful info
            for msg in all_messages:
                if msg.get('role') == 'tool' or msg.get('role') == 'function':
                    content = msg.get('content')
                    if content:  # Only proceed if content is not None
                        if any(marker in content.lower() for marker in ['course', 'recommend', 'credit', 'biology', 'physics']):
                            response_content = content
                            print(f"VIEW: Found specific content: {content[:50]}...")
                            break
            
            # If no specific tool content was found, use assistant responses
            if not response_content:
                for msg in all_messages:
                    if msg.get('role') == 'assistant' and msg.get('content'):
                        response_content = msg.get('content')
                        print(f"VIEW: Using assistant message: {response_content[:50]}...")
                        break
            
            # If we still don't have a response, use a fallback
            if not response_content:
                response_content = f"I'm the {agent_display_name}. How can I help you today?"
                
            # Collect all assistant and tool responses for the frontend
            for msg in all_messages:
                if msg.get('role') in ['assistant', 'tool', 'function']:
                    content = msg.get('content')
                    if content:  # Only include messages with content
                        all_assistant_responses.append({
                            'content': content,
                            'agent': agent_display_name
                        })
                
        except Exception as e:
            logger.exception(f"Error processing with Swarm: {str(e)}")
            # Fallback to a simple response if Swarm fails
            agent_display_name = "System"
            response_content = f"I'm having trouble processing your request. Error: {str(e)}"
            all_assistant_responses = [{
                'content': response_content,
                'agent': agent_display_name
            }]
            
            # Save the error response
            Message.objects.create(
                session=session,
                role='assistant',
                content=response_content,
                agent_name=agent_display_name
            )
        
        # Get all messages for this session
        session_messages = [{
            "id": str(msg.id),
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat(),
            "agent_name": msg.agent_name,
            "function_name": msg.function_name,
            "function_arguments": msg.function_arguments,
        } for msg in session.messages.all().order_by('timestamp')]
        
        # Return response with all necessary fields
        return JsonResponse({
            'session_id': str(session.session_id),
            'response': response_content,  # Main response content
            'responses': all_assistant_responses,  # All assistant and tool responses
            'agent': agent_display_name,
            'messages': session_messages  # All messages for the session
        })
    
    except Exception as e:
        logger.exception(f"Error processing chat request: {str(e)}")
        return JsonResponse({'error': f'Error processing request: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def clear_chat(request):
    """Clear chat history for a session."""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        
        if not session_id:
            return JsonResponse({'error': 'No session ID provided'}, status=400)
        
        try:
            session = UserSession.objects.get(session_id=session_id)
            # Delete all messages
            session.messages.all().delete()
            
            # Reset the agent to the triage agent
            session.current_agent = "triage_agent"
            session.save(update_fields=['current_agent'])
        except (UserSession.DoesNotExist, ValueError):
            return JsonResponse({'error': 'Session not found'}, status=404)
        
        return JsonResponse({
            'session_id': str(session.session_id),
            'status': 'success',
            'message': 'Chat history cleared'
        })
    
    except Exception as e:
        logger.exception(f"Error clearing chat: {str(e)}")
        return JsonResponse({'error': f'Error clearing chat: {str(e)}'}, status=500)
