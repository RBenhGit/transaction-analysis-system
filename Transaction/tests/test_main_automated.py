#!/usr/bin/env python3
"""
Test main.py in automated mode.
"""

import os
import sys
import subprocess
import signal
import time

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test_main_app():
    """Test that main.py starts without errors."""
    print("=" * 50)
    print("TESTING MAIN APPLICATION")
    print("=" * 50)

    try:
        # Start main.py as a subprocess
        process = subprocess.Popen(
            [sys.executable, 'main.py'],
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Wait a short time for startup
        time.sleep(3)

        # Terminate the process
        process.terminate()

        # Get output
        stdout, stderr = process.communicate(timeout=5)

        print("+ Main application started successfully")
        print("+ Startup output:")
        for line in stdout.split('\n')[:10]:  # Show first 10 lines
            if line.strip():
                print(f"  {line}")

        if stderr:
            print("+ Startup warnings/errors:")
            for line in stderr.split('\n')[:5]:  # Show first 5 lines
                if line.strip():
                    print(f"  {line}")

        return True

    except subprocess.TimeoutExpired:
        print("- Main application timed out")
        return False
    except Exception as e:
        print(f"- Main application failed to start: {e}")
        return False

if __name__ == "__main__":
    success = test_main_app()
    sys.exit(0 if success else 1)