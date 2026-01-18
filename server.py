#!/usr/bin/env python3
"""
Bumi API Server Entry Point for Render deployment.
Run with: uvicorn server:app --host 0.0.0.0 --port 8000
"""

from src.api import create_api_server

app = create_api_server()

if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
