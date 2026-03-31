"""
Tunnel Manager - Multi-Provider Tunnel for Vapi Integration
Supports multiple tunnel providers as alternatives to ngrok:
  1. localhost.run (SSH-based, zero install)
  2. cloudflared (Cloudflare Tunnel)
  3. localtunnel (npx, requires Node.js)

Usage:
    python scripts/start_tunnel.py                    # Auto-detect best provider
    python scripts/start_tunnel.py --provider ssh     # Use localhost.run (SSH)
    python scripts/start_tunnel.py --provider cloudflare  # Use cloudflared
    python scripts/start_tunnel.py --provider localtunnel # Use localtunnel (npx)
"""

import subprocess
import re
import time
import sys
import signal
import argparse
import requests
from urllib.parse import urljoin

LOCAL_BACKEND = "http://localhost:8000"
LOCAL_PORT = 8000

PROVIDERS = {
    "ssh": {
        "name": "localhost.run (SSH)",
        "install": "No installation needed — uses built-in SSH",
        "requires": "ssh",
    },
    "cloudflare": {
        "name": "Cloudflare Tunnel (cloudflared)",
        "install": "brew install cloudflared",
        "requires": "cloudflared",
    },
    "localtunnel": {
        "name": "localtunnel (npx)",
        "install": "npm install -g localtunnel  OR  use npx (comes with Node.js)",
        "requires": "npx",
    },
}


def check_backend_running():
    """Check if backend server is running"""
    try:
        response = requests.get(f"{LOCAL_BACKEND}/", timeout=3)
        return response.status_code == 200
    except Exception:
        return False


