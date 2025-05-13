/**
 * University Support System - Main JavaScript
 * Handles chat functionality and API interactions
 */

// DOM Elements
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const agentNameDisplay = document.getElementById('agent-name');

// State management
let sessionId = null;
let isWaitingForResponse = false;

// Force new session on page reload (for testing purposes)
const forceNewSessionOnReload = true;

// Load session ID from localStorage if available or create new one
document.addEventListener('DOMContentLoaded', () => {
    if (forceNewSessionOnReload) {
        // Clear any existing session when page loads
        localStorage.removeItem('uniSupportSessionId');
        sessionId = null;
        console.log('Starting fresh session on page load');
    } else {
        // Use existing session if available
        sessionId = localStorage.getItem('uniSupportSessionId');
    }
    
    // Set up event listeners
    sendButton.addEventListener('click', handleSendMessage);
    userInput.addEventListener('keydown', handleInputKeydown);
    document.getElementById('new-chat').addEventListener('click', handleNewChat);
});

/**
 * Handles sending a user message to the backend
 */
function handleSendMessage() {
    const message = userInput.value.trim();
    
    if (!message || isWaitingForResponse) {
        return;
    }
    
    // Display user message in chat
    addMessageToChat('user', message);
    
    // Clear input field
    userInput.value = '';
    
    // Show loading indicator
    isWaitingForResponse = true;
    addLoadingIndicator();
    
    // Send request to backend
    sendQueryToBackend(message);
}

/**
 * Handles keydown events in the input field
 * @param {KeyboardEvent} event 
 */
function handleInputKeydown(event) {
    // Send message on Enter key (without Shift)
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        handleSendMessage();
    }
}

/**
 * Adds a message to the chat interface
 * @param {string} role - 'user', 'assistant', or 'system'
 * @param {string} content - Message content
 * @param {string} agentName - Name of the agent (for assistant messages)
 */
function addMessageToChat(role, content, agentName = null) {
    // Create message element
    const messageElement = document.createElement('div');
    messageElement.className = `message ${role}`;
    
    // Create message content element
    const contentElement = document.createElement('div');
    contentElement.className = 'message-content';
    
    // Detect handoff messages (when an agent is transferring to another agent)
    let isHandoffMessage = false;
    let handoffAgentName = null;
    
    if (role === 'assistant' && content) {
        // Check for handoff messages by detecting common phrases
        const handoffPhrases = [
            "transfer you to",
            "connect you with",
            "hand you off to",
            "pass you to",
            "would be better answered by"
        ];
        
        for (const phrase of handoffPhrases) {
            if (content.toLowerCase().includes(phrase.toLowerCase())) {
                isHandoffMessage = true;
                break;
            }
        }
        
        // Determine which agent is likely doing the handoff based on content
        if (isHandoffMessage) {
            // Agent mapping for reverse lookup
            const agentMapping = {
                "Triage Agent": ["course advisor", "university poet", "scheduling assistant"],
                "Course Advisor Agent": ["triage agent", "university poet", "scheduling assistant"],
                "University Poet Agent": ["triage agent", "course advisor", "scheduling assistant"],
                "Scheduling Assistant Agent": ["triage agent", "course advisor", "university poet"]
            };
            
            // Check which agent is being handed off to in the message
            for (const [sourceAgent, targetPhrases] of Object.entries(agentMapping)) {
                for (const phrase of targetPhrases) {
                    if (content.toLowerCase().includes(phrase.toLowerCase()) && 
                        agentName !== sourceAgent) {
                        handoffAgentName = sourceAgent;
                        break;
                    }
                }
                if (handoffAgentName) break;
            }
            
            // If we couldn't determine handoff agent, use a fallback
            if (!handoffAgentName) {
                // Default to Triage Agent as fallback source for handoffs
                handoffAgentName = "Triage Agent";
            }
        }
    }
    
    // Add agent label based on the agent type
    if (role === 'assistant') {
        // Update the agent name in the header (always use current agent)
        agentNameDisplay.textContent = agentName || 'Assistant';
        
        // For the message label, use handoff agent if detected
        const agentLabel = document.createElement('div');
        agentLabel.className = 'agent-label';
        
        if (isHandoffMessage && handoffAgentName) {
            // Use the handoff agent name for this message
            agentLabel.textContent = handoffAgentName;
            // Add special styling for handoff messages
            agentLabel.classList.add('handoff-message');
            messageElement.classList.add('handoff-message');
        } else {
            // Use the agent name provided
            agentLabel.textContent = agentName || 'Assistant';
        }
        
        contentElement.appendChild(agentLabel);
    } else if (role === 'system') {
        // Add a system label
        const systemLabel = document.createElement('div');
        systemLabel.className = 'agent-label system';
        systemLabel.textContent = 'System';
        contentElement.appendChild(systemLabel);
    }
    
    // Special formatting for Triage Agent
    if (role === 'assistant' && agentName === 'Triage Agent') {
        // Create a content container for the formatted message
        const formattedContent = document.createElement('div');
        formattedContent.className = 'formatted-content';
        formattedContent.innerHTML = formatMessageContent(content);
        contentElement.appendChild(formattedContent);
        
        // Add a special triage class to the message element
        messageElement.classList.add('triage-message');
    }
    // Special formatting for Course Advisor Agent
    else if (role === 'assistant' && agentName === 'Course Advisor Agent') {
        // Create a content container for the formatted message
        const formattedContent = document.createElement('div');
        formattedContent.className = 'formatted-content';
        formattedContent.innerHTML = formatMessageContent(content);
        contentElement.appendChild(formattedContent);
        
        // Add a special advisor class to the message element
        messageElement.classList.add('advisor-message');
    }
    // Special formatting for University Poet Agent
    else if (role === 'assistant' && agentName === 'University Poet Agent') {
        // Try to detect haiku format (3 lines with specific syllable pattern)
        const lines = content.split('\n').filter(line => line.trim());
        if (lines.length === 3) {
            const haikuElement = document.createElement('div');
            haikuElement.className = 'haiku';
            
            lines.forEach(line => {
                const lineElement = document.createElement('div');
                lineElement.className = 'haiku-line';
                lineElement.textContent = line;
                haikuElement.appendChild(lineElement);
            });
            
            contentElement.appendChild(haikuElement);
        } else {
            // Create a content container for the formatted message
            const formattedContent = document.createElement('div');
            formattedContent.className = 'formatted-content';
            formattedContent.innerHTML = formatMessageContent(content);
            contentElement.appendChild(formattedContent);
        }
        // Add a special poet class to the message element
        messageElement.classList.add('poet-message');
    }
    // Special formatting for Scheduling Assistant Agent
    else if (role === 'assistant' && agentName === 'Scheduling Assistant Agent') {
        // Create a content container for the formatted message
        const formattedContent = document.createElement('div');
        formattedContent.className = 'formatted-content';
        formattedContent.innerHTML = formatMessageContent(content);
        contentElement.appendChild(formattedContent);
        
        // Add a special scheduling class to the message element
        messageElement.classList.add('scheduling-message');
    }
    // Default formatting for all other messages
    else {
        // Create a content container for the formatted message
        const formattedContent = document.createElement('div');
        formattedContent.className = 'formatted-content';
        formattedContent.innerHTML = formatMessageContent(content);
        contentElement.appendChild(formattedContent);
    }
    
    // Add content to message
    messageElement.appendChild(contentElement);
    
    // Add message to chat
    chatMessages.appendChild(messageElement);
    
    // Scroll to bottom
    scrollToBottom();
}

