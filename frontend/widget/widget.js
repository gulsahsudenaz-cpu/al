const config = window.ChatbotConfig || {
    apiUrl: "ws://localhost:8000/v1/ws/chat",
    roomKey: "tenant_123",
    theme: "auto",
    heartbeat: 30000,
    enableFeedback: true
};

let ws = null;
let heartbeatTimer = null;
let lastMessageHash = '';
let isTyping = false;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;
const reconnectDelay = 3000;

// DOM Elements
const toggle = document.getElementById('widgetToggle');
const widget = document.getElementById('chatbotWidget');
const closeBtn = document.getElementById('widgetClose');
const messages = document.getElementById('widgetMessages');
const input = document.getElementById('widgetMessageInput');
const sendButton = document.getElementById('widgetSendButton');
const attachFileBtn = document.getElementById('attachFileBtn');
const voiceBtn = document.getElementById('voiceBtn');
const cameraBtn = document.getElementById('cameraBtn');

// Widget Toggle
if (toggle) {
    toggle.addEventListener('click', () => {
        widget.classList.toggle('active');
        toggle.classList.toggle('active');
        if (widget.classList.contains('active')) {
            const theme = config.theme === 'auto' 
                ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
                : config.theme;
            document.body.setAttribute('data-theme', theme);
            input?.focus();
            connectWebSocket();
        } else {
            disconnectWebSocket();
        }
    });
}

// Close Button
if (closeBtn) {
    closeBtn.addEventListener('click', () => {
        widget.classList.remove('active');
        toggle.classList.remove('active');
        disconnectWebSocket();
    });
}

// Click outside to close
document.addEventListener('click', (e) => {
    if (widget && toggle && 
        !widget.contains(e.target) && 
        !toggle.contains(e.target) && 
        widget.classList.contains('active')) {
        // Don't close on mobile, only on desktop
        if (window.innerWidth > 768) {
            widget.classList.remove('active');
            toggle.classList.remove('active');
        }
    }
});

// WebSocket Connection
function connectWebSocket() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        return;
    }

    const wsUrl = config.apiUrl.replace('http://', 'ws://').replace('https://', 'wss://');
    const url = `${wsUrl}?room_key=${config.roomKey || 'default'}`;
    
    try {
        ws = new WebSocket(url);

        ws.onopen = () => {
            console.log('WebSocket connected');
            reconnectAttempts = 0;
            if (config.welcomeMessage) {
                addMessage(config.welcomeMessage, 'bot');
            }
            startHeartbeat();
        };

        ws.onmessage = async (e) => {
            try {
                const data = JSON.parse(e.data);
                
                if (data.type === 'server.message') {
                    const hash = btoa(data.message + (data.timestamp || ''));
                    if (hash === lastMessageHash) return;
                    lastMessageHash = hash;
                    
                    showTyping(false);
                    await streamMessage(data.message || data.text || '', 'bot', data.sources);
                } else if (data.type === 'server.typing') {
                    showTyping(data.is_typing);
                } else if (data.type === 'server.error') {
                    showTyping(false);
                    addMessage('Üzgünüm, bir hata oluştu. Tekrar deneyin.', 'bot');
                } else if (data.type === 'pong') {
                    // Heartbeat response
                }
            } catch (err) {
                console.error('Error parsing message:', err);
            }
        };

        ws.onclose = () => {
            clearInterval(heartbeatTimer);
            if (reconnectAttempts < maxReconnectAttempts && widget.classList.contains('active')) {
                reconnectAttempts++;
                setTimeout(connectWebSocket, reconnectDelay * reconnectAttempts);
            }
        };

        ws.onerror = (err) => {
            console.error('WebSocket error:', err);
            showTyping(false);
        };
    } catch (err) {
        console.error('WebSocket connection error:', err);
    }
}

function disconnectWebSocket() {
    if (ws) {
        ws.close();
        ws = null;
    }
    clearInterval(heartbeatTimer);
}

// Send Message
function sendWidgetMessage() {
    const text = input?.value.trim();
    if (!text || !ws || ws.readyState !== WebSocket.OPEN) {
        return;
    }

    // Rate limiting
    if (Date.now() - (window.lastSend || 0) < 1000) {
        return;
    }
    window.lastSend = Date.now();

    try {
        ws.send(JSON.stringify({ type: 'client.message', text }));
        addMessage(text, 'user');
        if (input) input.value = '';
        showTyping(true);
    } catch (err) {
        console.error('Error sending message:', err);
    }
}

