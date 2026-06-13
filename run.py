"""
Khamsat Deep Scanner PRO - Unified Runner
Infrastructure for running the FastAPI server.
"""
import os
import sys
import subprocess

def main():
    print("=" * 60)
    print("💎 KHAMSAT DEEP SCANNER PRO - REALTIME ENGINE")
    print("=" * 60 + "\n")

    os.makedirs("data", exist_ok=True)
    
    # Start the FastAPI server which handles everything (WebSockets + Scraper Loop)
    print("🌐 [PRO] Starting Real-time Server...")
    subprocess.run([sys.executable, "server.py"])

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 [PRO] System closed successfully.")
        sys.exit(0)
