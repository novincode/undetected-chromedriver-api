# Undetected-Chromedriver-API

![Undetected-Chromedriver-API](https://github.com/user-attachments/assets/56ff9a7f-a464-42a7-b974-332414047f23)

A simple and powerful API layer built on top of `undetected-chromedriver` to control Chrome browsers programmatically. This project is perfect for developers who need to automate web interactions while bypassing anti-bot measures.

## 🌟 Features

- **Undetectable Browsing**: Uses `undetected-chromedriver` to bypass bot detection.
- **RESTful API**: Control the browser using simple HTTP requests.
- **Profile Management**: Save and reuse browser sessions with ease.
- **JavaScript Execution**: Run custom JavaScript on any webpage.
- **HTML Retrieval**: Fetch the source code of any webpage.
- **Screenshot Capture**: Take screenshots of web pages as images.
- **Proxy Support**: Browse anonymously using proxy servers.
- **Headless Mode**: Run the browser in the background without a visible window.

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher
- Chrome browser installed

### Installation

1. Clone this repository or download the files:
   ```bash
   git clone https://github.com/your-username/undetected-chromedriver-api.git
   cd undetected-chromedriver-api
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the API server:
   ```bash
   python app.py
   ```

   The server will start on `http://localhost:8000`.

4. Open the API documentation in your browser:
   - Navigate to `http://localhost:8000/docs` for an interactive Swagger UI.

## 🎮 How to Use

### API Endpoints

Here are the main endpoints you can use to control the browser:

#### 1. **Start Browser**
   - **Endpoint**: `POST /browser/start`
   - **Description**: Starts a new browser session with optional settings.
   - **Request Body**:
     ```json
     {
       "url": "https://www.example.com",
       "proxy": "http://username:password@proxyserver:port",
       "headless": true,
       "profile_name": "my-profile"
     }
     ```
   - **Response**:
     ```json
     {
       "success": true,
       "data": {
         "title": "Example Domain",
         "profile": "my-profile"
       }
     }
     ```

#### 2. **Navigate to URL**
   - **Endpoint**: `POST /browser/navigate`
   - **Description**: Navigate to a specific URL in the browser.
   - **Request Body**:
     ```json
     {
       "url": "https://www.example.com",
       "timeout": 30
     }
     ```
   - **Response**:
     ```json
     {
       "success": true,
       "data": {
         "title": "Example Domain"
       }
     }
     ```

#### 3. **Execute JavaScript**
   - **Endpoint**: `POST /browser/javascript`
   - **Description**: Run custom JavaScript on the current page.
   - **Request Body**:
     ```json
     {
       "script": "document.title",
       "timeout": 30
     }
     ```
   - **Response**:
     ```json
     {
       "success": true,
       "data": "Example Domain"
     }
     ```

#### 4. **Get Page HTML**
   - **Endpoint**: `GET /browser/html`
   - **Description**: Retrieve the HTML source of the current page.
   - **Response**:
     ```json
     {
       "success": true,
       "data": {
         "html": "<!DOCTYPE html>..."
       }
     }
     ```

#### 5. **Take Screenshot**
   - **Endpoint**: `GET /browser/screenshot`
   - **Description**: Capture a screenshot of the current page.
   - **Response**:
     ```json
     {
       "success": true,
       "data": {
         "screenshot": "base64-encoded-image-data"
       }
     }
     ```

#### 6. **Close Browser**
   - **Endpoint**: `POST /browser/close`
   - **Description**: Close the current browser session.
   - **Response**:
     ```json
     {
       "success": true
     }
     ```

#### 7. **List Profiles**
   - **Endpoint**: `GET /browser/profiles`
   - **Description**: List all available browser profiles.
   - **Response**:
     ```json
     {
       "success": true,
       "data": {
         "profiles": ["default", "my-profile"]
       }
     }
     ```

### Example Workflow

1. Start the browser with a specific profile:
   ```bash
   curl -X POST http://localhost:8000/browser/start -H "Content-Type: application/json" -d '{
     "url": "https://www.example.com",
     "profile_name": "my-profile"
   }'
   ```

2. Navigate to another URL:
   ```bash
   curl -X POST http://localhost:8000/browser/navigate -H "Content-Type: application/json" -d '{
     "url": "https://www.google.com"
   }'
   ```

3. Execute JavaScript:
   ```bash
   curl -X POST http://localhost:8000/browser/javascript -H "Content-Type: application/json" -d '{
     "script": "document.title"
   }'
   ```

4. Take a screenshot:
   ```bash
   curl -X GET http://localhost:8000/browser/screenshot
   ```

5. Close the browser:
   ```bash
   curl -X POST http://localhost:8000/browser/close
   ```

## 🔍 Troubleshooting

- **Port Already in Use**: Ensure port `8000` is free or change the port in `app.py`.
- **Browser Not Starting**: Verify that Chrome is installed and accessible.
- **Connection Issues**: Ensure the API server is running before making requests.

## ⚠️ Important Notes

- This tool is for educational and legitimate research purposes only.
- Always respect websites' terms of service.
- Using proxies may violate some websites' terms.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to open an issue or submit a pull request.

## 📝 License

This project is [MIT](https://choosealicense.com/licenses/mit/) licensed.
