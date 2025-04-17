// Sample data for demonstration
const users = [
    {
        id: 1,
        name: "Jhon Snow",
        avatar: "https://i.pravatar.cc/150?img=12",
        lastMessage: "Thanks a lot",
        timestamp: "09:54 am",
        unread: false
    },
    {
        id: 2,
        name: "Dianne Russell",
        avatar: "https://i.pravatar.cc/150?img=5",
        lastMessage: "Pre Chat Form Submitted",
        timestamp: "09:54 am",
        unread: false
    },
    {
        id: 3,
        name: "Albert Flores",
        avatar: "https://i.pravatar.cc/150?img=8",
        lastMessage: "A report that has been done...",
        timestamp: "09:54 am",
        unread: false
    },
    {
        id: 4,
        name: "مقصود",
        avatar: "https://i.pravatar.cc/150?img=3",
        lastMessage: "I understand, but I was hoping...",
        timestamp: "09:54 am",
        unread: false
    },
    {
        id: 5,
        name: "মরিয়ুল ইসলাম",
        avatar: "https://i.pravatar.cc/150?img=10",
        lastMessage: "Thank you for providing the information",
        timestamp: "09:54 am",
        unread: true,
        badge: 3
    },
    {
        id: 6,
        name: "Rina Rumana Remu",
        avatar: "https://i.pravatar.cc/150?img=1",
        lastMessage: "[draft] Sure, you can...",
        timestamp: "3m 20s",
        unread: false
    }
];

