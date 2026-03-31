"""
Phase 2: ngrok Tunnel Automation Script
Automatically starts ngrok tunnel and displays the public URL for Vapi configuration.

Prerequisites:
1. Install ngrok: brew install ngrok
2. Configure authtoken: ngrok config add-authtoken YOUR_TOKEN
3. Backend server must be running: uvicorn app.main:app --reload

Usage:
    python scripts/start_ngrok.py
"""

import subprocess
import json
import time
import sys
import requests
from urllib.parse import urljoin

NGROK_API_URL = "http://localhost:4040/api/tunnels"
LOCAL_BACKEND = "http://localhost:8000"


def check_ngrok_installed():
    """Check if ngrok is installed"""
    try:
        result = subprocess.run(
            ["ngrok", "version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False
    except Exception:
        return False


def check_backend_running():
    """Check if backend server is running"""
    try:
        response = requests.get(f"{LOCAL_BACKEND}/", timeout=3)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except Exception:
        return False


def get_ngrok_tunnels():
    """Get active ngrok tunnels from the API"""
    try:
        response = requests.get(NGROK_API_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("tunnels", [])
    except requests.exceptions.ConnectionError:
        return None
    except Exception as e:
        print(f"Error checking ngrok: {e}")
        return None
    return None


def start_ngrok_tunnel():
    """Start ngrok tunnel in background"""
    print("🚀 Starting ngrok tunnel...")
    
    # Start ngrok as subprocess
    process = subprocess.Popen(
        ["ngrok", "http", LOCAL_BACKEND, "--log=stdout"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for tunnel to establish
    print("⏳ Waiting for ngrok to establish tunnel...")
    time.sleep(3)
    
    # Check if process is still running
    if process.poll() is not None:
        stdout, stderr = process.communicate()
        print(f"❌ ngrok failed to start")
        print(f"STDOUT: {stdout}")
        print(f"STDERR: {stderr}")
        return None
    
    return process


def display_vapi_config(public_url):
    """Display Vapi configuration information"""
    print("\n" + "=" * 70)
    print("🌐 NGROK TUNNEL ESTABLISHED")
    print("=" * 70)
    print(f"\n📍 Public URL: {public_url}")
    print(f"📍 Local Backend: {LOCAL_BACKEND}")
    
    print("\n" + "-" * 70)
    print("🔗 VAPI TOOL CONFIGURATION URLs:")
    print("-" * 70)
    
    endpoints = [
        ("create_todo", "Create Todo"),
        ("get_todos", "Get Todos"),
        ("complete_todo", "Complete Todo"),
        ("delete_todo", "Delete Todo"),
        ("add_reminder", "Add Reminder"),
        ("get_reminders", "Get Reminders"),
        ("delete_reminder", "Delete Reminder"),
        ("add_calendar_entry", "Add Calendar Entry"),
        ("get_calendar_entries", "Get Calendar Entries"),
        ("delete_calendar_entry", "Delete Calendar Entry"),
    ]
    
    for endpoint, description in endpoints:
        full_url = urljoin(public_url + "/", endpoint)
        print(f"  {description:25} → {full_url}")
    
    print("\n" + "=" * 70)
    print("📋 NEXT STEPS:")
    print("=" * 70)
    print("1. Copy the Public URL above")
    print("2. Go to https://dashboard.vapi.ai")
    print("3. Open your assistant → Tools tab")
    print("4. Add each tool with the URLs shown above")
    print("5. Test your voice assistant!")
    print("\n⚠️  Keep this terminal open to maintain the tunnel")
    print("=" * 70 + "\n")


def test_tunnel_connection(public_url):
    """Test if the tunnel is working by making a request"""
    test_url = urljoin(public_url + "/", "get_todos")
    
    payload = {
        "message": {
            "tool_calls": [{
                "id": "ngrok_test",
                "function": {"name": "get_todos", "arguments": {}}
            }]
        }
    }
    
    try:
        response = requests.post(test_url, json=payload, timeout=10)
        if response.status_code == 200:
            print("✅ Tunnel test successful! Backend is accessible via ngrok.")
            return True
        else:
            print(f"⚠️  Tunnel test returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️  Tunnel test failed: {e}")
        return False


def main():
    print("=" * 70)
    print("🎙️  VOICE ASSISTANT - PHASE 2: NGROK TUNNEL SETUP")
    print("=" * 70)
    
    # Check prerequisites
    print("\n📋 Checking prerequisites...")
    
    if not check_ngrok_installed():
        print("\n❌ ngrok is not installed!")
        print("\nInstall ngrok:")
        print("  brew install ngrok")
        print("\nThen configure your authtoken:")
        print("  ngrok config add-authtoken YOUR_AUTHTOKEN")
        print("\nGet your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken")
        sys.exit(1)
    print("  ✅ ngrok is installed")
    
    if not check_backend_running():
        print("\n❌ Backend server is not running!")
        print(f"\nStart the backend first:")
        print(f"  uvicorn app.main:app --reload")
        sys.exit(1)
    print("  ✅ Backend server is running at", LOCAL_BACKEND)
    
    # Check if ngrok is already running
    existing_tunnels = get_ngrok_tunnels()
    
    if existing_tunnels:
        print("\n✅ ngrok is already running!")
        for tunnel in existing_tunnels:
            if tunnel.get("public_url"):
                display_vapi_config(tunnel["public_url"])
                test_tunnel_connection(tunnel["public_url"])
                
                print("\n💡 Tip: Press Ctrl+C to stop ngrok when done")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n\n👋 Stopping...")
                return
    
    # Start ngrok tunnel
    ngrok_process = start_ngrok_tunnel()
    
    if not ngrok_process:
        sys.exit(1)
    
    # Wait and get tunnel info
    time.sleep(2)
    
    for attempt in range(5):
        tunnels = get_ngrok_tunnels()
        
        if tunnels:
            for tunnel in tunnels:
                public_url = tunnel.get("public_url")
                if public_url and public_url.startswith("https://"):
                    display_vapi_config(public_url)
                    test_tunnel_connection(public_url)
                    
                    print("\n💡 Tip: Press Ctrl+C to stop ngrok when done")
                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        print("\n\n👋 Stopping ngrok...")
                        ngrok_process.terminate()
                        ngrok_process.wait()
                        print("✅ ngrok stopped")
                    return
        
        print(f"  Waiting for tunnel... (attempt {attempt + 1}/5)")
        time.sleep(2)
    
    print("\n❌ Failed to get ngrok tunnel URL")
    ngrok_process.terminate()
    sys.exit(1)


if __name__ == "__main__":
    main()