/**
 * Formats message content with proper paragraph breaks and links
 * @param {string} content 
 * @returns {string} Formatted HTML
 */
function formatMessageContent(content) {
    // Convert line breaks to paragraphs
    const paragraphs = content.split('\n\n');
    return paragraphs
        .map(p => {
            // Skip empty paragraphs
            if (!p.trim()) return '';
            
            // Handle single line breaks within paragraphs
            const lines = p.split('\n');
            
            // If it looks like a list with - or * items, format accordingly
            if (lines.some(line => line.trim().match(/^[\-\*•]/))) {
                return `<ul>${lines.map(line => {
                    const trimmed = line.trim();
                    if (trimmed.match(/^[\-\*•]/)) {
                        return `<li>${trimmed.replace(/^[\-\*•]\s*/, '')}</li>`;
                    }
                    return `<li>${trimmed}</li>`;
                }).join('')}</ul>`;
            }
            
            return `<p>${lines.join('<br>')}</p>`;
        })
        .filter(p => p) // Remove empty paragraphs
        .join('');
}

/**
 * Adds a loading indicator to the chat
 */
function addLoadingIndicator() {
    const loadingElement = document.createElement('div');
    loadingElement.id = 'loading-indicator';
    loadingElement.className = 'message assistant';
    
    const contentElement = document.createElement('div');
    contentElement.className = 'message-content';
    
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    typingIndicator.innerHTML = '<span></span><span></span><span></span>';
    
    contentElement.appendChild(typingIndicator);
    loadingElement.appendChild(contentElement);
    
    chatMessages.appendChild(loadingElement);
    scrollToBottom();
}

/**
 * Removes the loading indicator from the chat
 */
function removeLoadingIndicator() {
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.remove();
    }
}

/**
 * Scrolls the chat to the bottom
 */
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Sends a query to the backend API
 * @param {string} query - User's message
 */
function sendQueryToBackend(query) {
    fetch('/api/query/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            query: query,
            session_id: sessionId
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        // Save session ID if not already saved
        if (!sessionId && data.session_id) {
            sessionId = data.session_id;
            localStorage.setItem('uniSupportSessionId', sessionId);
        }
        
        // Remove loading indicator
        removeLoadingIndicator();
        isWaitingForResponse = false;
        
        // Add assistant response to chat
        if (data.response) {
            addMessageToChat('assistant', data.response, data.agent);
        } else {
            addMessageToChat('system', 'Sorry, there was an issue processing your request.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        removeLoadingIndicator();
        isWaitingForResponse = false;
        addMessageToChat('system', 'Sorry, there was an error connecting to the server. Please try again later.');
    });
}

/**
 * Creates a brand new chat session or clears the existing one
 */
function handleNewChat() {
    if (isWaitingForResponse) {
        return;
    }
    
    // If there's an existing session, clear it on the server
    if (sessionId) {
        fetch('/api/clear/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ session_id: sessionId })
        })
        .then(response => response.json())
        .catch(error => {
            console.error('Error clearing chat:', error);
        });
    }
    
    // Clear localStorage and reset session
    localStorage.removeItem('uniSupportSessionId');
    sessionId = null;
    
    // Clear the UI
    clearChatMessages();
    
    // Reset agent name
    agentNameDisplay.textContent = 'Triage Agent';
    
    // Add welcome message
    addSystemWelcomeMessage();
    
    console.log('Started new chat session');
}

/**
 * Handles clearing the chat history
 */
function clearChatMessages() {
    while (chatMessages.firstChild) {
        chatMessages.removeChild(chatMessages.firstChild);
    }
}

/**
 * Adds a system welcome message to the chat
 */
function addSystemWelcomeMessage() {
    addMessageToChat('system', 'Welcome to the University Support Center! I\'m the Triage Agent. How can I help you today?\n\nYou can ask me about:\n- Course recommendations and academic advising\n- Campus culture and social events (our poet will answer in haiku)\n- Class schedules, deadlines, and academic dates');
}