const chats = {
    2: [
        {
            id: 1,
            sender: "Dianne Russell",
            senderAvatar: "https://i.pravatar.cc/150?img=5",
            content: "Hi, I need some help with my loan application.",
            timestamp: "11:50 pm",
            type: "received"
        },
        {
            id: 2,
            sender: "Rafi",
            senderAvatar: "https://i.pravatar.cc/150?img=7",
            content: "Hello! I'd be happy to assist you. Could you please provide more details about the issue?",
            timestamp: "11:51 pm",
            type: "sent"
        },
        {
            id: 3,
            sender: "Dianne Russell",
            senderAvatar: "https://i.pravatar.cc/150?img=5",
            content: "I submitted my application a few days ago, but I haven't received any updates yet.",
            timestamp: "11:53 pm",
            type: "received"
        },
        {
            id: 4,
            sender: "Rafi",
            senderAvatar: "https://i.pravatar.cc/150?img=7",
            content: "Sure! May I have your application reference number?",
            timestamp: "11:54 pm",
            type: "sent"
        },
        {
            id: 5,
            sender: "Dianne Russell",
            senderAvatar: "https://i.pravatar.cc/150?img=5",
            content: "My reference number is #543434",
            timestamp: "11:57 pm",
            type: "received"
        },
        {
            id: 6,
            sender: "Jhonat",
            senderAvatar: "https://i.pravatar.cc/150?img=9",
            content: "Admin message",
            timestamp: "11:58 pm",
            type: "admin"
        }
    ],
    1: [
        {
            id: 1,
            sender: "Jhon Snow",
            senderAvatar: "https://i.pravatar.cc/150?img=12",
            content: "Thank you for your quick response!",
            timestamp: "09:50 am",
            type: "received"
        },
        {
            id: 2,
            sender: "Rafi",
            senderAvatar: "https://i.pravatar.cc/150?img=7",
            content: "You're welcome! Let me know if you need anything else.",
            timestamp: "09:52 am",
            type: "sent"
        },
        {
            id: 3,
            sender: "Jhon Snow",
            senderAvatar: "https://i.pravatar.cc/150?img=12",
            content: "Thanks a lot",
            timestamp: "09:54 am",
            type: "received"
        }
    ],
    3: [
        {
            id: 1,
            sender: "Albert Flores",
            senderAvatar: "https://i.pravatar.cc/150?img=8",
            content: "I need to submit a report on my recent purchase.",
            timestamp: "09:45 am",
            type: "received"
        },
        {
            id: 2,
            sender: "Rafi",
            senderAvatar: "https://i.pravatar.cc/150?img=7",
            content: "I can help you with that. What details do you have?",
            timestamp: "09:48 am",
            type: "sent"
        },
        {
            id: 3,
            sender: "Albert Flores",
            senderAvatar: "https://i.pravatar.cc/150?img=8",
            content: "A report that has been done...",
            timestamp: "09:54 am",
            type: "received"
        }
    ],
    4: [
        {
            id: 1,
            sender: "مقصود",
            senderAvatar: "https://i.pravatar.cc/150?img=3",
            content: "Could you explain the shipping policy again?",
            timestamp: "09:40 am",
            type: "received"
        },
        {
            id: 2,
            sender: "Rafi",
            senderAvatar: "https://i.pravatar.cc/150?img=7",
            content: "Certainly! Our shipping takes 3-5 business days within the country.",
            timestamp: "09:45 am",
            type: "sent"
        },
        {
            id: 3,
            sender: "مقصود",
            senderAvatar: "https://i.pravatar.cc/150?img=3",
            content: "I understand, but I was hoping...",
            timestamp: "09:54 am",
            type: "received"
        }
    ],
    5: [
        {
            id: 1,
            sender: "মরিয়ুল ইসলাম",
            senderAvatar: "https://i.pravatar.cc/150?img=10",
            content: "I need information about my account status.",
            timestamp: "09:30 am",
            type: "received"
        },
        {
            id: 2,
            sender: "Rafi",
            senderAvatar: "https://i.pravatar.cc/150?img=7",
            content: "I'll need some verification details first. Can you provide your account ID?",
            timestamp: "09:35 am",
            type: "sent"
        },
        {
            id: 3,
            sender: "মরিয়ুল ইসলাম",
            senderAvatar: "https://i.pravatar.cc/150?img=10",
            content: "Thank you for providing the information",
            timestamp: "09:54 am",
            type: "received"
        }
    ],
    6: [
        {
            id: 1,
            sender: "Rina Rumana Remu",
            senderAvatar: "https://i.pravatar.cc/150?img=1",
            content: "Do you have that product in blue color?",
            timestamp: "3m 05s",
            type: "received"
        },
        {
            id: 2,
            sender: "Rafi",
            senderAvatar: "https://i.pravatar.cc/150?img=7",
            content: "Let me check our inventory for you.",
            timestamp: "3m 10s",
            type: "sent"
        },
        {
            id: 3,
            sender: "Rina Rumana Remu",
            senderAvatar: "https://i.pravatar.cc/150?img=1",
            content: "[draft] Sure, you can...",
            timestamp: "3m 20s",
            type: "received"
        }
    ]
};

