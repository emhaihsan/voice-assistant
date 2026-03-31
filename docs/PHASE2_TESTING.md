# Phase 2: Testing & Tunnel Setup - Complete Guide

## 🎯 Phase 2 Objectives
1. Run backend locally ✅
2. Test all endpoints ✅  
3. Expose via tunnel for Vapi integration

---

## ✅ Cara Verifikasi Implementasi

## Quick Start (Automated)

### Option 1: Auto-detect tunnel (recommended)
```bash
# Make sure backend is running first!
python scripts/start_tunnel.py
```

This script will:
- Auto-detect best available tunnel provider
- Start tunnel automatically
- Display all 10 Vapi tool URLs
- Test the tunnel connection
- Keep tunnel open until Ctrl+C

### Option 2: Choose specific provider
```bash
# Terminal 1: Backend
uvicorn app.main:app --reload

# Terminal 2: SSH tunnel (zero install, uses built-in SSH)
python scripts/start_tunnel.py --provider ssh

# Or: Cloudflare Tunnel
python scripts/start_tunnel.py --provider cloudflare

# Or: localtunnel (requires Node.js)
python scripts/start_tunnel.py --provider localtunnel
```

### Available Tunnel Providers
| Provider | Install | Command |
|----------|---------|--------|
| **localhost.run** | None (uses SSH) | `--provider ssh` |
| **Cloudflare Tunnel** | `brew install cloudflared` | `--provider cloudflare` |
| **localtunnel** | `npm install -g localtunnel` | `--provider localtunnel` |

---

## Testing Endpoints

### Automated Test Suite
```bash
python tests/test_api.py
```
Expected: **13/13 tests passed**

### Interactive Vapi Simulator
```bash
# Interactive mode
python scripts/vapi_simulator.py -i

# Or test specific endpoint
python scripts/vapi_simulator.py get_todos
python scripts/vapi_simulator.py create_todo '{"title": "Test", "description": "Test"}'
```

**Output yang diharapkan:**
```
============================================================
🎙️  VOICE ASSISTANT API - VERIFICATION TEST
============================================================

📋 Test 1: Get Todos
   ✅ GET /get_todos berfungsi

📝 Test 2: Create Todo
   ✅ POST /create_todo berfungsi

🔍 Test 3: Verify Created Todo Appears
   ✅ Todo found with ID: 1

✅ Test 4: Complete Todo (ID: 1)
   ✅ POST /complete_todo berfungsi

🗑️  Test 5: Delete Todo (ID: 1)
   ✅ POST /delete_todo berfungsi

⏰ Test 6: Add Reminder
   ✅ POST /add_reminder berfungsi

...

============================================================
📊 TEST SUMMARY
============================================================
  ✅ PASS - GET /get_todos
  ✅ PASS - POST /create_todo
  ✅ PASS - Verify Created Todo
  ✅ PASS - POST /complete_todo
  ✅ PASS - POST /delete_todo
  ✅ PASS - POST /add_reminder
  ...

🎉 SEMUA TEST BERHASIL! Implementation benar.
```

### 2. **Manual Testing dengan curl**

Jika test script tidak work, test manual:

#### Test 1: Create Todo
```bash
curl -X POST http://localhost:8000/create_todo \
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
```

**Expected Response:**
```json
{
  "results": [{
    "toolCallId": "call_123",
    "result": "success"
  }]
}
```

#### Test 2: List Todos
```bash
curl -X POST http://localhost:8000/get_todos \
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

**Expected Response:**
```json
{
  "results": [{
    "toolCallId": "call_456",
    "result": [
      {"id": 1, "title": "Walk the dog", "description": "Take dog out", "completed": false}
    ]
  }]
}
```

#### Test 3: Add Reminder
```bash
curl -X POST http://localhost:8000/add_reminder \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "tool_calls": [{
        "id": "call_rem_1",
        "function": {
          "name": "add_reminder",
          "arguments": {"reminder_text": "Buy milk", "importance": "high"}
        }
      }]
    }
  }'
