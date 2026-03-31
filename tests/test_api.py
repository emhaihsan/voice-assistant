"""
Test script untuk Voice Assistant API
Run: python tests/test_api.py

Script ini akan mengecek semua endpoint dan memastikan:
1. Response format sesuai Vapi specification
2. Tool call ID dikembalikan dengan benar
3. CRUD operations berfungsi
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

# Test data
TEST_TODO_TITLE = "Test Todo from Script"
TEST_REMINDER_TEXT = "Test Reminder"
TEST_EVENT_TITLE = "Test Calendar Event"

def make_request(endpoint, function_name, arguments=None, tool_call_id="test_123"):
    """Helper function untuk membuat request dengan Vapi format"""
    payload = {
        "message": {
            "tool_calls": [
                {
                    "id": tool_call_id,
                    "function": {
                        "name": function_name,
                        "arguments": arguments or {}
                    }
                }
            ]
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/{endpoint}", json=payload, timeout=5)
        return response
    except requests.exceptions.ConnectionError:
        print(f"❌ ERROR: Tidak bisa connect ke {BASE_URL}")
        print("   Pastikan server sudah running: uvicorn app:app --reload")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None

def check_response(response, expected_status=200, check_tool_call_id=None):
    """Check response format dan tool_call_id"""
    if response is None:
        return False
    
    if response.status_code != expected_status:
        print(f"   Status: {response.status_code} (expected {expected_status})")
        return False
    
    try:
        data = response.json()
        
        # Check format Vapi response
        if "results" not in data:
            print(f"   ❌ Missing 'results' in response")
            return False
        
        if check_tool_call_id:
            if not data["results"] or data["results"][0].get("toolCallId") != check_tool_call_id:
                print(f"   ❌ Tool call ID tidak sesuai atau missing")
                return False
        
        return True
    except json.JSONDecodeError:
        print(f"   ❌ Response bukan valid JSON")
        return False

# ========== TEST CASES ==========

def test_get_todos():
    """Test GET todos (list semua todos)"""
    print("\n📋 Test 1: Get Todos")
    response = make_request("get_todos", "get_todos", {}, "test_todos_1")
    
    if check_response(response, 200, "test_todos_1"):
        data = response.json()
        if isinstance(data["results"][0]["result"], list):
            print("   ✅ GET /get_todos berfungsi")
            return True
    print("   ❌ GET /get_todos gagal")
    return False

def test_create_todo():
    """Test CREATE todo"""
    print("\n📝 Test 2: Create Todo")
    response = make_request(
        "create_todo", 
        "create_todo", 
        {"title": TEST_TODO_TITLE, "description": "Test description"},
        "test_create_1"
    )
    
    if check_response(response, 200, "test_create_1"):
        print("   ✅ POST /create_todo berfungsi")
        return True
    print("   ❌ POST /create_todo gagal")
    return False

def test_get_todos_after_create():
    """Verify todo yang baru dibuat muncul di list"""
    print("\n🔍 Test 3: Verify Created Todo Appears")
    response = make_request("get_todos", "get_todos", {}, "test_verify_1")
    
    if check_response(response, 200):
        data = response.json()
        todos = data["results"][0]["result"]
        
        for todo in todos:
            if todo.get("title") == TEST_TODO_TITLE:
                print(f"   ✅ Todo found with ID: {todo.get('id')}")
                return todo.get('id')
        
        print("   ❌ Todo yang dibuat tidak muncul di list")
    return None

def test_complete_todo(todo_id):
    """Test COMPLETE todo"""
    print(f"\n✅ Test 4: Complete Todo (ID: {todo_id})")
    response = make_request(
        "complete_todo",
        "complete_todo",
        {"id": todo_id},
        "test_complete_1"
    )
    
    if check_response(response, 200, "test_complete_1"):
        print("   ✅ POST /complete_todo berfungsi")
        return True
    print("   ❌ POST /complete_todo gagal")
    return False

def test_delete_todo(todo_id):
    """Test DELETE todo"""
    print(f"\n🗑️  Test 5: Delete Todo (ID: {todo_id})")
    response = make_request(
        "delete_todo",
        "delete_todo",
        {"id": todo_id},
        "test_delete_1"
    )
    
    if check_response(response, 200, "test_delete_1"):
        print("   ✅ POST /delete_todo berfungsi")
        return True
    print("   ❌ POST /delete_todo gagal")
    return False

def test_add_reminder():
    """Test ADD reminder"""
    print("\n⏰ Test 6: Add Reminder")
    response = make_request(
        "add_reminder",
        "add_reminder",
        {"reminder_text": TEST_REMINDER_TEXT, "importance": "high"},
        "test_reminder_1"
    )
    
    if check_response(response, 200, "test_reminder_1"):
        print("   ✅ POST /add_reminder berfungsi")
        return True
    print("   ❌ POST /add_reminder gagal")
    return False

def test_get_reminders():
    """Test GET reminders"""
    print("\n📋 Test 7: Get Reminders")
    response = make_request("get_reminders", "get_reminders", {}, "test_get_rem_1")
    
    if check_response(response, 200, "test_get_rem_1"):
        data = response.json()
        reminders = data["results"][0]["result"]
        
        for rem in reminders:
            if rem.get("reminder_text") == TEST_REMINDER_TEXT:
                print(f"   ✅ Reminder found with ID: {rem.get('id')}")
                return rem.get('id')
        
        print("   ❌ Reminder tidak ditemukan")
    return None

def test_delete_reminder(reminder_id):
    """Test DELETE reminder"""
    print(f"\n🗑️  Test 8: Delete Reminder (ID: {reminder_id})")
    response = make_request(
        "delete_reminder",
        "delete_reminder",
        {"id": reminder_id},
        "test_del_rem_1"
    )
    
    if check_response(response, 200, "test_del_rem_1"):
        print("   ✅ POST /delete_reminder berfungsi")
        return True
    print("   ❌ POST /delete_reminder gagal")
    return False

def test_add_calendar_entry():
    """Test ADD calendar entry"""
    print("\n📅 Test 9: Add Calendar Entry")
    from datetime import datetime, timedelta
    
    now = datetime.now()
    event_from = now.isoformat()
    event_to = (now + timedelta(hours=1)).isoformat()
    
    response = make_request(
        "add_calendar_entry",
        "add_calendar_entry",
        {
            "title": TEST_EVENT_TITLE,
            "description": "Test event description",
            "event_from": event_from,
            "event_to": event_to
        },
        "test_cal_1"
    )
    
    if check_response(response, 200, "test_cal_1"):
        print("   ✅ POST /add_calendar_entry berfungsi")
        return True
    print("   ❌ POST /add_calendar_entry gagal")
    return False

def test_get_calendar_entries():
    """Test GET calendar entries"""
    print("\n📋 Test 10: Get Calendar Entries")
    response = make_request("get_calendar_entries", "get_calendar_entries", {}, "test_get_cal_1")
    
    if check_response(response, 200, "test_get_cal_1"):
        data = response.json()
        events = data["results"][0]["result"]
        
        for event in events:
            if event.get("title") == TEST_EVENT_TITLE:
                print(f"   ✅ Calendar event found with ID: {event.get('id')}")
                return event.get('id')
        
        print("   ❌ Calendar event tidak ditemukan")
    return None

def test_delete_calendar_entry(event_id):
    """Test DELETE calendar entry"""
    print(f"\n🗑️  Test 11: Delete Calendar Entry (ID: {event_id})")
    response = make_request(
        "delete_calendar_entry",
        "delete_calendar_entry",
        {"id": event_id},
        "test_del_cal_1"
    )
    
    if check_response(response, 200, "test_del_cal_1"):
        print("   ✅ POST /delete_calendar_entry berfungsi")
        return True
    print("   ❌ POST /delete_calendar_entry gagal")
    return False

def test_invalid_request():
    """Test error handling untuk invalid request"""
    print("\n⚠️  Test 12: Error Handling (Invalid Request)")
    
    # Test dengan function name yang tidak ada
    response = make_request("get_todos", "wrong_function_name", {}, "test_error_1")
    
    if response and response.status_code == 400:
        print("   ✅ Error handling berfungsi (return 400)")
        return True
    print("   ❌ Error handling tidak berfungsi dengan benar")
    return False

def test_tool_call_id_echo():
    """Verify tool_call_id selalu di-echo balik"""
    print("\n🔄 Test 13: Tool Call ID Echo")
    
    unique_id = "custom_id_abc_xyz_123"
    response = make_request("get_todos", "get_todos", {}, unique_id)
    
    if check_response(response, 200, unique_id):
        print(f"   ✅ Tool call ID '{unique_id}' di-echo dengan benar")
        return True
    print("   ❌ Tool call ID tidak di-echo dengan benar")
    return False

def main():
    print("=" * 60)
    print("🎙️  VOICE ASSISTANT API - VERIFICATION TEST")
    print("=" * 60)
    print(f"\nTesting against: {BASE_URL}")
    print("Pastikan server running: uvicorn app.main:app --reload")
    
    results = []
    
    # Run tests
    results.append(("GET /get_todos", test_get_todos()))
    results.append(("POST /create_todo", test_create_todo()))
    
    todo_id = test_get_todos_after_create()
    if todo_id:
        results.append(("Verify Created Todo", True))
        results.append(("POST /complete_todo", test_complete_todo(todo_id)))
        results.append(("POST /delete_todo", test_delete_todo(todo_id)))
    else:
        results.append(("Verify Created Todo", False))
        results.append(("POST /complete_todo", False))
        results.append(("POST /delete_todo", False))
    
    results.append(("POST /add_reminder", test_add_reminder()))
    
    reminder_id = test_get_reminders()
    if reminder_id:
        results.append(("Verify Reminder", True))
        results.append(("POST /delete_reminder", test_delete_reminder(reminder_id)))
    else:
        results.append(("Verify Reminder", False))
        results.append(("POST /delete_reminder", False))
    
    results.append(("POST /add_calendar_entry", test_add_calendar_entry()))
    
    event_id = test_get_calendar_entries()
    if event_id:
        results.append(("Verify Calendar Entry", True))
        results.append(("POST /delete_calendar_entry", test_delete_calendar_entry(event_id)))
    else:
        results.append(("Verify Calendar Entry", False))
        results.append(("POST /delete_calendar_entry", False))
    
    results.append(("Error Handling", test_invalid_request()))
    results.append(("Tool Call ID Echo", test_tool_call_id_echo()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    print("-" * 60)
    print(f"  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 SEMUA TEST BERHASIL! Implementation benar.")
        print("\nNext steps:")
        print("  1. Install ngrok: brew install ngrok")
        print("  2. Run: ngrok http http://127.0.0.1:8000")
        print("  3. Copy HTTPS URL ke Vapi dashboard")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test gagal. Periksa implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
