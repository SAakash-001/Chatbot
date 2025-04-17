// Global conversation array to store messages.
let conversation = [];
// Base URL for API calls - making it configurable 
const API_BASE_URL = window.location.origin; // Automatically use the current domain
// Add session ID tracking
let currentSessionId = null;
// WebSocket connection
let socket = null;
// Connect timeout for reconnection attempts
let connectTimeout = null;
// Reconnect attempt count
let reconnectAttempts = 0;
// Max reconnect attempts
const MAX_RECONNECT_ATTEMPTS = 5;
// Whether support chat is active
let supportChatActive = false;

function renderConversation() {
    const chatLog = document.getElementById("chat-log");
    chatLog.innerHTML = "";

    conversation.forEach(msg => {
        const div = document.createElement("div");
        div.classList.add("message");
        
        if (msg.sender === "user") {
            div.classList.add("user-message");
        } else if (msg.sender === "support") {
            div.classList.add("support-message");
        } else {
            div.classList.add("bot-message");
        }

        const senderName = msg.sender === "user" ? "You" : 
                          msg.sender === "support" ? "Support Agent" : "Bot";
        
        div.innerHTML = `<strong>${senderName}:</strong> ${msg.text.replace(/\n/g, "<br>")}`;

        if (msg.options && Array.isArray(msg.options) && msg.options.length > 0) {
            const optionsDiv = document.createElement("div");
            optionsDiv.classList.add("options-list");
            
            // Apply satisfaction-specific styling if needed
            if (msg.isSatisfactionCheck) {
                optionsDiv.classList.add("satisfaction-options");
            }

            msg.options.forEach(option => {
                const btn = document.createElement("button");
                btn.textContent = option;
                
                // For satisfaction check, if this is the support option, handle it differently
                if (msg.isSatisfactionCheck && option.toLowerCase().includes("human support")) {
                    btn.onclick = () => {
                        // Don't send the message to the chatbot, instead connect to support
                        connectToSupportChat();
                    };
                } else {
                btn.onclick = () => sendMessage(option);
                }
                
                // Apply specific class for satisfaction buttons
                if (msg.isSatisfactionCheck) {
                    btn.classList.add("satisfaction-btn");
                    
                    // Add appropriate icon class based on the option
                    if (option.includes("satisfied")) {
                        btn.classList.add("satisfied-btn");
                    } else if (option.includes("support")) {
                        btn.classList.add("support-btn");
                    }
                }
                
                optionsDiv.appendChild(btn);
            });

            div.appendChild(optionsDiv);
        }

        chatLog.appendChild(div);
    });

    // Auto-scroll to the latest message
    chatLog.scrollTop = chatLog.scrollHeight;
}

function appendMessage(sender, text, options = null, isSatisfactionCheck = false) {
    if (!text) return; // Prevent adding empty messages
    conversation.push({ sender, text, options, isSatisfactionCheck });
    renderConversation();
}

async function sendMessage(message = null) {
    const inputBox = document.getElementById("chatInput");
    if (!inputBox) {
        console.error("Error: chatInput is not defined in the DOM.");
        return;
    }

    const userInput = message || inputBox.value.trim();
    if (!userInput) return;

    appendMessage("user", userInput);
    inputBox.value = "";

    console.log("Sending message with session ID:", currentSessionId);

    // If support chat is active, send via WebSocket only and don't use chatbot
    if (supportChatActive && socket && socket.readyState === WebSocket.OPEN) {
        try {
            socket.send(JSON.stringify({
                type: "user_message",
                content: userInput,
                sender_name: "User"
            }));
            return;
        } catch (error) {
            console.error("Error sending WebSocket message:", error);
            // If WebSocket fails when in support mode, notify the user
            appendMessage("bot", "Error sending message to support agent. Please try again.");
            return;
        }
    }

    try {
        const response = await fetch(`${API_BASE_URL}/ask`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                message: userInput,
                session_id: currentSessionId // Send the current session ID if we have one
            })
        });

        if (!response.ok) {
            console.error("Server responded with an error:", response.status);
            appendMessage("bot", "I'm sorry, something went wrong. Please try again.");
            return;
        }

        const data = await response.json();
        console.log("Backend Response:", data); // Debugging log
        
        // Save the session ID for future requests
        if (data.session_id) {
            console.log("Received session ID:", data.session_id);
            if (currentSessionId !== data.session_id) {
                console.log("Session ID changed from", currentSessionId, "to", data.session_id);
            }
            currentSessionId = data.session_id;
        }

        // Show a typing indicator before showing the actual response
        showTypingIndicator();

        // Simulate a delay (e.g., 800ms) before displaying the actual response
        const responseText = data.response || "I'm sorry, no response received.";
        const options = Array.isArray(data.options) ? data.options : [];
        const isSatisfactionCheck = data.is_satisfaction_check || false;

        // Calculate delay based on response length
        const baseTimePerChar = 40 / 10; // 20ms per 10 characters (reduced from 50ms)
        const minDelay = 200; // Minimum delay (reduced from 500ms)
        const maxDelay = 1500; // Maximum delay (reduced from 3000ms)
        const dynamicDelay = Math.min(Math.max(responseText.length * baseTimePerChar, minDelay), maxDelay);

        setTimeout(() => {
            removeTypingIndicator();
            console.log("Final Response:", responseText);
            console.log("Options:", options);
            console.log("Is Satisfaction Check:", isSatisfactionCheck);
            appendMessage("bot", responseText, options, isSatisfactionCheck);
        }, dynamicDelay);

    } catch (error) {
        console.error("Error sending message:", error);
        appendMessage("bot", "Network error. Please try again later.");
    }
}

