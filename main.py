from fastapi import FastAPI, Request, Response, BackgroundTasks, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import uuid
import os
import sqlite3
from utils import scipris_chatbot, initialize_user_context, user_contexts
from datetime import datetime, timedelta
import json
import time
from models import ConnectionManager, ChatMessage

app = FastAPI()

# Add CORS middleware to handle cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Mount static files for CSS/JS
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Dictionary to store user context by session ID
user_sessions = {}

# WebSocket connection manager
manager = ConnectionManager()

# Session timeout settings (in seconds)
SESSION_TIMEOUT = 30 * 60  # 30 minutes
CLEANUP_INTERVAL = 60 * 60  # 1 hour
last_cleanup_time = time.time()

def cleanup_expired_sessions():
    """Remove expired sessions to prevent memory leaks."""
    global last_cleanup_time
    current_time = time.time()
    
    # Only run cleanup periodically
    if current_time - last_cleanup_time < CLEANUP_INTERVAL:
        return
    
    expired_count = 0
    sessions_to_remove = []
    
    # Find expired sessions
    for session_id, session_data in user_sessions.items():
        last_activity = session_data.get("last_activity", 0)
        if current_time - last_activity > SESSION_TIMEOUT:
            sessions_to_remove.append(session_id)
            
    # Remove expired sessions from both dictionaries
    for session_id in sessions_to_remove:
        if session_id in user_sessions:
            del user_sessions[session_id]
        if session_id in user_contexts:
            del user_contexts[session_id]
        expired_count += 1
    
    if expired_count > 0:
        print(f"Cleaned up {expired_count} expired sessions. Active sessions: {len(user_sessions)}")
    
    last_cleanup_time = current_time


@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request) -> HTMLResponse:
    """Serve the chatbot's HTML interface."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/support", response_class=HTMLResponse)
async def support_chat(request: Request) -> HTMLResponse:
    """Serve the support chat HTML interface."""
    return templates.TemplateResponse("support_chat.html", {"request": request})

@app.post("/ask")
async def ask(request: Request, background_tasks: BackgroundTasks) -> JSONResponse:
    """Handle user chat messages and return chatbot responses along with options if any."""
    try:
        # Run session cleanup in the background
        background_tasks.add_task(cleanup_expired_sessions)
        
        data = await request.json()
        user_message: str = data.get("message", "")
        session_id: str = data.get("session_id", None)
        
        current_time = time.time()
        
        # Create a new session ID if none exists
        if not session_id:
            session_id = str(uuid.uuid4())
            print(f"DEBUG MAIN: Created new session ID: {session_id}")
            user_sessions[session_id] = {
                "created_at": datetime.now().isoformat(),
                "last_activity": current_time
            }
            initialize_user_context(session_id)
        else:
            # If session exists, update its activity time
            if session_id in user_sessions:
                user_sessions[session_id]["last_activity"] = current_time
                print(f"DEBUG MAIN: Using existing session ID: {session_id}")
            else:
                # Only initialize if the session ID is valid but not in our records
                # (server restart case)
                print(f"DEBUG MAIN: Received existing session ID but not found: {session_id} - Restoring it")
                user_sessions[session_id] = {
                    "created_at": datetime.now().isoformat(),
                    "last_activity": current_time
                }
                initialize_user_context(session_id)
        
        # Rate limiting - check if user is sending too many messages
        last_message_time = user_sessions[session_id].get("last_message_time", 0)
        if current_time - last_message_time < 0.3:  # 300ms minimum between messages
            return JSONResponse({
                "response": "Please slow down a bit. I'm processing your previous message.",
                "options": None,
                "session_id": session_id
            })
        
        user_sessions[session_id]["last_message_time"] = current_time
        
        # Get previous context
        previous_context = user_contexts.get(session_id, {}).get("conversation_state")
        print(f"DEBUG MAIN: Before chatbot call - User ID: {session_id}, Previous context: {previous_context}")
        
        # Call the chatbot with user ID to maintain context
        response_text, new_context = scipris_chatbot(user_message, previous_context, session_id)
        print(f"DEBUG MAIN: After chatbot call - Response: '{response_text[:30]}...', New context: {new_context}")
        
        # Update conversation state in user context
        if session_id in user_contexts:
            user_contexts[session_id]["conversation_state"] = new_context
            print(f"DEBUG MAIN: Updated context to: {new_context}")
        else:
            print(f"DEBUG MAIN: User context not found for session: {session_id}")
        
        # Build response object
        response = {
            "response": response_text,
            "options": new_context,
            "session_id": session_id,
            "is_satisfaction_check": False
        }

        # Check if the options are the satisfaction check options
        from utils import SATISFACTION_OPTIONS
        if isinstance(new_context, list) and set(new_context) == set(SATISFACTION_OPTIONS):
            response["is_satisfaction_check"] = True
            
        # Optional: add typing simulation details
        response["char_count"] = len(response_text)  # For dynamic typing speed
        
        # Send message to support agents via WebSocket
        try:
            user_message_for_support = ChatMessage(
                id=str(uuid.uuid4()),
                sender_id=session_id,
                sender_name=f"User ({session_id[:8]})",
                content=user_message,
                timestamp=datetime.now().strftime("%H:%M %p"),
                type="user",
                avatar="https://i.pravatar.cc/150?img=70"
            )
            
            bot_response_for_support = ChatMessage(
                id=str(uuid.uuid4()),
                sender_id="system",
                sender_name="Chatbot",
                content=response_text,
                timestamp=datetime.now().strftime("%H:%M %p"),
                type="system",
                avatar="https://i.pravatar.cc/150?img=7"
            )
            
            # Store messages
            manager.store_message(session_id, user_message_for_support)
            manager.store_message(session_id, bot_response_for_support)
            
            # Broadcast to support
            await manager.broadcast_to_support({
                "type": "new_chat",
                "session_id": session_id,
                "user_message": user_message_for_support.dict(),
                "bot_response": bot_response_for_support.dict()
            })
        except Exception as e:
            print(f"Error sending message to support: {e}")

        return JSONResponse(response)
        
    except Exception as e:
        print(f"Error in ask endpoint: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/session/{session_id}/history")
async def get_session_history(session_id: str) -> JSONResponse:
    """Retrieve conversation history for a given session ID."""
    if session_id not in user_contexts:
        return JSONResponse({"error": "Session not found"}, status_code=404)
        
    history = user_contexts[session_id].get("history", [])
    return JSONResponse({"history": history})

@app.websocket("/ws/user/{user_id}")
async def websocket_user_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for users to connect and receive support messages"""
    try:
        # Connect the user
        await manager.connect_user(user_id, websocket)
        
        # Send message history
        messages = manager.get_message_history(user_id)
        
        if messages:
            await websocket.send_json({
                "type": "message_history",
                "messages": [msg.dict() for msg in messages]
            })
        
        # Keep connection alive and handle user messages
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "user_message":
                # Store the user message
                user_message = ChatMessage(
                    id=str(uuid.uuid4()),
                    sender_id=user_id,
                    sender_name=message_data.get("sender_name", f"User ({user_id[:8]})"),
                    content=message_data.get("content", ""),
                    timestamp=datetime.now().strftime("%H:%M %p"),
                    type="user",
                    avatar="https://i.pravatar.cc/150?img=70"
                )
                
                manager.store_message(user_id, user_message)
                
                # Broadcast to support agents
                await manager.broadcast_to_support({
                    "type": "new_message",
                    "session_id": user_id,
                    "message": user_message.dict()
                })
                
                # Confirm message was received
                await websocket.send_json({
                    "type": "message_received",
                    "message_id": user_message.id
                })
    
    except WebSocketDisconnect:
        # Handle user disconnection
        await manager.disconnect(user_id)
    
    except Exception as e:
        print(f"Error in user WebSocket connection: {e}")
        try:
            await manager.disconnect(user_id)
        except Exception:
            pass  # Ignore errors in disconnection

