# Phase 3: Vapi Assistant Configuration

Complete guide to configure Mike (AI Voice Assistant) in Vapi dashboard.

---

## 🎯 Phase 3 Objectives
1. Create Vapi assistant
2. Configure system prompt & first message
3. Add all 10 custom tools
4. Configure voice & transcription settings
5. Test voice calls

---

## Prerequisites

- [ ] Phase 1 complete (backend implementation)
- [ ] Phase 2 complete (ngrok tunnel active)
- [ ] ngrok URL ready (e.g., `https://abc123.ngrok-free.app`)
- [ ] Vapi account (free credits available at vapi.ai)

---

## Step 1: Create Assistant

1. Go to https://dashboard.vapi.ai
2. Click **"Create Assistant"**
3. Select **"Blank Assistant"**

---

## Step 2: Configure Model & Prompt

### Basic Settings
| Setting | Value |
|---------|-------|
| **Name** | Mike (Personal Assistant) |
| **Model** | OpenAI GPT-4o (or GPT-5.4 nano for faster responses) |
| **Temperature** | 0.2 - 0.4 (lower = more consistent function calling) |

### First Message
```
Hey, I am Mike, your personal management assistant. How can I help you today?
```

### System Prompt
```
You are Mike, a helpful and efficient personal management assistant. You help users manage their daily tasks, reminders, and calendar events through natural conversation.

## Capabilities
You can help users with:
- **Todos**: Create, complete, delete, and list todos
- **Reminders**: Add reminders with importance levels (high/medium/low)
- **Calendar**: Schedule events with start and end times

## Guidelines
1. Be friendly, professional, and concise
2. Always confirm actions after completing them ("I've added 'Buy milk' to your reminders")
3. If a user wants to complete or delete an item but doesn't specify which one, first list the items and ask them to specify
4. For calendar events, ask for title, description (optional), start time, and end time
5. For reminders, ask for the reminder text and importance level

## Important Notes
- When a user says "delete" or "complete" without specifying ID, load the list first and ask them to clarify
- Convert natural language times to ISO format for calendar entries (e.g., "tomorrow 3pm" → "2026-04-01T15:00:00")
- Always echo back what you've done to confirm understanding
```

---

## Step 3: Add Custom Tools

For each endpoint, add a custom tool in the **Tools** tab:

### Tool Configuration Template

#### 1. create_todo
```json
{
  "name": "create_todo",
  "description": "Create a new todo item. Use when the user wants to add a task to their todo list.",
  "url": "https://YOUR_NGROK_URL/create_todo",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "message": {
      "tool_calls": [
        {
          "id": "{{tool_call_id}}",
          "function": {
            "name": "create_todo",
            "arguments": {
              "title": "{{title}}",
              "description": "{{description}}"
            }
          }
        }
      ]
    }
  },
  "properties": {
    "title": {
      "type": "string",
      "description": "The title of the todo item"
    },
    "description": {
      "type": "string",
      "description": "Optional description for the todo"
    }
  },
  "required": ["title"]
}
```

#### 2. get_todos
```json
{
  "name": "get_todos",
  "description": "Get all todo items. Use when the user asks to see their todos or task list.",
  "url": "https://YOUR_NGROK_URL/get_todos",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "message": {
      "tool_calls": [
        {
          "id": "{{tool_call_id}}",
          "function": {
            "name": "get_todos",
            "arguments": {}
          }
        }
      ]
    }
  }
}
```

#### 3. complete_todo
```json
{
  "name": "complete_todo",
  "description": "Mark a todo as completed. Use when the user says they finished a task or wants to mark something as done. If ID is not specified, get the list first and ask user to clarify.",
  "url": "https://YOUR_NGROK_URL/complete_todo",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "message": {
      "tool_calls": [
        {
          "id": "{{tool_call_id}}",
          "function": {
            "name": "complete_todo",
            "arguments": {
              "id": "{{id}}"
            }
          }
        }
      ]
    }
  },
  "properties": {
    "id": {
      "type": "integer",
      "description": "The ID of the todo to complete. If not explicitly specified, get the list first and ask user."
    }
  },
  "required": ["id"]
}
```

