#!/usr/bin/env python3
"""
Quick startup script for ADK Excel Generator Agent Web Server
Run from the parent directory: python start_adk_web.py
"""

import subprocess
import sys
import os

def main():
    """Start the ADK web server"""
    print("🚀 Starting ADK Excel Generator Web Server...")
    print("=" * 60)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  WARNING: .env file not found!")
        print("   Make sure to create .env with your GOOGLE_API_KEY")
    
    # Start adk web
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'google.adk', 'web'],
            cwd=os.getcwd(),
            env={**os.environ}
        )
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\n\n👋 ADK web server stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting ADK web server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
