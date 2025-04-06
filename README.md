# 🔐 Undetected-Chromedriver-API

> **Automate with invisibility. Browse like a human, not a bot.**

![Undetected-Chromedriver-API](https://github.com/user-attachments/assets/56ff9a7f-a464-42a7-b974-332414047f23)

[![Python 3.7+](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

A powerful REST API layer that wraps `undetected-chromedriver` to provide stealth browser automation. Perfect for developers building web scrapers, test automation tools, or any application that needs to bypass sophisticated bot detection systems.

## 🌟 Features

- 🛡️ **Undetectable Browsing** - Bypass Cloudflare, reCAPTCHA, and other bot detection systems
- 🔌 **RESTful API** - Control browsers programmatically with simple HTTP requests
- 🧩 **Profile Management** - Create, save and reuse browser sessions with different identities
- 📝 **JavaScript Execution** - Run custom JavaScript remotely on any webpage
- 🔍 **HTML Retrieval** - Fetch and analyze the source code of any webpage
- 📸 **Screenshot Capture** - Take high-quality screenshots remotely
- 🔒 **Proxy Support** - Route traffic through proxies for enhanced privacy
- 👻 **Headless Mode** - Run browsers invisibly in the background

## 🚀 Getting Started

### Prerequisites

- 🐍 Python 3.7 or higher
- 🌐 Chrome browser installed on your system

### 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/undetected-chromedriver-api.git
   cd undetected-chromedriver-api
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Choose your method**

   **Option A: GUI Interface (Recommended for beginners)**
   ```bash
   python gui.py
   ```
   
   **Option B: API Server Only**
   ```bash
   python app.py
   ```
   The server will start on `http://localhost:8000`.

4. **Explore the API**
   - Interactive API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## 📖 How to Use

### 🖥️ GUI Method

Our user-friendly GUI provides easy access to all API functions:

1. Click "Start Server" to launch the API
2. Configure your browser settings (profile, proxy, headless mode)
3. Click "Start Browser" to launch a Chrome instance
4. Use the tabs to:
   - Navigate to websites
   - Execute JavaScript
   - View page HTML
   - Take screenshots

### ⚡ API Method

#### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/browser/start` | POST | Start a new browser with custom settings |
| `/browser/navigate` | POST | Navigate to a specified URL |
| `/browser/javascript` | POST | Execute JavaScript code |
| `/browser/html` | GET | Retrieve page HTML |
| `/browser/screenshot` | GET | Take a screenshot |
| `/browser/close` | POST | Close the browser |
| `/browser/profiles` | GET | List available profiles |

#### Example: Start a Browser Session

```bash
curl -X POST http://localhost:8000/browser/start \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.example.com",
    "headless": false,
    "profile_name": "my-profile"
  }'
```

#### Example: Execute JavaScript

```bash
curl -X POST http://localhost:8000/browser/javascript \
  -H "Content-Type: application/json" \
  -d '{
    "script": "document.title",
    "timeout": 30
  }'
```

## 🛠️ Advanced Usage

### 🔑 Profile Management

Create different browser profiles to maintain separate cookies, cache, and session data:

```bash
# Start with a specific profile
curl -X POST http://localhost:8000/browser/start \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.example.com",
    "profile_name": "shopping-account"
  }'
```

### 🕵️ Proxy Configuration

```bash
# Use with a proxy
curl -X POST http://localhost:8000/browser/start \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.example.com",
    "proxy": "http://username:password@proxyserver:port"
  }'
```

## 🔍 Troubleshooting

- **Port Conflict**: If port 8000 is already in use, modify the port in `app.py`
- **Chrome Not Found**: Ensure Chrome is installed in the default location
- **Connection Issues**: Verify the server is running before making API calls

## 🔜 Future Plans

- ✨ TypeScript client library for easier integration
- 📱 Support for mobile emulation
- 🌐 Enhanced proxy rotation capabilities
- 🧪 Additional browser fingerprinting protections

## ⚠️ Important Notes

- This tool is intended for legitimate research, testing, and automation purposes
- Always respect websites' terms of service and robots.txt
- Using proxies may violate some websites' terms of service

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## 📞 Support

Need help? Have questions?
- Telegram: [@codeideal_support](https://t.me/codeideal_support)
- Email: codeideal.com@gmail.com

## 📝 License

This project is [MIT](https://choosealicense.com/licenses/mit/) licensed.
