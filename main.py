"""Compatibility entry point; the application implementation is in app.main."""
import os
import threading
import webbrowser
import uvicorn
from app.main import app


def open_ui_in_browser() -> None:
    webbrowser.open(f"http://127.0.0.1:{os.getenv('PORT', '8000')}")


if __name__ == "__main__":
    if os.getenv("AETHERAI_OPEN_BROWSER", "1").lower() not in {"0", "false", "no"}:
        threading.Timer(1.5, open_ui_in_browser).start()
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
        reload=False,
    )
