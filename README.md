# University Support System

A Django application demonstrating the use of OpenAI's Swarm framework to orchestrate multiple AI agents that respond to university-related queries.

## Overview

The system consists of:

- **Triage Agent**: Routes user queries to specialized agents, handles simple greetings directly
- **Course Advisor Agent**: Offers academic advice in an informative tone
- **University Poet Agent**: Responds to campus culture queries in haiku form
- **Scheduling Assistant Agent**: Provides factual information about academic dates

## Features

- **Intelligent Agent Routing**: The system intelligently routes queries to the most appropriate specialist agent
- **Natural Conversational Flow**: Each agent handles greetings naturally and avoids unnecessary handoffs
- **Visual Agent Identification**: Each message clearly shows which agent is responding
- **Agent Handoff Tracking**: When an agent transfers to another specialist, the handoff is visually indicated
- **Stylish UI**: Simple, intuitive chat interface with a streamlined design

## Installation

### Prerequisites
- Python 3.8+(preferred 3.11.9)
- OpenAI API key

### Setup

1. **Clone and install dependencies**
   ```bash
   git clone <repository-url>
   cd UniSupportSystem
   pip install -r requirements.txt
   ```

2. **Set environment variables**
   Create a `.env` file in the project root with(copy and paste below to a .env file in root directory, replace your_openai_api_key with your actual OpenAI API key and leave the rest as is):
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   DEBUG=True
   SECRET_KEY=django-insecure-key-for-development-only
   ```

3. **Run database migrations(for initializing db)**
   ```bash
   cd backend
   python3 manage.py migrate
   ```

4. **Start the application**
   ```bash
   cd backend
   python3 manage.py runserver
   ```

5. **Access the application**
   Open your browser and navigate to:
   ```
   http://localhost:8000/
   ```
   The chat interface will load automatically.

## Usage Examples

Test different agents with these example queries:

- **Course Advisor**: "What courses should I take for data science?"
- **University Poet**: "Tell me about campus life in haiku form"
- **Scheduling Assistant**: "Can you show me calendar year schedule of Fall 2025?"

The Triage Agent will automatically route your query to the appropriate specialist agent.

## Future Enhancements

With additional time, we could implement:

1. **Admin Panel**: View and manage conversations and monitor system usage
2. **Expanded Knowledge Base**: Connect to real university data sources
3. **User Authentication**: Personalized experiences and session management
4. **Better Error Handling**: Graceful recovery from API failures 
5. **Mobile Interface**: Native mobile application support



