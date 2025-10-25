# Solo Leveling Self-Improvement System

A backend system that extracts Gmail emails, processes them with AWS Bedrock LLM to create quests, integrates with Google Calendar, and provides an Agno agent for user interaction.

## Features

- Gmail email extraction via OAuth2
- LLM-powered quest generation from emails
- Google Calendar integration for quest events
- Agno agent for conversational quest management
- FastAPI backend for mobile app integration

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. Set up Google OAuth credentials:
```bash
python scripts/setup_credentials.py
```

4. Run the email processing:
```bash
python scripts/process_emails.py
```

5. Start the API server:
```bash
python src/api/main.py
```

## API Endpoints

- `POST /process-emails?days=7` - Process emails from last N days
- `GET /quests` - Get quests with optional filters
- `PATCH /quests/{id}` - Update quest status
- `POST /chat` - Chat with the quest agent
- `GET /health` - Health check

