from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime
import random
from fastapi import WebSocket

class ChatMessage(BaseModel):
    """Model representing a chat message"""
    id: str
    sender_id: str
    sender_name: str
    content: str
    timestamp: str
    type: str  # "user", "support", "system"
    avatar: str

class ConnectionManager:
    """Manages WebSocket connections and message history"""
    def __init__(self):
        # {user_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}
        
        # {user_id: bool} - tracks if connections are active
        self.connection_state: Dict[str, bool] = {}
        
        # Support connections - {support_id: WebSocket}
        self.support_connections: Dict[str, WebSocket] = {}
        
        # Message history - {user_id: List[ChatMessage]}
        self.message_history: Dict[str, List[ChatMessage]] = {}

    async def connect_user(self, user_id: str, websocket: WebSocket) -> None:
        """Connect a user"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.connection_state[user_id] = True
        print(f"User {user_id} connected. Total users: {len(self.active_connections)}")
        
        # Notify support agents about this connection
        await self.broadcast_to_support({
            "type": "user_connected",
            "user_id": user_id
        })

    async def connect_support(self, support_id: str, websocket: WebSocket) -> None:
        """Connect a support agent"""
        self.support_connections[support_id] = websocket
        self.connection_state[support_id] = True
        print(f"Support agent {support_id} connected. Total support agents: {len(self.support_connections)}")

    async def disconnect(self, connection_id: str) -> None:
        """Disconnect a user or support agent"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
            self.connection_state[connection_id] = False
            print(f"User {connection_id} disconnected. Total users: {len(self.active_connections)}")
            
            # Notify support agents about this disconnection
            await self.broadcast_to_support({
                "type": "user_disconnected",
                "user_id": connection_id
            })
            
        elif connection_id in self.support_connections:
            del self.support_connections[connection_id]
            self.connection_state[connection_id] = False
            print(f"Support agent {connection_id} disconnected. Total support agents: {len(self.support_connections)}")

    async def send_message(self, message: ChatMessage, recipient_id: str) -> bool:
        """Send a message to a specific connection"""
        try:
            # Check if the connection is active
            if not self.connection_state.get(recipient_id, False):
                print(f"Connection {recipient_id} is not active. Cannot send message.")
                return False
                
            # Check if recipient is a user
            if recipient_id in self.active_connections:
                await self.active_connections[recipient_id].send_json(message.dict())
                return True
            # Check if recipient is a support agent
            elif recipient_id in self.support_connections:
                await self.support_connections[recipient_id].send_json(message.dict())
                return True
            return False
        except Exception as e:
            print(f"Error sending message to {recipient_id}: {e}")
            # Mark connection as inactive
            self.connection_state[recipient_id] = False
            return False

    async def broadcast_to_support(self, message: Any) -> None:
        """Broadcast a message to all support agents"""
        # Create a copy to avoid mutation during iteration
        disconnected_support = []
        
        for support_id, connection in list(self.support_connections.items()):
            # Check if the connection is active before sending
            if not self.connection_state.get(support_id, False):
                disconnected_support.append(support_id)
                continue
                
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to support {support_id}: {e}")
                disconnected_support.append(support_id)
                # Mark as inactive
                self.connection_state[support_id] = False
        
        # Remove disconnected support connections
        for support_id in disconnected_support:
            if support_id in self.support_connections:
                del self.support_connections[support_id]
                
    async def send_support_message_to_user(self, user_id: str, message: ChatMessage) -> bool:
        """Send a support message to a user"""
        if user_id not in self.active_connections:
            return False
            
        try:
            # Store the message
            self.store_message(user_id, message)
            
            # Send to user if they have an active WebSocket connection
            if self.connection_state.get(user_id, False):
                await self.active_connections[user_id].send_json({
                    "type": "support_message",
                    "message": message.dict()
                })
                return True
            return False
        except Exception as e:
            print(f"Error sending support message to user {user_id}: {e}")
            return False

    def store_message(self, user_id: str, message: ChatMessage) -> None:
        """Store a message in the history for a user"""
        if user_id not in self.message_history:
            self.message_history[user_id] = []
        self.message_history[user_id].append(message)
        
        # Limit history to last 100 messages per user
        if len(self.message_history[user_id]) > 100:
            self.message_history[user_id] = self.message_history[user_id][-100:]

    def get_message_history(self, user_id: str) -> List[ChatMessage]:
        """Get message history for a user"""
        return self.message_history.get(user_id, []) 