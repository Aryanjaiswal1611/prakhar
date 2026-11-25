"""Convenience entrypoint for running from the backend directory.

Preferred: uvicorn app.main:app --reload --port 8000
Also supported: uvicorn main:app --reload --port 8000
"""
from app.main import app  # noqa: F401

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