function connectToSupportChat() {
    if (!currentSessionId) {
        appendMessage("bot", "Unable to connect to support without a session ID. Please try asking a question first.");
        return;
    }
    
    supportChatActive = true;
    appendMessage("bot", "Connecting you to a support agent. Please wait a moment...");
    
    // Initialize WebSocket connection
    initWebSocket();
    
    // Update UI to indicate support mode is active
    document.querySelector('.chat-header').classList.add('support-mode');
    const chatHeader = document.querySelector('.chat-header');
    if (chatHeader) {
        chatHeader.innerHTML = '<i class="fas fa-headset"></i> Support Chat';
    }
}

function initWebSocket() {
    if (socket && socket.readyState === WebSocket.OPEN) {
        console.log("WebSocket already connected");
        return;
    }
    
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const socketUrl = `${protocol}//${window.location.host}/ws/user/${currentSessionId}`;
    
    console.log("Connecting to WebSocket:", socketUrl);
    
    try {
        socket = new WebSocket(socketUrl);
        
        socket.onopen = function() {
            console.log("WebSocket connection established");
            // Reset reconnect attempts on successful connection
            reconnectAttempts = 0;
            appendMessage("bot", "Connected to support. A support agent will assist you shortly.");
        };
        
        socket.onmessage = function(event) {
            handleSocketMessage(event.data);
        };
        
        socket.onclose = function() {
            console.log("WebSocket connection closed");
            
            // Try to reconnect if support chat is still active
            if (supportChatActive && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
                reconnectAttempts++;
                console.log(`Attempting to reconnect (${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})...`);
                
                // Exponential backoff for reconnection
                const backoffTime = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
                connectTimeout = setTimeout(initWebSocket, backoffTime);
            } else if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
                appendMessage("bot", "Unable to maintain connection to support. Please try again later.");
                supportChatActive = false;
                
                // Reset UI to normal mode
                document.querySelector('.chat-header').classList.remove('support-mode');
                const chatHeader = document.querySelector('.chat-header');
                if (chatHeader) {
                    chatHeader.innerHTML = 'SciPris Chatbot';
                }
            }
        };
        
        socket.onerror = function(error) {
            console.error("WebSocket error:", error);
        };
    } catch (error) {
        console.error("Error initializing WebSocket:", error);
        appendMessage("bot", "Error connecting to support. Please try again later.");
        supportChatActive = false;
        
        // Reset UI to normal mode
        document.querySelector('.chat-header').classList.remove('support-mode');
        const chatHeader = document.querySelector('.chat-header');
        if (chatHeader) {
            chatHeader.innerHTML = 'SciPris Chatbot';
        }
    }
}

function handleSocketMessage(data) {
    try {
        const message = JSON.parse(data);
        console.log("Received WebSocket message:", message);
        
        switch (message.type) {
            case "message_history":
                // Handle message history
                if (message.messages && Array.isArray(message.messages)) {
                    message.messages.forEach(msg => {
                        if (msg.type === "support") {
                            appendMessage("support", msg.content);
                        }
                    });
                }
                break;
                
            case "support_message":
                // Handle incoming support message
                if (message.message) {
                    appendMessage("support", message.message.content);
                }
                break;
                
            case "message_received":
                // Message acknowledgment
                console.log("Message received by server:", message.message_id);
                break;
        }
    } catch (error) {
        console.error("Error handling WebSocket message:", error, data);
    }
}

function showTypingIndicator() {
    appendMessage("bot", "Bot is typing...", []);
}

function removeTypingIndicator() {
    if (conversation.length > 0 && conversation[conversation.length - 1].text === "Bot is typing...") {
        conversation.pop();
    }
    renderConversation();
}


document.getElementById("chatInput").addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        event.preventDefault();
        sendMessage();
    }
});

window.onload = function () {
    appendMessage("bot", "Welcome to SciPris Chatbot! Please choose one of the following options:", [
        "Payment Failure", "Refund Issues", "Invoice Requests", "Other Payment Queries"
    ]);
};
