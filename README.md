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
- **Agent Handoff Tracking**: When an agent transfers to another specialist, the handoff is visually indicated(in most cases yes, or at least in backend logs)
- **Stylish UI**: Simple, intuitive chat interface with a streamlined design
- **Database**: SQLite database for storing conversation history and user sessions

## Installation

### Prerequisites
- Python 3.8+(preferred 3.11.9)
- OpenAI API key

### Setup

1. **Unzip the folder , get into the root directory and install dependencies**
   ```
   pip install -r requirements.txt
   or 
   pip3 install -r requirements.txt 
   ```

2. **Set environment variables**
   Create a `.env` file in the project root with(copy and paste below to a .env file in root directory, replace your_openai_api_key with your actual OpenAI API key and leave the rest as is):
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   DEBUG=True
   SECRET_KEY=django-insecure-key-for-development-only
   ```

3. **Run database migrations(for initializing db, only need to do this once, might be a bit slow around 30 seconds)**
   ```
   cd backend
   python manage.py migrate
   or
   python3 manage.py migrate
   ```

4. **Start the application**
   ```
   cd backend
   python manage.py runserver
   or
   python3 manage.py runserver
   ```

5. **Access the application**
   Open your browser and navigate to:
   
   http://localhost:8000/
   

## Usage Examples

Test different agents with these example queries:

- **Course Advisor**: "What courses should I take for data science?"
- **University Poet**: "Tell me about campus life in haiku form"
- **Scheduling Assistant**: "Can you show me academic important dates of Fall 2025?"

The Triage Agent will automatically route your query to the appropriate specialist agent, sometimes might need user to re-query with the actual content since the agent transfer process count as a round of talk in some cases. 

## Future Enhancements

With additional time, below could be implemented/optimized:

1. **Applying real world data and full RAG architecture**: Connect to real university data sources, applying vector embedding with a full RAG architecture that can connect to pdf documents, csv files and other resources rather only only applied with semantic search for course recommendations.
2. **User Authentication/Validation**: Safer user experience, can be implemented by using JWT or other authentication methods, validation can be implemented by using Django's built-in authentication system.
3. **Admin Panel**: View and manage conversations and monitor system usage
4. **Expanding the functionality so the system can be a helper that can handle more process**: Like adding hands and legs to the system by applying with mcp servers so that it can handle more complex queries and really be able to communicate and make changes with other database or external systems. 


## Database views
To view SQLite database for storing conversation history and user sessions
1. Import the SQLite database file (e.g., `db.sqlite3`) into a SQLite database viewer(SQLiteStudio for Mac) or other management tool.
2. Check the chat_system_message and chat_system_usersession to view the data(I've attached screenshots via the email).

## Add on resources
sentence-transformers from hugging face, which is used for semantic search. It is a pre-trained model that can be used to generate embeddings for text data.  In this case, I used this + vector embedding as a lightweight fallback solution for semantic search via simulated course recommendations. (can be seen from backend terminal logs natively if triggered)
