#!/usr/bin/env python3
"""
Alternative server startup script
This handles the server startup more gracefully with better error handling
"""

import os
import sys
import subprocess
from pathlib import Path


def check_basic_setup():
    """Quick setup check before starting server"""
    issues = []

    # Check required files
    if not Path("app/main.py").exists():
        issues.append("app/main.py not found")

    if not Path(".env").exists():
        issues.append(".env file not found")

    # Check if we can import the app
    try:
        sys.path.insert(0, os.getcwd())
        from app.main import app
        print("✅ FastAPI app loaded successfully")
    except Exception as e:
        issues.append(f"Cannot import app: {str(e)[:100]}...")

    return issues


def start_with_uvicorn():
    """Start server using uvicorn directly"""
    try:
        import uvicorn
        from app.main import app

        # Get configuration from environment
        host = os.getenv("HOST", "127.0.0.1")
        port = int(os.getenv("PORT", 8000))
        reload = os.getenv("RELOAD", "true").lower() == "true"

        print(f"🚀 Starting server on http://{host}:{port}")
        print(f"📚 API docs available at http://{host}:{port}/docs")
        print("Press CTRL+C to stop\n")

        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )

    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        return False

    return True


def start_with_subprocess():
    """Fallback: start with subprocess (like the original command)"""
    print("🔄 Falling back to subprocess method...")

    try:
        # Use the same command as in the error log
        cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--reload"]

        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd)
        return result.returncode == 0

    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        return True
    except Exception as e:
        print(f"❌ Subprocess startup failed: {e}")
        return False


def main():
    """Main startup logic"""
    print("🚀 Homework Management System - Server Startup")
    print("=" * 50)

    # Quick setup check
    issues = check_basic_setup()

    if issues:
        print("❌ Setup issues found:")
        for issue in issues:
            print(f"   • {issue}")
        print("\n💡 Try running: python diagnose.py")
        return

    # Try to start server
    print("Starting server...")

    # Method 1: Direct uvicorn import
    if start_with_uvicorn():
        return

    # Method 2: Subprocess fallback
    print("\n🔄 Trying alternative startup method...")
    if start_with_subprocess():
        return

    # If all fails
    print("\n❌ Could not start server with any method")
    print("💡 Try these commands manually:")
    print("   python run.py")
    print("   uvicorn app.main:app --reload")
    print("   python -m uvicorn app.main:app --reload")


if __name__ == "__main__":
    main()