def check_command_exists(cmd):
    """Check if a command is available in PATH"""
    try:
        result = subprocess.run(
            ["which", cmd],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


def detect_best_provider():
    """Auto-detect the best available tunnel provider"""
    # SSH is always available on macOS/Linux
    if check_command_exists("ssh"):
        return "ssh"
    if check_command_exists("cloudflared"):
        return "cloudflare"
    if check_command_exists("npx"):
        return "localtunnel"
    return None


def start_ssh_tunnel():
    """Start tunnel via localhost.run (SSH-based, zero install)"""
    print("🚀 Starting localhost.run tunnel via SSH...")
    print("   (No signup or token required)\n")

    process = subprocess.Popen(
        [
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "ServerAliveInterval=30",
            "-R", f"80:localhost:{LOCAL_PORT}",
            "nokey@localhost.run",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    # Read output to find the public URL
    public_url = None
    start_time = time.time()

    while time.time() - start_time < 30:
        line = process.stdout.readline()
        if not line:
            if process.poll() is not None:
                break
            continue

        print(f"   {line.strip()}")

        # localhost.run outputs URL like: https://xxxxx.lhr.life
        url_match = re.search(r'(https://[a-zA-Z0-9._-]+\.lhr\.life)', line)
        if not url_match:
            url_match = re.search(r'(https://[a-zA-Z0-9._-]+\.localhost\.run)', line)
        if url_match:
            public_url = url_match.group(1)
            break

    return process, public_url


def start_cloudflare_tunnel():
    """Start tunnel via Cloudflare Tunnel (cloudflared)"""
    print("🚀 Starting Cloudflare Tunnel...")
    print("   (No signup required for quick tunnels)\n")

    process = subprocess.Popen(
        [
            "cloudflared",
            "tunnel",
            "--url", f"http://localhost:{LOCAL_PORT}",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    public_url = None
    start_time = time.time()

    while time.time() - start_time < 30:
        line = process.stdout.readline()
        if not line:
            if process.poll() is not None:
                break
            continue

        print(f"   {line.strip()}")

        # cloudflared outputs: https://xxxxx.trycloudflare.com
        url_match = re.search(r'(https://[a-zA-Z0-9._-]+\.trycloudflare\.com)', line)
        if url_match:
            public_url = url_match.group(1)
            break

    return process, public_url


def start_localtunnel():
    """Start tunnel via localtunnel (npx)"""
    print("🚀 Starting localtunnel via npx...")
    print("   (Uses Node.js npx)\n")

    process = subprocess.Popen(
        ["npx", "localtunnel", "--port", str(LOCAL_PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    public_url = None
    start_time = time.time()

    while time.time() - start_time < 30:
        line = process.stdout.readline()
        if not line:
            if process.poll() is not None:
                break
            continue

        print(f"   {line.strip()}")

        # localtunnel outputs: your url is: https://xxxxx.loca.lt
        url_match = re.search(r'(https://[a-zA-Z0-9._-]+\.loca\.lt)', line)
        if url_match:
            public_url = url_match.group(1)
            break

    return process, public_url


def display_vapi_config(public_url, provider_name):
    """Display Vapi configuration information"""
    print("\n" + "=" * 70)
    print(f"🌐 TUNNEL ESTABLISHED via {provider_name}")
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
    print("🔍 Testing tunnel connection...")
    test_url = urljoin(public_url + "/", "get_todos")

    payload = {
        "message": {
            "tool_calls": [
                {
                    "id": "tunnel_test",
                    "function": {"name": "get_todos", "arguments": {}},
                }
            ]
        }
    }

    try:
        response = requests.post(test_url, json=payload, timeout=15)
        if response.status_code == 200:
            print("✅ Tunnel test successful! Backend is accessible via tunnel.")
            return True
        else:
            print(f"⚠️  Tunnel test returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️  Tunnel test failed: {e}")
        print("   (This may be normal for some providers — try manually)")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Tunnel Manager - Expose local backend for Vapi integration"
    )
    parser.add_argument(
        "--provider",
        choices=["ssh", "cloudflare", "localtunnel"],
        help="Tunnel provider to use (default: auto-detect)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=LOCAL_PORT,
        help=f"Local port to tunnel (default: {LOCAL_PORT})",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available tunnel providers",
    )
    args = parser.parse_args()

    port = args.port
    backend_url = f"http://localhost:{port}"

    print("=" * 70)
    print("🎙️  VOICE ASSISTANT - TUNNEL MANAGER")
    print("=" * 70)

    if args.list:
        print("\n📋 Available tunnel providers:\n")
        for key, info in PROVIDERS.items():
            available = "✅" if check_command_exists(info["requires"]) else "❌"
            print(f"  {available} --provider {key:15} {info['name']}")
            print(f"     Install: {info['install']}\n")
        return

    # Check backend
    print("\n📋 Checking prerequisites...")

    if not check_backend_running():
        print(f"\n❌ Backend server is not running at {backend_url}")
        print(f"\nStart the backend first:")
        print(f"  uvicorn app.main:app --reload")
        sys.exit(1)
    print(f"  ✅ Backend server is running at {backend_url}")

    # Select provider
    provider = args.provider
    if not provider:
        provider = detect_best_provider()
        if not provider:
            print("\n❌ No tunnel provider available!")
            print("\nInstall one of:")
            for key, info in PROVIDERS.items():
                print(f"  {info['name']}: {info['install']}")
            sys.exit(1)

    provider_info = PROVIDERS[provider]
    print(f"  ✅ Using tunnel provider: {provider_info['name']}")

    # Check if provider command exists
    if not check_command_exists(provider_info["requires"]):
        print(f"\n❌ {provider_info['name']} is not installed!")
        print(f"\nInstall: {provider_info['install']}")
        sys.exit(1)

    # Start tunnel
    print()
    if provider == "ssh":
        process, public_url = start_ssh_tunnel()
    elif provider == "cloudflare":
        process, public_url = start_cloudflare_tunnel()
    elif provider == "localtunnel":
        process, public_url = start_localtunnel()

    if not public_url:
        print("\n❌ Failed to establish tunnel — no public URL obtained")
        if process and process.poll() is None:
            process.terminate()
        sys.exit(1)

    display_vapi_config(public_url, provider_info["name"])

    # Test connection
    time.sleep(2)
    test_tunnel_connection(public_url)

    # Keep running
    print("\n💡 Press Ctrl+C to stop the tunnel")

    def signal_handler(sig, frame):
        print("\n\n👋 Stopping tunnel...")
        if process and process.poll() is None:
            process.terminate()
            process.wait(timeout=5)
        print("✅ Tunnel stopped")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        while True:
            if process.poll() is not None:
                print("\n⚠️  Tunnel process exited unexpectedly")
                print("   Restart with: python scripts/start_tunnel.py")
                sys.exit(1)
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    main()
