"""
JAN MVP Main Application

Entry point for starting the UI and API server.
"""
import uvicorn
from fastapi import FastAPI
import gradio as gr

# Ensure the app can import local modules when running from the root directory
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.app_ui import create_ui

# Create FastAPI app
app = FastAPI(title="JAN MVP API")

# Create Gradio interface
ui = create_ui()

# Mount Gradio onto FastAPI
app = gr.mount_gradio_app(app, ui, path="/")

if __name__ == "__main__":
    print("Starting JAN MVP...")
    # Run server
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
