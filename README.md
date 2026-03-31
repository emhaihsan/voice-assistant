# AI Voice Assistant 

[![GitHub](https://img.shields.io/badge/GitHub-emhaihsan%2Fvoice--assistant-blue?logo=github)](https://github.com/emhaihsan/voice-assistant)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)](https://python.org)

Professional AI voice assistant built with **FastAPI** and **Vapi** (Voice API) integration. Users can call the assistant via phone or web to manage todos, reminders, and calendar events through natural voice conversations.

## Demo

Call the assistant and say:
- *"Hey Mike, show me my todos"*
- *"Add a new todo: drink coffee"*
- *"Complete the todo called walk the dog"*
- *"What do I have on my calendar?"*
- *"Remind me to buy milk, high priority"*

## Architecture

```
User (Voice) ←→ Vapi Platform ←→ FastAPI Backend
                  - GPT-4o LLM        - SQLite DB
                  - Deepgram STT      - CRUD endpoints
                  - ElevenLabs TTS    - Vapi format
```

**Flow:**
1. User speaks → Vapi transcribes (Deepgram STT)
2. LLM (GPT-4o) decides which tool/function to call
3. Vapi sends POST request to FastAPI backend
4. Backend processes request, returns Vapi-formatted response
5. LLM generates voice response → ElevenLabs TTS → User hears response

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI |
| Database | SQLAlchemy + SQLite |
| Validation | Pydantic |
| Voice Platform | Vapi (vapi.ai) |
| STT | Deepgram Nova 2 |
| TTS | ElevenLabs |
| LLM | OpenAI GPT-4o |
| Tunneling (dev) | ngrok |

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Backend

```bash
uvicorn app:app --reload
```

The API will be available at `http://127.0.0.1:8000`

### 3. Test Endpoints

You can test the endpoints using curl:

```bash
# Create a todo
curl -X POST http://127.0.0.1:8000/create_todo \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "tool_calls": [{
        "id": "call_123",
        "function": {
          "name": "create_todo",
          "arguments": {"title": "Walk the dog", "description": "Take dog out"}
        }
      }]
    }
  }'

# Get all todos
curl -X POST http://127.0.0.1:8000/get_todos \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "tool_calls": [{
        "id": "call_456",
        "function": {
          "name": "get_todos",
          "arguments": {}
        }
      }]
    }
  }'
```

## Vapi Configuration

### 1. Create Vapi Account

- Sign up at https://vapi.ai (free credits available)
- Go to dashboard → Create new assistant

### 2. Assistant Settings

| Setting | Value |
|---------|-------|
| **Model** | OpenAI GPT-4o |
| **Temperature** | Low (0.1-0.3) for more accurate intent recognition |
| **First Message** | "Hey, I am Mike, your personal management assistant. How can I help you today?" |

### 3. System Prompt

```
You are Mike, a personal management assistant that helps users manage their todos, reminders, and calendar events. You can:
- Create, complete, and delete todos
- Add and view reminders with importance levels (high/medium/low)
- Schedule and view calendar events

Be helpful, friendly, and efficient. Always confirm actions after completing them.
```

### 4. Add Tools

For each endpoint, create a custom tool in Vapi:

| Tool Name | Server URL | Properties | Required |
|-----------|-----------|------------|----------|
| `create_todo` | `{ngrok_url}/create_todo` | title (string), description (string) | title |
| `get_todos` | `{ngrok_url}/get_todos` | — | — |
| `complete_todo` | `{ngrok_url}/complete_todo` | id (integer) | id |
| `delete_todo` | `{ngrok_url}/delete_todo` | id (integer) | id |
| `add_reminder` | `{ngrok_url}/add_reminder` | reminder_text (string), importance (string) | both |
| `get_reminders` | `{ngrok_url}/get_reminders` | — | — |
| `delete_reminder` | `{ngrok_url}/delete_reminder` | id (integer) | id |
| `add_calendar_entry` | `{ngrok_url}/add_calendar_entry` | title, description, event_from, event_to | title, event_from, event_to |
| `get_calendar_entries` | `{ngrok_url}/get_calendar_entries` | — | — |
| `delete_calendar_entry` | `{ngrok_url}/delete_calendar_entry` | id (integer) | id |

**Note:** Use ngrok to expose your local backend: `ngrok http http://127.0.0.1:8000`

### 5. Voice Settings (Optimal)

| Setting | Value |
|---------|-------|
| **Transcriber** | Deepgram, English, Nova 2 phone call model |
| **Background Denoising** | Enabled |
| **Voice Provider** | ElevenLabs |
| **Voice** | Drew (or your preference) |
| **Smart Endpointing** | Enabled |
| **Wait Time** | 0.6 seconds |

## API Endpoints

All endpoints are POST (Vapi requirement):

### Todos
- `POST /create_todo` - Create new todo
- `POST /get_todos` - List all todos
- `POST /complete_todo` - Mark todo as completed
- `POST /delete_todo` - Delete todo

### Reminders
- `POST /add_reminder` - Create reminder
- `POST /get_reminders` - List all reminders
- `POST /delete_reminder` - Delete reminder

### Calendar Events
- `POST /add_calendar_entry` - Schedule event
- `POST /get_calendar_entries` - List all events
- `POST /delete_calendar_entry` - Delete event

## Data Models

### Request Format (Vapi → Backend)
```json
{
  "message": {
    "tool_calls": [{
      "id": "call_abc123",
      "function": {
        "name": "create_todo",
        "arguments": "{\"title\": \"Walk the dog\"}"
      }
    }]
  }
}
```

### Response Format (Backend → Vapi)
```json
{
  "results": [{
    "toolCallId": "call_abc123",
    "result": "success"
  }]
}
```

## Project Structure

```
voiceAssistantApp/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── todos.py         # Todo CRUD endpoints
│   │           ├── reminders.py     # Reminder endpoints
│   │           └── calendar.py      # Calendar endpoints
│   ├── core/
│   │   └── database.py            # Database config & session
│   ├── models/
│   │   └── models.py               # SQLAlchemy models
│   ├── schemas/
│   │   └── schemas.py              # Pydantic schemas
│   ├── main.py                     # FastAPI app entry point
│   └── __init__.py
├── tests/
│   └── test_api.py                 # API test suite
├── docs/                           # Documentation (gitignored)
├── requirements.txt                # Dependencies
├── README.md                      # Documentation
├── .gitignore                     # Git ignore rules
└── run.py                         # Entry point runner
```

## Development

### Run Server

```bash
# Run with uvicorn
uvicorn app.main:app --reload

# Or use the run script
python run.py
```

### Run Tests

```bash
# Run full test suite
python tests/test_api.py

# Test with curl
curl -X POST http://localhost:8000/get_todos \
  -H "Content-Type: application/json" \
  -d '{"message":{"tool_calls":[{"id":"1","function":{"name":"get_todos","arguments":{}}}]}}'
```

### Expose via ngrok (for Vapi testing)
```bash
# Install ngrok first, then:
ngrok http http://127.0.0.1:8000

# Copy the HTTPS URL and use it in Vapi tools
```

## Deployment

For production, deploy on:
- **Railway** (https://railway.app)
- **Render** (https://render.com)
- **VPS** with static IP

Update Vapi tools to use the production URL.

## GitHub Repository

**Source Code:** [github.com/emhaihsan/voice-assistant](https://github.com/emhaihsan/voice-assistant)

```bash
git clone https://github.com/emhaihsan/voice-assistant.git
cd voice-assistant
pip install -r requirements.txt
uvicorn app:app --reload
```

## License

MIT