@app.websocket("/ws/support/{support_id}")
async def websocket_support_endpoint(websocket: WebSocket, support_id: str):
    """WebSocket endpoint for support agents"""
    try:
        await websocket.accept()
        
        # Connect support agent
        await manager.connect_support(support_id, websocket)
        
        # Send list of active chat sessions
        active_sessions = [{
            "session_id": session_id,
            "created_at": session_data.get("created_at", ""),
            "last_activity": session_data.get("last_activity", 0),
            "messages": [msg.dict() for msg in manager.get_message_history(session_id)]
        } for session_id, session_data in user_sessions.items()]
        
        await websocket.send_json({
            "type": "active_sessions",
            "sessions": active_sessions
        })
        
        # Handle messages from support agent
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Handle different message types
            if message_data.get("type") == "support_message":
                session_id = message_data.get("session_id")
                
                if session_id and session_id in user_sessions:
                    message = ChatMessage(
                        id=str(uuid.uuid4()),
                        sender_id=support_id,
                        sender_name="Support Agent",
                        content=message_data.get("content", ""),
                        timestamp=datetime.now().strftime("%H:%M %p"),
                        type="support",
                        avatar="https://i.pravatar.cc/150?img=7"
                    )
                    
                    # Store the message
                    manager.store_message(session_id, message)
                    
                    # Confirm message was stored to support agent
                    await websocket.send_json({
                        "type": "message_stored",
                        "message_id": message.id
                    })
                    
                    # Send message to user via WebSocket if connected
                    was_sent = await manager.send_support_message_to_user(session_id, message)
                    
                    if was_sent:
                        await websocket.send_json({
                            "type": "message_delivered",
                            "message_id": message.id
                        })
    
    except WebSocketDisconnect:
        # Handle support agent disconnection
        try:
            await manager.disconnect(support_id)
        except Exception as e:
            print(f"Error disconnecting support agent: {e}")
    
    except Exception as e:
        print(f"Error in support WebSocket connection: {e}")
        try:
            # Try to disconnect properly
            await manager.disconnect(support_id)
        except Exception:
            pass  # Ignore error if disconnect fails

@app.get("/healthcheck")
async def healthcheck() -> JSONResponse:
    """Health check endpoint for monitoring."""
    # Also check database connectivity
    db_status = "ok"
    try:
        conn = sqlite3.connect("articles.db")
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        conn.close()
    except Exception as e:
        db_status = f"error: {str(e)}"
        
    return JSONResponse({
        "status": "ok",
        "database": db_status,
        "active_sessions": len(user_sessions),
        "active_websockets": len(manager.active_connections),
        "uptime": time.time() - last_cleanup_time
    })

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
