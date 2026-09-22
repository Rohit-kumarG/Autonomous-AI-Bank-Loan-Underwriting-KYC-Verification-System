"""
Entrypoint to start the Autonomous Banking Underwriting Server.
"""

import uvicorn
from config.settings import settings

if __name__ == "__main__":
    print(f"🚀 Starting {settings.APP_NAME} on http://{settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