#### 4. delete_todo
```json
{
  "name": "delete_todo",
  "description": "Delete a todo item. Use when the user wants to remove a task. If ID is not specified, get the list first and ask user to clarify.",
  "url": "https://YOUR_NGROK_URL/delete_todo",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "message": {
      "tool_calls": [
        {
          "id": "{{tool_call_id}}",
          "function": {
            "name": "delete_todo",
            "arguments": {
              "id": "{{id}}"
            }
          }
        }
      ]
    }
  },
  "properties": {
    "id": {
      "type": "integer",
      "description": "The ID of the todo to delete. If not explicitly specified, get the list first and ask user."
    }
  },
  "required": ["id"]
}
```

#### 5. add_reminder
```json
{
  "name": "add_reminder",
  "description": "Add a new reminder with importance level. Use when user wants to set a reminder.",
  "url": "https://YOUR_NGROK_URL/add_reminder",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "message": {
      "tool_calls": [
        {
          "id": "{{tool_call_id}}",
          "function": {
            "name": "add_reminder",
            "arguments": {
              "reminder_text": "{{reminder_text}}",
              "importance": "{{importance}}"
            }
          }
        }
      ]
    }
  },
  "properties": {
    "reminder_text": {
      "type": "string",
      "description": "The text content of the reminder"
    },
    "importance": {
      "type": "string",
      "enum": ["high", "medium", "low"],
      "description": "Importance level of the reminder"
    }
  },
  "required": ["reminder_text", "importance"]
}
```

#### 6. get_reminders
```json
{
  "name": "get_reminders",
  "description": "Get all reminders. Use when user asks to see their reminders.",
  "url": "https://YOUR_NGROK_URL/get_reminders",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "message": {
      "tool_calls": [
        {
          "id": "{{tool_call_id}}",
          "function": {
            "name": "get_reminders",
            "arguments": {}
          }
        }
      ]
    }
  }
}
```

#### 7. delete_reminder
```json
{
  "name": "delete_reminder",
  "description": "Delete a reminder. Use when user wants to remove a reminder. If ID not specified, get the list first.",
  "url": "https://YOUR_NGROK_URL/delete_reminder",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "message": {
      "tool_calls": [
        {
          "id": "{{tool_call_id}}",
          "function": {
            "name": "delete_reminder",
            "arguments": {
              "id": "{{id}}"
            }
          }
        }
      ]
    }
  },
  "properties": {
    "id": {
      "type": "integer",
      "description": "The ID of the reminder to delete"
    }
  },
  "required": ["id"]
}
```

#### 8. add_calendar_entry
```json
{
  "name": "add_calendar_entry",
  "description": "Add a calendar event. Use when user wants to schedule something. Ask for title, description (optional), start time, and end time. Convert natural language times to ISO format.",
  "url": "https://YOUR_NGROK_URL/add_calendar_entry",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "message": {
      "tool_calls": [
        {
          "id": "{{tool_call_id}}",
          "function": {
            "name": "add_calendar_entry",
            "arguments": {
              "title": "{{title}}",
              "description": "{{description}}",
              "event_from": "{{event_from}}",
              "event_to": "{{event_to}}"
            }
          }
        }
      ]
    }
  },
  "properties": {
    "title": {
      "type": "string",
      "description": "Title of the calendar event"
    },
    "description": {
      "type": "string",
      "description": "Optional description of the event"
    },
    "event_from": {
      "type": "string",
      "format": "date-time",
      "description": "Start time in ISO 8601 format (e.g., 2026-04-01T14:00:00)"
    },
    "event_to": {
      "type": "string",
      "format": "date-time",
      "description": "End time in ISO 8601 format (e.g., 2026-04-01T15:00:00)"
    }
  },
  "required": ["title", "event_from", "event_to"]
}
```

