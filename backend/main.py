"""Vercel/FastAPI service entrypoint.

The application implementation lives under ``app`` so it remains a normal
installable Python package, while Vercel Services can import ``main:app`` from
this service root.
"""

from app.main import app

__all__ = ["app"]