// User information
const userDetails = {
    1: {
        name: "Jhon Snow",
        phone: "+18505551234",
        email: "jhon.snow@example.com",
        visitorType: "New",
        gender: "Male",
        location: "New York, USA",
        mapImage: "https://maps.googleapis.com/maps/api/staticmap?center=New+York,USA&zoom=12&size=400x120&key=YOUR_API_KEY"
    },
    2: {
        name: "Dianne Russell",
        phone: "+8801684610691",
        email: "dianne_rll@gmail.com",
        visitorType: "Repeat",
        gender: "Male",
        location: "Dhaka, Bangladesh",
        mapImage: "https://maps.googleapis.com/maps/api/staticmap?center=Dhaka,Bangladesh&zoom=12&size=400x120&key=YOUR_API_KEY"
    },
    3: {
        name: "Albert Flores",
        phone: "+14155552671",
        email: "albert.flores@example.com",
        visitorType: "Repeat",
        gender: "Male",
        location: "Chicago, USA",
        mapImage: "https://maps.googleapis.com/maps/api/staticmap?center=Chicago,USA&zoom=12&size=400x120&key=YOUR_API_KEY"
    },
    4: {
        name: "مقصود",
        phone: "+971501234567",
        email: "maqsood@example.com",
        visitorType: "New",
        gender: "Male",
        location: "Dubai, UAE",
        mapImage: "https://maps.googleapis.com/maps/api/staticmap?center=Dubai,UAE&zoom=12&size=400x120&key=YOUR_API_KEY"
    },
    5: {
        name: "মরিয়ুল ইসলাম",
        phone: "+8801712345678",
        email: "moriulislam@example.com",
        visitorType: "Repeat",
        gender: "Male",
        location: "Chittagong, Bangladesh",
        mapImage: "https://maps.googleapis.com/maps/api/staticmap?center=Chittagong,Bangladesh&zoom=12&size=400x120&key=YOUR_API_KEY"
    },
    6: {
        name: "Rina Rumana Remu",
        phone: "+8801987654321",
        email: "rina.remu@example.com",
        visitorType: "New",
        gender: "Female",
        location: "Sylhet, Bangladesh",
        mapImage: "https://maps.googleapis.com/maps/api/staticmap?center=Sylhet,Bangladesh&zoom=12&size=400x120&key=YOUR_API_KEY"
    }
};

// WebSocket connection variables
let socket;
const supportId = 'support_' + Date.now().toString(36);
let liveGuests = {}; // Store connected guests from WebSocket

// Current state
let currentUserId = null;

// DOM elements
const userListElement = document.getElementById('userList');
const chatMessagesElement = document.getElementById('chatMessages');
const messageInputElement = document.getElementById('messageInput');
const sendMessageButton = document.getElementById('sendMessage');
const currentUserNameElement = document.getElementById('currentUserName');
const currentUserAvatarElement = document.getElementById('currentUserAvatar');
const userDetailsElement = document.getElementById('userDetails');
const assigneeNameElement = document.getElementById('assigneeName');
const assigneeAvatarElement = document.getElementById('assigneeAvatar');

// Initialize the application
function init() {
    renderUserList();
    addEventListeners();
    connectWebSocket();
    
    // Select the first user by default
    if (users.length > 0) {
        selectUser(2); // Select Dianne Russell by default
    }
}

// Connect to WebSocket
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const socketUrl = `${protocol}//${window.location.host}/ws/support/${supportId}`;
    
    console.log('Connecting to WebSocket:', socketUrl);
    socket = new WebSocket(socketUrl);
    
    socket.onopen = function(e) {
        console.log('WebSocket connection established');
        showSystemMessage('Connected to support chat server');
    };
    
    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        console.log('Received message:', data);
        
        handleSocketMessage(data);
    };
    
    socket.onclose = function(event) {
        console.log('WebSocket connection closed:', event);
        showSystemMessage('Disconnected from chat server. Trying to reconnect...');
        
        // Try to reconnect after a delay
        setTimeout(connectWebSocket, 3000);
    };
    
    socket.onerror = function(error) {
        console.error('WebSocket error:', error);
        showSystemMessage('Error connecting to chat server');
    };
}

// Handle incoming WebSocket messages
function handleSocketMessage(data) {
    switch (data.type) {
        case 'active_sessions':
            // Update the list of connected guests
            updateActiveSessionsList(data.sessions);
            break;
        
        case 'user_connected':
            // Add new guest to the list
            addNewUser(data.user_id);
            break;
        
        case 'user_disconnected':
            // Handle guest disconnection
            handleUserDisconnection(data.user_id);
            break;
        
        case 'new_chat':
            // Handle new chat messages
            handleNewChat(data.session_id, data.user_message, data.bot_response);
            break;
            
        case 'new_message':
            // Handle single new message
            handleNewMessage(data.session_id, data.message);
            break;
        
        case 'message_stored':
            // Confirmation that message was stored
            console.log('Message stored:', data.message_id);
            break;
            
        case 'message_delivered':
            // Confirmation that message was delivered to the user
            console.log('Message delivered to user:', data.message_id);
            showSystemMessage('Message delivered to user');
            break;
    }
}

