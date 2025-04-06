# Stealth Browser API

A FastAPI-based controller API for undetected-chromedriver that allows developers to control a stealth Chrome browser via HTTP requests.

## Features

- Launch or reuse a headless Chrome browser with stealth capabilities
- Navigate to URLs
- Execute JavaScript code on the current page
- Extract HTML content
- Take screenshots
- Configure proxy settings
- Consistent JSON response structure

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python app.py
```

Or with uvicorn directly:
```bash
uvicorn app:app --reload
```

## API Endpoints

### Start Browser and Navigate
```
POST /browser/start
```
Body:
```json
{
  "url": "https://example.com",
  "proxy": "http://user:pass@proxy.example:8080",  // optional
  "headless": true,  // optional, default true
  "timeout": 30  // optional, default 30 seconds
}
```

### Navigate to URL
```
POST /browser/navigate
```
Body:
```json
{
  "url": "https://example.com",
  "timeout": 30  // optional, default 30 seconds
}
```

### Execute JavaScript
```
POST /browser/javascript
```
Body:
```json
{
  "script": "document.title",
  "timeout": 30  // optional, default 30 seconds
}
```

### Get Page HTML
```
GET /browser/html
```

### Take Screenshot
```
GET /browser/screenshot
```

### Close Browser
```
POST /browser/close
```

All responses follow this structure:
```json
{
  "success": true,
  "data": { ... },  // response data if successful
  "error": "Error message if any"  // only present on error
}
```

## Swagger Documentation
When the API is running, visit `http://localhost:8000/docs` for interactive API documentation.