// Add Message
function addMessage(text, sender, sources = null) {
    if (!messages) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = `widget-message ${sender}`;
    const timeString = new Date().toLocaleTimeString('tr-TR', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    let content = text;
    
    // Add sources if available
    if (sources && Array.isArray(sources) && sources.length > 0) {
        sources.forEach((source, idx) => {
            const sourceUrl = source.url || source.source;
            const sourceTitle = source.title || source.name || `Kaynak ${idx + 1}`;
            content += `<br><small style="opacity:0.7; font-size:10px; color:#667eea; cursor:pointer; margin-top:4px; display:block;" onclick="openSource('${sourceUrl}')">📄 ${sourceTitle}</small>`;
        });
    }
    
    content += `<div class="widget-message-time">${timeString}</div>`;
    
    // Add feedback buttons for bot messages
    if (sender === 'bot' && config.enableFeedback) {
        content += `
            <div class="feedback-container">
                <button class="feedback-btn" onclick="giveFeedback(this, true, '${text.substring(0, 50)}')">👍</button>
                <button class="feedback-btn" onclick="giveFeedback(this, false, '${text.substring(0, 50)}')">👎</button>
            </div>
        `;
    }
    
    messageDiv.innerHTML = `<div class="widget-message-content">${content}</div>`;
    messages.appendChild(messageDiv);
    scrollToBottom();
}

// Stream Message
async function streamMessage(fullText, sender, sources = null) {
    if (!messages) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = `widget-message ${sender}`;
    const messageId = `stream-msg-${Date.now()}`;
    messageDiv.innerHTML = `<div class="widget-message-content" id="${messageId}"><span id="stream-text-${messageId}"></span></div>`;
    messages.appendChild(messageDiv);
    scrollToBottom();

    const streamTextEl = document.getElementById(`stream-text-${messageId}`);
    if (!streamTextEl) return;

    let text = '';
    for (let char of fullText) {
        text += char;
        streamTextEl.textContent = text;
        scrollToBottom();
        await new Promise(resolve => setTimeout(resolve, 20));
    }

    // Replace with final message including sources
    messageDiv.remove();
    addMessage(fullText, sender, sources);
}

// Show Typing Indicator
function showTyping(show) {
    if (!messages) return;
    if (isTyping === show) return;
    isTyping = show;

    const typingEl = document.getElementById('typing-indicator');
    
    if (show && !typingEl) {
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.className = 'widget-message bot';
        typingDiv.innerHTML = `
            <div class="widget-typing-indicator">
                <div class="widget-typing-dot"></div>
                <div class="widget-typing-dot"></div>
                <div class="widget-typing-dot"></div>
            </div>
        `;
        messages.appendChild(typingDiv);
        scrollToBottom();
    } else if (!show && typingEl) {
        typingEl.remove();
    }
}

// Heartbeat
function startHeartbeat() {
    clearInterval(heartbeatTimer);
    heartbeatTimer = setInterval(() => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }));
        }
    }, config.heartbeat || 30000);
}

// Scroll to Bottom
function scrollToBottom() {
    if (messages) {
        messages.scrollTop = messages.scrollHeight;
    }
}

// Open Source
function openSource(url) {
    if (url) {
        window.open(url, '_blank');
    }
}

// Give Feedback
function giveFeedback(el, helpful, messageText) {
    if (el) {
        el.style.transform = 'scale(1.5)';
    }
    
    if (helpful) {
        // Confetti effect
        for (let i = 0; i < 20; i++) {
            const confetti = document.createElement('div');
            const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57'];
            confetti.style.cssText = `
                position: fixed;
                left: ${Math.random() * 100}vw;
                top: 50vh;
                width: 10px;
                height: 10px;
                background: ${colors[Math.floor(Math.random() * colors.length)]};
                border-radius: 50%;
                pointer-events: none;
                z-index: 1001;
                animation: confetti ${Math.random() * 3 + 1}s linear forwards;
            `;
            document.body.appendChild(confetti);
            setTimeout(() => confetti.remove(), 3000);
        }
        addMessage('Teşekkürler! Bu yardımcı oldu. 🎉', 'bot');
    } else {
        addMessage('Üzgünüm, daha iyi yapacağım. Detay verebilir misin?', 'bot');
    }
    
    // TODO: Send feedback to backend
}

// Event Listeners
if (sendButton) {
    sendButton.addEventListener('click', sendWidgetMessage);
}

if (input) {
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendWidgetMessage();
        }
    });
    
    input.addEventListener('input', () => {
        if (input) {
            input.style.height = 'auto';
            input.style.height = input.scrollHeight + 'px';
        }
    });
}

// Media Buttons
if (attachFileBtn) {
    attachFileBtn.addEventListener('click', () => {
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = '*/*';
        fileInput.onchange = (e) => {
            const file = e.target.files[0];
            if (file) {
                addMessage(`📎 Dosya: ${file.name}`, 'user');
                // TODO: Upload file and send via WebSocket
            }
        };
        fileInput.click();
    });
}

if (voiceBtn) {
    voiceBtn.addEventListener('click', async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream);
            const audioChunks = [];
            
            mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);
            mediaRecorder.onstop = () => {
                addMessage('🎤 Ses kaydı gönderildi', 'user');
                // TODO: Send audio via WebSocket
                stream.getTracks().forEach(track => track.stop());
            };
            
            mediaRecorder.start();
            voiceBtn.textContent = '⏹️';
            
            setTimeout(() => {
                mediaRecorder.stop();
                voiceBtn.textContent = '🎤';
            }, 5000);
        } catch (err) {
            console.error('Microphone access error:', err);
            addMessage('Mikrofon erişimi reddedildi', 'system');
        }
    });
}

if (cameraBtn) {
    cameraBtn.addEventListener('click', () => {
        const cameraInput = document.createElement('input');
        cameraInput.type = 'file';
        cameraInput.accept = 'image/*';
        cameraInput.capture = 'environment';
        cameraInput.onchange = (e) => {
            const file = e.target.files[0];
            if (file) {
                addMessage(`📷 Fotoğraf: ${file.name}`, 'user');
                // TODO: Upload image and send via WebSocket
            }
        };
        cameraInput.click();
    });
}

// Initialize
window.addEventListener('load', () => {
    scrollToBottom();
});

// Export functions for global access
window.sendWidgetMessage = sendWidgetMessage;
window.openSource = openSource;
window.giveFeedback = giveFeedback;

