#!/usr/bin/env python3
"""
Launch script for Equity Research Report Generator UI.

This script starts the Streamlit web interface.
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Launch Streamlit UI."""
    ui_path = Path(__file__).parent / "ui" / "app.py"
    
    print("🚀 Starting Equity Research Report Generator UI...")
    print(f"📂 UI File: {ui_path}")
    print("\n" + "="*70)
    print("The UI will open in your default browser.")
    print("Press Ctrl+C to stop the server.")
    print("="*70 + "\n")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            str(ui_path),
            "--server.port", "8501",
            "--server.headless", "false"
        ], check=True)
    except KeyboardInterrupt:
        print("\n\n✋ Shutting down UI...")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error starting UI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