```

#### Test 4: Add Calendar Event
```bash
curl -X POST http://localhost:8000/add_calendar_entry \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "tool_calls": [{
        "id": "call_cal_1",
        "function": {
          "name": "add_calendar_entry",
          "arguments": {
            "title": "Meeting",
            "description": "Team sync",
            "event_from": "2026-03-31T10:00:00",
            "event_to": "2026-03-31T11:00:00"
          }
        }
      }]
    }
  }'
```

### 3. **Checklist Verifikasi**

Verifikasi bahwa implementation memenuhi requirement Vapi:

| Check | Status | Notes |
|-------|--------|-------|
| ✅ Semua endpoint POST method | ☐ | Bukan GET/PUT/DELETE |
| ✅ Response punya `results` array | ☐ | Wajib untuk Vapi |
| ✅ `toolCallId` di-echo balik | ☐ | Harus sama dengan request |
| ✅ Arguments bisa string atau dict | ☐ | Handle `isinstance` check |
| ✅ Todo CRUD berfungsi | ☐ | Create, Read, Update, Delete |
| ✅ Reminder CRUD berfungsi | ☐ | Create, Read, Delete |
| ✅ Calendar CRUD berfungsi | ☐ | Create, Read, Delete |
| ✅ Error handling 400/404 | ☐ | Invalid request handled |
| ✅ SQLite DB tercreate | ☐ | `voice_assistant.db` muncul |
| ✅ FastAPI docs accessible | ☐ | `http://localhost:8000/docs` |

### 4. **Check FastAPI Auto-Generated Docs**

```bash
# Buka browser
curl http://localhost:8000/docs
```

Verifikasi:
- [ ] Semua 10 endpoint terdaftar
- [ ] Request/response schema benar
- [ ] Bisa "Try it out" dari UI

---

## 🌐 Phase 2: Tunnel Setup (Untuk Vapi Integration)

### Recommended: SSH Tunnel (Zero Install)

```bash
# No installation needed! Uses built-in SSH
python scripts/start_tunnel.py --provider ssh
```

### Alternative: Cloudflare Tunnel

```bash
# Install cloudflared
brew install cloudflared

# Run tunnel
python scripts/start_tunnel.py --provider cloudflare
```

### Alternative: localtunnel

```bash
# Requires Node.js
npm install -g localtunnel

# Run tunnel
python scripts/start_tunnel.py --provider localtunnel
```

**Output tunnel script:**
```
🌐 TUNNEL ESTABLISHED via localhost.run (SSH)
======================================================================

📍 Public URL: https://xxxxx.lhr.life
📍 Local Backend: http://localhost:8000

🔗 VAPI TOOL CONFIGURATION URLs:
  Create Todo               → https://xxxxx.lhr.life/create_todo
  Get Todos                 → https://xxxxx.lhr.life/get_todos
  ...
```

**Copy the Public URL untuk Vapi dashboard.**

---

## 🔧 Troubleshooting

### Error: "Connection refused"
```
❌ ERROR: Tidak bisa connect ke http://localhost:8000
   Pastikan server sudah running: uvicorn app:app --reload
```
**Fix:** Pastikan server jalan di terminal terpisah sebelum run test.

### Error: "404 Not Found"
**Fix:** Endpoint di Vapi harus pakai trailing slash? Tidak, FastAPI handle both.
Cek: `python -c "from app import app; print([r.path for r in app.routes])"`

### Error: "Missing toolCallId in response"
**Fix:** Response harus format: `{"results": [{"toolCallId": "...", "result": ...}]}`

### Error: Pydantic validation error
**Fix:** Pastikan `from_attributes = True` (bukan `orm_mode = True`) di Pydantic v2

---

## 🚀 Next: Phase 3 - Vapi Configuration

Setelah semua test pass:

1. **Start tunnel** (`python scripts/start_tunnel.py`)
2. **Login ke https://vapi.ai**
3. **Create assistant baru**
4. **Add 10 custom tools** dengan tunnel URL
5. **Test voice call!**

Lihat `README.md` section "Vapi Configuration" untuk detail setup.
