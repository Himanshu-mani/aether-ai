from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import webbrowser
import threading
from api.chat_routes import router as chat_router
from core.config import DOWNLOADS_DIR, UPLOADS_DIR, CHROMA_DIR

# Workspace folders check
os.makedirs(DOWNLOADS_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True) # ✨ UPDATE: Vector database folder
os.makedirs("frontend", exist_ok=True) # Ensure frontend folder exists

app = FastAPI(title="AI Chatbot API")

# CORS Configuration (Prevents UI and Backend conflicts)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Routes: Connecting Backend API
app.include_router(chat_router, prefix="/api")

# 2. Downloads: Making download folder public
app.mount("/downloads", StaticFiles(directory=DOWNLOADS_DIR), name="downloads")

# 3. Static Files: Fixed 404 error for CSS and JS files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# 4. Frontend: Hosting the UI (Must be placed last)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

# Function to automatically open the browser
def open_ui_in_browser():
    print("▶ AI Chatbot is launching...")
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    import uvicorn
    
    # Open browser 1.5 seconds after server starts
    threading.Timer(1.5, open_ui_in_browser).start()
    
    # Command to run the server
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
