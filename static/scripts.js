let conversation = [];

function renderConversation() {
    const chatLog = document.getElementById("chat-log");
    chatLog.innerHTML = "";

    conversation.forEach(msg => {
        const div = document.createElement("div");
        div.classList.add("message");
        div.classList.add(msg.sender === "user" ? "user-message" : "bot-message");

        div.innerHTML = `<strong>${msg.sender === "user" ? "You" : "Bot"}:</strong> ${msg.text.replace(/\n/g, "<br>")}`;

        if (msg.options) {
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

    chatLog.scrollTop = chatLog.scrollHeight;
}

function appendMessage(sender, text, options = null) {
    conversation.push({ sender, text, options });
    renderConversation();
}

async function sendMessage(message = null) {
    const inputField = document.getElementById("chatInput");
    const userMessage = message || inputField.value.trim();
    if (!userMessage) return;

    appendMessage("user", userMessage);
    inputField.value = "";

    try {
        const response = await fetch("/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userMessage })
        });

        const data = await response.json();
        appendMessage("bot", data.response, data.options || []);
    } catch (error) {
        console.error("Error:", error);
        appendMessage("bot", "There was an error processing your request.");
    }
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