// Add a new user to the list
function addNewUser(userId) {
    // Check if this is a known user or a new one
    if (liveGuests[userId]) {
        // Update existing user
        liveGuests[userId].isOnline = true;
    } else {
        // Create a new user entry
        liveGuests[userId] = {
            id: userId,
            name: `User (${userId.substring(0, 8)})`,
            avatar: "https://i.pravatar.cc/150?img=70",
            isOnline: true,
            lastActivity: new Date()
        };
    }
    
    // Create a notification sound
    playNotificationSound();
    
    // Show a system message
    showSystemMessage(`New user connected: ${liveGuests[userId].name}`);
    
    // Update the UI
    renderLiveGuests();
}

// Handle user disconnection
function handleUserDisconnection(userId) {
    if (liveGuests[userId]) {
        const userName = liveGuests[userId].name;
        showSystemMessage(`User disconnected: ${userName}`);
        
        // Mark user as offline in our list
        liveGuests[userId].isOnline = false;
        renderLiveGuests();
    }
}

// Handle a new chat (both user message and bot response)
function handleNewChat(userId, userMessage, botResponse) {
    if (!chats[userId]) {
        chats[userId] = [];
    }
    
    // Create user message object in our local format
    const userMessageObj = {
        id: userMessage.id,
        sender: userMessage.sender_name,
        senderAvatar: userMessage.avatar,
        content: userMessage.content,
        timestamp: userMessage.timestamp,
        type: "received"
    };
    
    // Create bot response object in our local format
    const botResponseObj = {
        id: botResponse.id,
        sender: botResponse.sender_name,
        senderAvatar: botResponse.avatar,
        content: botResponse.content,
        timestamp: botResponse.timestamp,
        type: "system"
    };
    
    // Add to chat history
    chats[userId].push(userMessageObj);
    chats[userId].push(botResponseObj);
    
    // If this is the currently selected user, update the chat display
    if (currentUserId === userId) {
        renderChatMessages(userId);
    } else {
        // Otherwise, mark the user as having unread messages
        updateUserWithUnread(userId);
    }
    
    // Play notification sound
    playNotificationSound();
    
    // Add or update the user in our live guests list
    if (!liveGuests[userId]) {
        liveGuests[userId] = {
            id: userId,
            name: userMessage.sender_name,
            avatar: userMessage.avatar,
            isOnline: true,
            lastActivity: new Date(),
            lastMessage: userMessage.content
        };
        showSystemMessage(`New user connected: ${userMessage.sender_name}`);
    } else {
        // Update last activity time
        liveGuests[userId].lastActivity = new Date();
        liveGuests[userId].isOnline = true;
        liveGuests[userId].lastMessage = userMessage.content;
    }
    
    // Update the UI
    renderLiveGuests();
}

// Handle a new message from a user
function handleNewMessage(userId, message) {
    if (!chats[userId]) {
        chats[userId] = [];
    }
    
    // Create a message object in our local format
    const newMessage = {
        id: message.id,
        sender: message.sender_name,
        senderAvatar: message.avatar,
        content: message.content,
        timestamp: message.timestamp,
        type: "received"
    };
    
    // Add to chat history
    chats[userId].push(newMessage);
    
    // If this is the currently selected user, update the chat display
    if (currentUserId === userId) {
        renderChatMessages(userId);
    } else {
        // Otherwise, mark the user as having unread messages
        updateUserWithUnread(userId);
    }
    
    // Play notification sound
    playNotificationSound();
    
    // Add or update the user in our live guests list
    if (!liveGuests[userId]) {
        addNewUser(userId);
    } else {
        // Update last activity time
        liveGuests[userId].lastActivity = new Date();
        liveGuests[userId].isOnline = true;
        liveGuests[userId].lastMessage = message.content;
        renderLiveGuests();
    }
}

