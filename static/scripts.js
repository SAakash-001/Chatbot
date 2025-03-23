// Global conversation array to store messages.
let conversation = [];
// Base URL for API calls - making it configurable 
const API_BASE_URL = window.location.origin; // Automatically use the current domain
// Add session ID tracking
let currentSessionId = null;

function renderConversation() {
    const chatLog = document.getElementById("chat-log");
    chatLog.innerHTML = "";

    conversation.forEach(msg => {
        const div = document.createElement("div");
        div.classList.add("message");
        div.classList.add(msg.sender === "user" ? "user-message" : "bot-message");

        div.innerHTML = `<strong>${msg.sender === "user" ? "You" : "Bot"}:</strong> ${msg.text.replace(/\n/g, "<br>")}`;

        if (msg.options && Array.isArray(msg.options) && msg.options.length > 0) {
            const optionsDiv = document.createElement("div");
            optionsDiv.classList.add("options-list");

            msg.options.forEach(option => {
                const btn = document.createElement("button");
                btn.textContent = option;
                btn.onclick = () => sendMessage(option);
                optionsDiv.appendChild(btn);
            });

            div.appendChild(optionsDiv);
        }

        chatLog.appendChild(div);
    });

    // Auto-scroll to the latest message
    chatLog.scrollTop = chatLog.scrollHeight;
}

function appendMessage(sender, text, options = null) {
    if (!text) return; // Prevent adding empty messages
    conversation.push({ sender, text, options });
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

        // Calculate delay based on response length
        const baseTimePerChar = 40 / 10; // 20ms per 10 characters (reduced from 50ms)
        const minDelay = 200; // Minimum delay (reduced from 500ms)
        const maxDelay = 1500; // Maximum delay (reduced from 3000ms)
        const dynamicDelay = Math.min(Math.max(responseText.length * baseTimePerChar, minDelay), maxDelay);

        setTimeout(() => {
            removeTypingIndicator();
            console.log("Final Response:", responseText);
            console.log("Options:", options);
            appendMessage("bot", responseText, options);
        }, dynamicDelay);

    } catch (error) {
        console.error("Error sending message:", error);
        appendMessage("bot", "Network error. Please try again later.");
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
