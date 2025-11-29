/**
 * Healthcare Assistant Frontend
 * Handles user input and communicates with the orchestrator API.
 */

// Load configuration (config.js should be loaded before this file)
// Configuration is set in config.js or via window.CONFIG
const CONFIG = window.CONFIG || {
    ORCHESTRATOR_URL: 'http://localhost:7071/api/orchestrate',
    FUNCTION_KEY: '',
    TIMEOUT: 30000
};

// State
let conversationHistory = [];

// DOM Elements
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const statusBar = document.getElementById('status');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    updateStatus('Ready');
});

/**
 * Sets up event listeners for user interactions.
 */
function setupEventListeners() {
    sendButton.addEventListener('click', handleSendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });
}

/**
 * Handles sending a message to the orchestrator.
 */
async function handleSendMessage() {
    const message = userInput.value.trim();
    
    if (!message) {
        return;
    }
    
    // Disable input while processing
    setInputEnabled(false);
    
    // Add user message to chat
    addMessage(message, 'user');
    
    // Clear input
    userInput.value = '';
    
    // Show typing indicator
    const typingIndicator = showTypingIndicator();
    
    try {
        updateStatus('Processing...');
        
        // Call orchestrator API
        const response = await callOrchestrator(message);
        
        // Remove typing indicator
        removeTypingIndicator(typingIndicator);
        
        // Add bot response
        addMessage(response.response || 'I apologize, but I encountered an error processing your request.', 'bot');
        
        // Update conversation history
        conversationHistory.push(
            { role: 'user', content: message },
            { role: 'assistant', content: response.response }
        );
        
        updateStatus('Ready');
        
    } catch (error) {
        console.error('Error:', error);
        removeTypingIndicator(typingIndicator);
        addMessage('Sorry, I encountered an error. Please try again.', 'bot');
        updateStatus('Error occurred');
    } finally {
        setInputEnabled(true);
        userInput.focus();
    }
}

/**
 * Calls the orchestrator API.
 */
async function callOrchestrator(query) {
    const url = new URL(CONFIG.ORCHESTRATOR_URL);
    
    // Add function key if provided
    if (CONFIG.FUNCTION_KEY) {
        url.searchParams.append('code', CONFIG.FUNCTION_KEY);
    }
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), CONFIG.TIMEOUT || 30000);
    
    try {
        const response = await fetch(url.toString(), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                history: conversationHistory
            }),
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
    
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`API error: ${response.status} - ${errorText}`);
        }
        
        return await response.json();
    } catch (error) {
        clearTimeout(timeoutId);
        if (error.name === 'AbortError') {
            throw new Error('Request timeout - the server took too long to respond');
        }
        throw error;
    }
}

/**
 * Adds a message to the chat interface.
 */
function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const textParagraph = document.createElement('p');
    textParagraph.textContent = text;
    
    contentDiv.appendChild(textParagraph);
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Shows a typing indicator.
 */
function showTypingIndicator() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message typing-indicator-message';
    messageDiv.id = 'typing-indicator';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content typing-indicator';
    
    for (let i = 0; i < 3; i++) {
        const span = document.createElement('span');
        contentDiv.appendChild(span);
    }
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return messageDiv;
}

/**
 * Removes the typing indicator.
 */
function removeTypingIndicator(indicator) {
    if (indicator && indicator.parentNode) {
        indicator.parentNode.removeChild(indicator);
    }
}

/**
 * Enables or disables the input field and send button.
 */
function setInputEnabled(enabled) {
    userInput.disabled = !enabled;
    sendButton.disabled = !enabled;
}

/**
 * Updates the status bar.
 */
function updateStatus(status) {
    statusBar.textContent = status;
}