// Update a list of active chat sessions
function updateActiveSessionsList(sessions) {
    sessions.forEach(session => {
        const userId = session.session_id;
        
        // Create or update user in our live guests list
        if (!liveGuests[userId]) {
            liveGuests[userId] = {
                id: userId,
                name: `User (${userId.substring(0, 8)})`,
                avatar: "https://i.pravatar.cc/150?img=70",
                isOnline: true,
                lastActivity: new Date()
            };
        }
        
        // Process messages
        if (session.messages && session.messages.length > 0) {
            // Create chat history for this user if it doesn't exist
            if (!chats[userId]) {
                chats[userId] = [];
            }
            
            // Process each message
            session.messages.forEach(msg => {
                // Convert to our local format
                const newMessage = {
                    id: msg.id,
                    sender: msg.sender_name,
                    senderAvatar: msg.avatar,
                    content: msg.content,
                    timestamp: msg.timestamp,
                    type: msg.type === "user" ? "received" : 
                          msg.type === "support" ? "sent" : "system"
                };
                
                // Check if we already have this message (avoid duplicates)
                const existingMessageIndex = chats[userId].findIndex(m => m.id === newMessage.id);
                if (existingMessageIndex === -1) {
                    chats[userId].push(newMessage);
                }
            });
            
            // Update last message info
            const lastMessage = session.messages[session.messages.length - 1];
            liveGuests[userId].lastMessage = lastMessage.content;
        }
    });
    
    // Update the UI
    renderLiveGuests();
}

// Render live guests in the user list
function renderLiveGuests() {
    // We'll add live guests at the top of the list
    const existingUserIds = users.map(u => u.id);
    
    // Create a list of guest users to display in the UI
    const guestUsers = Object.entries(liveGuests).map(([guestId, guest]) => {
        return {
            id: guestId,
            name: guest.name,
            avatar: guest.avatar || "https://i.pravatar.cc/150?img=70",
            lastMessage: "New conversation started",
            timestamp: formatTimestamp(new Date()),
            unread: false,
            isLive: true,
            isOnline: guest.isOnline !== false
        };
    });
    
    // Re-render the user list
    renderUserList(guestUsers);
}

// Mark a user as having unread messages
function updateUserWithUnread(userId) {
    const userItem = document.querySelector(`.user-item[data-user-id="${userId}"]`);
    if (userItem) {
        userItem.classList.add('unread');
        
        // Check if badge exists
        let badge = userItem.querySelector('.user-badge');
        if (badge) {
            // Increment badge count
            const count = parseInt(badge.textContent) || 0;
            badge.textContent = count + 1;
        } else {
            // Create new badge
            badge = document.createElement('div');
            badge.className = 'user-badge';
            badge.textContent = '1';
            userItem.appendChild(badge);
        }
    }
}

// Play notification sound
function playNotificationSound() {
    const audio = new Audio('/static/notification.mp3');
    audio.play().catch(e => console.log('Unable to play notification sound'));
}

// Show a system message in the chat
function showSystemMessage(message) {
    if (!chatMessagesElement) return;
    
    const messageElement = document.createElement('div');
    messageElement.className = 'system-message';
    messageElement.textContent = message;
    
    chatMessagesElement.appendChild(messageElement);
    chatMessagesElement.scrollTop = chatMessagesElement.scrollHeight;
}

