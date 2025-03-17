from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from utils import scipris_chatbot

app = FastAPI()

# Mount static files for CSS/JS
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Dictionary to store user context (e.g., awaiting DOI/title for invoice issues)
user_context: dict = {}

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request) -> HTMLResponse:
    """Serve the chatbot's HTML interface."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ask")
async def ask(request: Request) -> JSONResponse:
    """Handle user chat messages and return chatbot responses along with options if any."""
    try:
        data = await request.json()
        user_message: str = data.get("message", "")
        
        # Track users by IP (use session ID in production)
        user_id: str = request.client.host  
        previous_context = user_context.get(user_id, None)
        
        response_text, new_context = scipris_chatbot(user_message, previous_context)
        
        # Update user context
        user_context[user_id] = new_context

        return JSONResponse({"response": response_text, "options": new_context})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
