#!/usr/bin/env python3
"""
FastAPI server startup script for Homework Management System
"""

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def main():
    """Start the FastAPI server"""
    print("🚀 Starting Homework Management API Server")
    print("=" * 50)

    # Configuration
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "true").lower() == "true"

    print(f"📡 Server will run on: http://{host}:{port}")
    print(f"🔄 Auto-reload: {'Enabled' if reload else 'Disabled'}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"🔧 Redoc Documentation: http://{host}:{port}/redoc")
    print("=" * 50)

    # Start server
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()