#### 9. get_calendar_entries
```json
{
  "name": "get_calendar_entries",
  "description": "Get all calendar events. Use when user asks about their schedule or calendar.",
  "url": "https://YOUR_NGROK_URL/get_calendar_entries",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "message": {
      "tool_calls": [
        {
          "id": "{{tool_call_id}}",
          "function": {
            "name": "get_calendar_entries",
            "arguments": {}
          }
        }
      ]
    }
  }
}
```

#### 10. delete_calendar_entry
```json
{
  "name": "delete_calendar_entry",
  "description": "Delete a calendar event. Use when user wants to cancel or remove an event. If ID not specified, get the list first.",
  "url": "https://YOUR_NGROK_URL/delete_calendar_entry",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "message": {
      "tool_calls": [
        {
          "id": "{{tool_call_id}}",
          "function": {
            "name": "delete_calendar_entry",
            "arguments": {
              "id": "{{id}}"
            }
          }
        }
      ]
    }
  },
  "properties": {
    "id": {
      "type": "integer",
      "description": "The ID of the calendar event to delete"
    }
  },
  "required": ["id"]
}
```

---

## Step 4: Voice & Transcription Settings

### Voice Settings
| Setting | Recommended Value |
|---------|-------------------|
| **Voice Provider** | ElevenLabs |
| **Voice** | Drew (friendly male) / Bella (friendly female) |
| **Voice Stability** | 0.5 |
| **Voice Similarity Boost** | 0.75 |
| **Voice Style** | 0.3 |

### Transcription Settings
| Setting | Recommended Value |
|---------|-------------------|
| **Provider** | Deepgram |
| **Model** | Nova 2 |
| **Language** | English (or your preferred language) |
| **Enable Background Denoising** | ✅ ON |
| **Smart Endpointing** | ✅ ON |
| **Endpointing Wait Time** | 0.6 seconds |

### Advanced Settings
| Setting | Value |
|---------|-------|
| **Response Delay (ms)** | 0 |
| **LLM Request Delay (ms)** | 0 |
| **Silence Timeout (ms)** | 30000 |
| **Max Duration (seconds)** | 600 |

---

## Step 5: Test Voice Call

### Web Testing
1. Click **"Test"** button in Vapi dashboard
2. Allow microphone access
3. Try these commands:
   - "Hey Mike, what can you do?"
   - "Add a todo: buy groceries"
   - "Show me my todos"
   - "Remind me to call mom, high priority"
   - "What do I have on my calendar?"
   - "Schedule a meeting tomorrow at 3pm for one hour"

### Phone Testing
1. Buy a phone number in Vapi dashboard
2. Assign the assistant to the number
3. Call the number and test

---

## Troubleshooting

### Tool Call Errors (400/404)
- Check ngrok URL is correct in tool configuration
- Ensure backend is running
- ngrok URL changes on restart - update Vapi tools

### LLM Not Calling Tools
- Lower the temperature (0.1-0.3)
- Make tool descriptions more explicit
- Add examples in system prompt

### Voice Not Clear
- Enable background denoising
- Try different voices (ElevenLabs has many options)
- Adjust voice stability/similarity

---

## Phase 3 Complete Checklist

- [ ] Assistant created in Vapi dashboard
- [ ] Model set to GPT-4o (or GPT-5.4 nano)
- [ ] First message configured
- [ ] System prompt added
- [ ] All 10 tools added with correct URLs
- [ ] Voice settings configured
- [ ] Transcription settings configured
- [ ] Web test successful
- [ ] Phone test successful (optional)

---

## Next Steps

Once Phase 3 is complete:
1. Share your assistant with others
2. Deploy backend to production (Railway/Render)
3. Update Vapi tools with production URL
4. Consider adding more features (email reminders, integrations)