// Render the list of users in the sidebar
function renderUserList(guestUsers = []) {
    userListElement.innerHTML = '';
    
    // Display live guests first
    const liveUsersSection = document.createElement('div');
    liveUsersSection.className = 'users-section';
    liveUsersSection.innerHTML = '<div class="section-header">Live Guests</div>';
    
    guestUsers.forEach(user => {
        const userItemElement = document.createElement('div');
        userItemElement.className = `user-item ${user.id === currentUserId ? 'active' : ''} ${user.isOnline === false ? 'offline' : ''}`;
        userItemElement.dataset.userId = user.id;
        
        let badge = '';
        if (user.badge) {
            badge = `<div class="user-badge">${user.badge}</div>`;
        }
        
        let statusIndicator = '';
        if (user.isLive) {
            statusIndicator = `<div class="status-dot ${user.isOnline !== false ? 'online' : 'offline'}"></div>`;
        }
        
        userItemElement.innerHTML = `
            ${statusIndicator}
            <img src="${user.avatar}" alt="${user.name}" class="avatar">
            <div class="user-content">
                <div class="user-name-row">
                    <div class="user-name">${user.name}</div>
                    <div class="timestamp">${user.timestamp}</div>
                </div>
                <div class="last-message">${user.lastMessage}</div>
            </div>
            ${badge}
        `;
        
        userItemElement.addEventListener('click', () => selectUser(user.id));
        liveUsersSection.appendChild(userItemElement);
    });
    
    if (guestUsers.length > 0) {
        userListElement.appendChild(liveUsersSection);
    }
    
    // Display static users in "Previous Chats" section
    const previousChatsSection = document.createElement('div');
    previousChatsSection.className = 'users-section';
    previousChatsSection.innerHTML = '<div class="section-header">Previous Chats</div>';
    
    users.forEach(user => {
        const userItemElement = document.createElement('div');
        userItemElement.className = `user-item ${user.id === currentUserId ? 'active' : ''}`;
        userItemElement.dataset.userId = user.id;
        
        let badge = '';
        if (user.badge) {
            badge = `<div class="user-badge">${user.badge}</div>`;
        }
        
        userItemElement.innerHTML = `
            <img src="${user.avatar}" alt="${user.name}" class="avatar">
            <div class="user-content">
                <div class="user-name-row">
                    <div class="user-name">${user.name}</div>
                    <div class="timestamp">${user.timestamp}</div>
                </div>
                <div class="last-message">${user.lastMessage}</div>
            </div>
            ${badge}
        `;
        
        userItemElement.addEventListener('click', () => selectUser(user.id));
        previousChatsSection.appendChild(userItemElement);
    });
    
    userListElement.appendChild(previousChatsSection);
}

// Select a user and show their chat
function selectUser(userId) {
    currentUserId = userId;
    
    // Update active user in the list
    document.querySelectorAll('.user-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.userId === userId.toString()) {
            item.classList.add('active');
            
            // Clear unread indicator
            item.classList.remove('unread');
            const badge = item.querySelector('.user-badge');
            if (badge) {
                badge.remove();
            }
        }
    });
    
    // Update header with user info
    let user = users.find(u => u.id.toString() === userId.toString());
    
    // If not found in static users, check live guests
    if (!user && liveGuests[userId]) {
        user = {
            id: userId,
            name: liveGuests[userId].name,
            avatar: liveGuests[userId].avatar
        };
    }
    
    if (user) {
        currentUserNameElement.textContent = user.name;
        currentUserAvatarElement.src = user.avatar;
    }
    
    // Load chat messages
    renderChatMessages(userId);
    
    // Load user details
    renderUserDetails(userId);
}

