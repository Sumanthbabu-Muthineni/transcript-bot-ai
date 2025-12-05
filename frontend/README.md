# Single-Video Twin - Frontend

Simple, clean HTML/CSS/JavaScript interface for the Video Twin chatbot.

## Features

- Minimalistic design with clean aesthetics
- Two-step flow: Ingest video → Chat
- Real-time chat interface
- Loading states and error handling
- Responsive design for mobile and desktop

## Setup

1. Update API endpoint in `script.js`:
```javascript
const API_BASE_URL = 'https://YOUR_API_GATEWAY_URL/prod';
```

Replace with your actual API Gateway URL from the backend deployment.

## Local Development

Simply open `index.html` in a browser. No build process needed.

For better CORS handling during development, you can use a local server:

```bash
# Python
python -m http.server 8000

# Node.js
npx http-server

# VS Code
# Install "Live Server" extension and click "Go Live"
```

Then visit: `http://localhost:8000`

## Deployment Options

### Option 1: S3 Static Website (Recommended)

1. Create S3 bucket in AWS Console
2. Enable static website hosting
3. Upload files:
```bash
aws s3 sync . s3://your-bucket-name --exclude "README.md"
```
4. Make bucket public (or use CloudFront)

### Option 2: Netlify/Vercel

1. Create account on Netlify or Vercel
2. Drag and drop the `frontend` folder
3. Done!

### Option 3: GitHub Pages

1. Push to GitHub repository
2. Enable GitHub Pages in repository settings
3. Select branch and `/frontend` folder

## Usage

1. **Load Video**: Paste any YouTube URL with captions enabled
2. **Wait**: Processing takes 30-60 seconds depending on video length
3. **Chat**: Ask questions about the video content
4. **Reset**: Click "Load New Video" to start over

## File Structure

```
frontend/
├── index.html      # Main page structure
├── styles.css      # Minimalistic styling
├── script.js       # API interactions and UI logic
└── README.md       # This file
```

## Browser Compatibility

Works on all modern browsers:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Customization

### Colors

Edit `styles.css` to change the color scheme:
- Primary: `#3498db` (blue buttons)
- Background: `#f5f5f5` (light gray)
- Text: `#333` (dark gray)

### Layout

All styling is in `styles.css` with clear section comments. No CSS framework dependencies.
