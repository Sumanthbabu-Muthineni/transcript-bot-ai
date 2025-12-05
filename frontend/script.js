
// Use local backend for processing (YouTube works from local IP)
// For chat, it will use Lambda after video is processed
const LOCAL_BACKEND_URL = 'http://localhost:5000';
const LAMBDA_BACKEND_URL = 'https://fx2g6wc3f4.execute-api.us-east-1.amazonaws.com/prod';

// Use local backend for /ingest (to bypass YouTube IP blocking)
// Use Lambda for /chat (serverless, scalable)
const API_BASE_URL = LOCAL_BACKEND_URL;

// State
let currentVideoId = null;

// Ingest video
async function ingestVideo() {
    const urlInput = document.getElementById('video-url');
    const url = urlInput.value.trim();
    const statusDiv = document.getElementById('ingest-status');
    const ingestBtn = document.getElementById('ingest-btn');

    if (!url) {
        showStatus('Please enter a YouTube URL', 'error');
        return;
    }

    // Validate URL format
    if (!url.includes('youtube.com') && !url.includes('youtu.be')) {
        showStatus('Please enter a valid YouTube URL', 'error');
        return;
    }

    // Show loading state with progress
    ingestBtn.disabled = true;

    // Show progress steps
    showStatus('📥 Step 1/4: Extracting transcript from YouTube...', 'loading');

    setTimeout(() => showStatus('📝 Step 2/4: Chunking transcript text...', 'loading'), 3000);
    setTimeout(() => showStatus('🧠 Step 3/4: Generating embeddings with OpenAI...', 'loading'), 6000);
    setTimeout(() => showStatus('☁️ Step 4/4: Uploading vector store to S3...', 'loading'), 15000);

    try {
        const response = await fetch(`${API_BASE_URL}/ingest`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            currentVideoId = data.video_id;
            showStatus(
                `✅ Video processed successfully! Created ${data.chunks_count} chunks from ${data.transcript_length} characters. Ready to chat!`,
                'success'
            );

            // Show chat section without default message
            setTimeout(() => {
                document.getElementById('ingest-section').style.display = 'none';
                document.getElementById('chat-section').style.display = 'block';
            }, 2000);
        } else {
            showStatus(`❌ Error: ${data.error || 'Failed to process video'}`, 'error');
            ingestBtn.disabled = false;
        }
    } catch (error) {
        showStatus(`❌ Error: ${error.message}`, 'error');
        ingestBtn.disabled = false;
    }
}

// Ask question
async function askQuestion() {
    const questionInput = document.getElementById('question-input');
    const question = questionInput.value.trim();
    const askBtn = document.getElementById('ask-btn');

    if (!question) {
        return;
    }

    // Disable input while processing
    questionInput.disabled = true;
    askBtn.disabled = true;

    // Add user message to chat
    addMessage(question, 'user');
    questionInput.value = '';

    // Show loading indicator
    const loadingId = addMessage('Thinking<span class="loading-dots"></span>', 'bot', true);

    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                video_id: currentVideoId,
                question: question
            })
        });

        const data = await response.json();

        // Remove loading message
        removeMessage(loadingId);

        if (response.ok && data.success) {
            addMessage(data.answer, 'bot');
        } else {
            addMessage(`Error: ${data.error || 'Failed to get answer'}`, 'bot');
        }
    } catch (error) {
        removeMessage(loadingId);
        addMessage(`Error: ${error.message}`, 'bot');
    } finally {
        questionInput.disabled = false;
        askBtn.disabled = false;
        questionInput.focus();
    }
}

// Handle Enter key in question input
function handleEnter(event) {
    if (event.key === 'Enter') {
        askQuestion();
    }
}

// Reset app to load new video
function resetApp() {
    currentVideoId = null;
    document.getElementById('video-url').value = '';
    document.getElementById('question-input').value = '';
    document.getElementById('ingest-status').innerHTML = '';
    document.getElementById('chat-box').innerHTML = '';
    document.getElementById('ingest-section').style.display = 'block';
    document.getElementById('chat-section').style.display = 'none';
    document.getElementById('ingest-btn').disabled = false;
}

// UI helper functions
function showStatus(message, type) {
    const statusDiv = document.getElementById('ingest-status');
    statusDiv.innerHTML = message;
    statusDiv.className = `status ${type}`;
}

function addMessage(text, type, isLoading = false) {
    const chatBox = document.getElementById('chat-box');
    const messageDiv = document.createElement('div');
    const messageId = `msg-${Date.now()}`;

    messageDiv.id = messageId;
    messageDiv.className = `message ${type}-message`;
    messageDiv.innerHTML = text;

    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    return messageId;
}

function removeMessage(messageId) {
    const message = document.getElementById(messageId);
    if (message) {
        message.remove();
    }
}
