"""Main entry point - supports both mock and real API modes"""
import uvicorn
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def main():
    mode = os.getenv("API_MODE", "real")
    
    if mode == "legacy_mock":
        from src.mock.analytics import app
        print("Starting with legacy mock API mode")
    else:
        from src.real_api import app
        print("Starting Seller Analytics API with token-based real/mock mode")
    
    uvicorn.run(
        app,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8090")),
        reload=os.getenv("RELOAD", "false").lower() == "true",
    )


if __name__ == "__main__":
    main()
