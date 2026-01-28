from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os

from app.nlp_service import process_customer_query, reset_conversation

# ==============================
# FastAPI App
# ==============================
app = FastAPI()

# ==============================
# Base Directories (Docker-safe)
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# ==============================
# Static Files
# ==============================
app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)

# ==============================
# Templates
# ==============================
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# ==============================
# Request Model
# ==============================
class ChatRequest(BaseModel):
    message: str

# ==============================
# UI Route
# ==============================
@app.get("/", response_class=HTMLResponse)
def chat_ui(request: Request):
    reset_conversation()
    return templates.TemplateResponse(
        "chat.html",
        {"request": request}
    )

# ==============================
# Chat API
# ==============================
@app.post("/chat", response_class=JSONResponse)
async def chat_api(request: ChatRequest):
    response = process_customer_query(request.message)
    return response

# ==============================
# Reset Conversation 
# ==============================
@app.post("/reset")
def reset_chat():
    reset_conversation()
    return {"status": "conversation reset"}
