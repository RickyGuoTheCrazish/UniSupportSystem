# University Support System

A Django application demonstrating the use of OpenAI's Swarm framework to orchestrate multiple AI agents that respond to university-related queries.

## Overview

The system consists of:

- **Triage Agent**: Routes user queries to specialized agents
- **Course Advisor Agent**: Offers academic advice in an informative tone
- **University Poet Agent**: Responds to campus culture queries in haiku form
- **Scheduling Assistant Agent**: Provides factual information about academic dates

## Installation

### Prerequisites
- Python 3.8+
- OpenAI API key

### Setup

1. **Clone and install dependencies**
   ```bash
   git clone <repository-url>
   cd UniSupportSystem
   pip install -r requirements.txt
   ```

2. **Set environment variables**
   Create a `.env` file in the project root with:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   DEBUG=True
   SECRET_KEY=django-insecure-key-for-development-only
   ```

3. **Run database migrations**
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
   Open your browser and go to http://localhost:8000

## Usage Examples

Test different agents with these example queries:

- **Course Advisor**: "What courses should I take for data science?"
- **University Poet**: "Tell me about campus life in haiku form"
- **Scheduling Assistant**: "When is the registration deadline?"

The Triage Agent will automatically route your query to the appropriate specialist agent.

## Future Enhancements

With additional time, we could implement:

1. **Admin Panel**: View and manage conversations and monitor system usage
2. **Expanded Knowledge Base**: Connect to real university data sources
3. **User Authentication**: Personalized experiences and session management
4. **Better Error Handling**: Graceful recovery from API failures 
5. **Mobile Interface**: Native mobile application support