// Render chat messages for a user
function renderChatMessages(userId) {
    chatMessagesElement.innerHTML = '';
    
    const messages = chats[userId] || [];
    
    messages.forEach(message => {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${message.type}`;
        
        messageElement.innerHTML = `
            <div class="message-sender">
                <img src="${message.senderAvatar}" alt="${message.sender}" class="avatar small-avatar">
                <div class="sender-name">${message.sender}</div>
                <div class="message-time">${message.timestamp}</div>
            </div>
            <div class="message-content">${message.content}</div>
        `;
        
        chatMessagesElement.appendChild(messageElement);
    });
    
    // Scroll to bottom
    chatMessagesElement.scrollTop = chatMessagesElement.scrollHeight;
}

// Render user details in the info sidebar
function renderUserDetails(userId) {
    // Check if we have details in our static data
    let details = userDetails[userId];
    
    // If not found in static data, check live guests
    if (!details && liveGuests[userId]) {
        const guest = liveGuests[userId];
        details = {
            name: guest.name,
            email: guest.email || "No email provided",
            phone: "Not available",
            visitorType: "Guest",
            gender: "Not specified",
            location: "Unknown location",
            mapImage: "https://maps.googleapis.com/maps/api/staticmap?center=0,0&zoom=1&size=400x120&key=YOUR_API_KEY"
        };
    }
    
    if (!details) return;
    
    // Set assignee info
    assigneeNameElement.textContent = "Rafi Ahmed";
    assigneeAvatarElement.src = "https://i.pravatar.cc/150?img=7";
    
    // User details
    userDetailsElement.innerHTML = `
        <div class="info-row">
            <div class="info-label">Name</div>
            <div class="info-value">${details.name}</div>
        </div>
        <div class="info-row">
            <div class="info-label">Phone</div>
            <div class="info-value">${details.phone}</div>
        </div>
        <div class="info-row">
            <div class="info-label">Email</div>
            <div class="info-value">${details.email}</div>
        </div>
        <div class="info-row">
            <div class="info-label">Visitor Type</div>
            <div class="info-value">${details.visitorType}</div>
        </div>
        <div class="info-row">
            <div class="info-label">Gender</div>
            <div class="info-value">${details.gender}</div>
        </div>
        <div class="info-row">
            <div class="info-label">Location</div>
            <div class="info-value">${details.location}</div>
        </div>
        <div class="location-map">
            <img src="${details.mapImage}" alt="Location Map">
        </div>
    `;
}

// Send a message to the current user
function sendMessage() {
    const content = messageInputElement.value.trim();
    if (!content || !currentUserId) return;
    
    // Create new message
    const newMessage = {
        id: Date.now(),
        sender: "Rafi",
        senderAvatar: "https://i.pravatar.cc/150?img=7",
        content: content,
        timestamp: formatTimestamp(new Date()),
        type: "sent"
    };
    
    // Add to local chat history
    if (!chats[currentUserId]) {
        chats[currentUserId] = [];
    }
    chats[currentUserId].push(newMessage);
    
    // Clear input
    messageInputElement.value = '';
    
    // Sending via WebSocket
    if (socket && socket.readyState === WebSocket.OPEN) {
        const socketMessage = {
            type: "support_message",
            session_id: currentUserId,
            content: content
        };
        
        socket.send(JSON.stringify(socketMessage));
    }
    
    // Render updated chat
    renderChatMessages(currentUserId);
}

// Format timestamp
function formatTimestamp(date) {
    let hours = date.getHours();
    const minutes = date.getMinutes();
    const ampm = hours >= 12 ? 'pm' : 'am';
    
    hours = hours % 12;
    hours = hours ? hours : 12;
    
    return `${hours}:${minutes.toString().padStart(2, '0')} ${ampm}`;
}

// Add event listeners
function addEventListeners() {
    // Send message on button click
    sendMessageButton.addEventListener('click', sendMessage);
    
    // Send message on Enter key
    messageInputElement.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Tab switching in info sidebar
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', function() {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // Section toggle in info sidebar
    document.querySelectorAll('.section-toggle').forEach(toggle => {
        toggle.addEventListener('click', function() {
            const section = this.closest('.user-info-section');
            const content = section.querySelector('.section-content');
            content.style.display = content.style.display === 'none' ? 'block' : 'none';
            this.innerHTML = content.style.display === 'none' ? '<i class="fas fa-plus"></i>' : '<i class="fas fa-minus"></i>';
        });
    });
}

// Initialize the app when the DOM is loaded
document.addEventListener('DOMContentLoaded', init); 