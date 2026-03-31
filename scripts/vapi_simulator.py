"""
Vapi Webhook Simulator
Simulates Vapi tool call requests to test endpoints without actual voice calls.

Usage:
    python scripts/vapi_simulator.py <endpoint> [arguments]

Examples:
    python scripts/vapi_simulator.py get_todos
    python scripts/vapi_simulator.py create_todo '{"title": "Test", "description": "Test desc"}'
    python scripts/vapi_simulator.py add_reminder '{"reminder_text": "Buy milk", "importance": "high"}'
    python scripts/vapi_simulator.py add_calendar_entry '{"title": "Meeting", "event_from": "2026-03-31T10:00:00", "event_to": "2026-03-31T11:00:00"}'
"""

import sys
import json
import argparse
import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"


def simulate_vapi_call(endpoint, function_name, arguments=None, base_url=BASE_URL):
    """Simulate a Vapi tool call request"""
    
    payload = {
        "message": {
            "tool_calls": [
                {
                    "id": f"simulator_{function_name}_{int(datetime.now().timestamp())}",
                    "function": {
                        "name": function_name,
                        "arguments": arguments or {}
                    }
                }
            ]
        }
    }
    
    url = f"{base_url}/{endpoint}"
    
    print(f"\n{'='*60}")
    print(f"🎙️  VAPI SIMULATOR - {function_name}")
    print(f"{'='*60}")
    print(f"\n📤 Request to: {url}")
    print(f"📦 Payload:\n{json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        print(f"\n📥 Response Status: {response.status_code}")
        print(f"📦 Response Body:\n{json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print(f"\n✅ Success! Endpoint working correctly.")
        else:
            print(f"\n❌ Error! Status code: {response.status_code}")
        
        return response.status_code == 200
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection Error!")
        print(f"   Make sure backend is running: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        return False


def interactive_mode(base_url=BASE_URL):
    """Interactive mode for testing multiple endpoints"""
    
    print("\n" + "="*60)
    print("🎙️  VAPI WEBHOOK SIMULATOR - Interactive Mode")
    print("="*60)
    print(f"\nBackend URL: {base_url}")
    print("\nAvailable endpoints:")
    print("  1. get_todos")
    print("  2. create_todo")
    print("  3. complete_todo")
    print("  4. delete_todo")
    print("  5. add_reminder")
    print("  6. get_reminders")
    print("  7. delete_reminder")
    print("  8. add_calendar_entry")
    print("  9. get_calendar_entries")
    print("  10. delete_calendar_entry")
    print("  0. Exit")
    
    while True:
        print("\n" + "-"*60)
        choice = input("Select endpoint (0-10): ").strip()
        
        if choice == "0":
            print("👋 Goodbye!")
            break
        
        elif choice == "1":
            simulate_vapi_call("get_todos", "get_todos", {})
        
        elif choice == "2":
            title = input("Enter todo title: ").strip()
            desc = input("Enter description (optional): ").strip()
            simulate_vapi_call("create_todo", "create_todo", {
                "title": title,
                "description": desc
            })
        
        elif choice == "3":
            todo_id = input("Enter todo ID to complete: ").strip()
            simulate_vapi_call("complete_todo", "complete_todo", {
                "id": int(todo_id)
            })
        
        elif choice == "4":
            todo_id = input("Enter todo ID to delete: ").strip()
            simulate_vapi_call("delete_todo", "delete_todo", {
                "id": int(todo_id)
            })
        
        elif choice == "5":
            text = input("Enter reminder text: ").strip()
            importance = input("Enter importance (high/medium/low) [medium]: ").strip() or "medium"
            simulate_vapi_call("add_reminder", "add_reminder", {
                "reminder_text": text,
                "importance": importance
            })
        
        elif choice == "6":
            simulate_vapi_call("get_reminders", "get_reminders", {})
        
        elif choice == "7":
            rem_id = input("Enter reminder ID to delete: ").strip()
            simulate_vapi_call("delete_reminder", "delete_reminder", {
                "id": int(rem_id)
            })
        
        elif choice == "8":
            title = input("Enter event title: ").strip()
            desc = input("Enter description (optional): ").strip()
            
            now = datetime.now()
            default_start = now.strftime("%Y-%m-%dT%H:%M:%S")
            default_end = (now + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")
            
            start = input(f"Start time [{default_start}]: ").strip() or default_start
            end = input(f"End time [{default_end}]: ").strip() or default_end
            
            simulate_vapi_call("add_calendar_entry", "add_calendar_entry", {
                "title": title,
                "description": desc,
                "event_from": start,
                "event_to": end
            })
        
        elif choice == "9":
            simulate_vapi_call("get_calendar_entries", "get_calendar_entries", {})
        
        elif choice == "10":
            event_id = input("Enter event ID to delete: ").strip()
            simulate_vapi_call("delete_calendar_entry", "delete_calendar_entry", {
                "id": int(event_id)
            })
        
        else:
            print("❌ Invalid choice. Please select 0-10.")


def main():
    parser = argparse.ArgumentParser(
        description="Vapi Webhook Simulator - Test endpoints without voice calls"
    )
    parser.add_argument(
        "endpoint",
        nargs="?",
        help="Endpoint to test (e.g., get_todos, create_todo)"
    )
    parser.add_argument(
        "arguments",
        nargs="?",
        help="JSON arguments for the function (e.g., '{\"title\": \"Test\"}')"
    )
    parser.add_argument(
        "--base-url",
        default=BASE_URL,
        help=f"Base URL for backend (default: {BASE_URL})"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    
    args = parser.parse_args()
    
    if args.interactive or not args.endpoint:
        interactive_mode(args.base_url)
        return
    
    # Parse arguments if provided
    arguments = {}
    if args.arguments:
        try:
            arguments = json.loads(args.arguments)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON arguments: {e}")
            sys.exit(1)
    
    # Map endpoint to function name
    function_name = args.endpoint
    
    success = simulate_vapi_call(
        args.endpoint,
        function_name,
        arguments,
        args.base_url
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
