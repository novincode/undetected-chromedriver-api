import base64
import io
import os
from typing import Dict, Optional, Any, List, Union
from pathlib import Path

import undetected_chromedriver as uc
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver

# Create profiles directory if it doesn't exist
PROFILES_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / "profiles"
PROFILES_DIR.mkdir(exist_ok=True)

# Models for request and response
class NavigateRequest(BaseModel):
    url: HttpUrl
    proxy: Optional[str] = None
    headless: bool = False  # Changed default to False - browser will be visible
    timeout: int = 30
    profile_name: Optional[str] = "default"

class JavascriptRequest(BaseModel):
    script: str
    timeout: int = 30

class ProfileRequest(BaseModel):
    profile_name: str = "default"

class ProfileListResponse(BaseModel):
    profiles: List[str]

class ProxyConfig(BaseModel):
    server: str
    username: Optional[str] = None
    password: Optional[str] = None

class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

# Browser controller class
class BrowserController:
    def __init__(self):
        self.driver: Optional[WebDriver] = None
        self.current_profile: Optional[str] = None
        
    async def start_browser(self, headless: bool = True, proxy: Optional[str] = None, profile_name: str = "default") -> None:
        """Start a new browser instance with the given options and profile"""
        # Close any existing session
        if self.driver:
            await self.close_browser()
            
        options = uc.ChromeOptions()
        
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')
        
        # Set up user data directory for the profile
        profile_path = PROFILES_DIR / profile_name
        profile_path.mkdir(exist_ok=True)
        
        try:
            self.driver = uc.Chrome(
                headless=headless,
                options=options,
                user_data_dir=str(profile_path),
                use_subprocess=True
            )
            self.current_profile = profile_name
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to start browser: {str(e)}")
    
    async def navigate_to(self, url: str, timeout: int = 30) -> str:
        """Navigate to a URL and return the page title"""
        if not self.driver:
            raise HTTPException(status_code=400, detail="Browser not started")
        
        try:
            self.driver.set_page_load_timeout(timeout)
            self.driver.get(url)
            return self.driver.title
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Navigation failed: {str(e)}")
    
    async def execute_js(self, script: str, timeout: int = 30) -> Any:
        """Execute JavaScript in the browser and return the result"""
        if not self.driver:
            raise HTTPException(status_code=400, detail="Browser not started")
        
        try:
            self.driver.set_script_timeout(timeout)
            result = self.driver.execute_script(f"return {script}")
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"JavaScript execution failed: {str(e)}")
    
    async def get_html(self) -> str:
        """Get the current page HTML"""
        if not self.driver:
            raise HTTPException(status_code=400, detail="Browser not started")
        
        try:
            return self.driver.page_source
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get HTML: {str(e)}")
    
    async def get_screenshot(self) -> str:
        """Take a screenshot and return as base64 string"""
        if not self.driver:
            raise HTTPException(status_code=400, detail="Browser not started")
        
        try:
            screenshot = self.driver.get_screenshot_as_base64()
            return screenshot
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to take screenshot: {str(e)}")
    
    async def close_browser(self) -> None:
        """Close the browser"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            finally:
                self.driver = None
    
    async def get_current_profile(self) -> Optional[str]:
        """Get the name of the current profile"""
        return self.current_profile

# FastAPI app
app = FastAPI(
    title="Stealth Browser API",
    description="API for controlling an undetected Chrome browser instance",
    version="1.0.0"
)

# Global browser controller
browser = BrowserController()

@app.post("/browser/start", response_model=ApiResponse)
async def start_browser(request: NavigateRequest):
    """Start a browser with the specified profile and navigate to the URL"""
    try:
        await browser.start_browser(
            headless=request.headless, 
            proxy=request.proxy,
            profile_name=request.profile_name
        )
        title = await browser.navigate_to(str(request.url), request.timeout)
        return {"success": True, "data": {"title": title, "profile": request.profile_name}}
    except HTTPException as e:
        return {"success": False, "error": e.detail}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/browser/navigate", response_model=ApiResponse)
async def navigate(request: NavigateRequest):
    """Navigate to a URL"""
    try:
        title = await browser.navigate_to(str(request.url), request.timeout)
        return {"success": True, "data": {"title": title}}
    except HTTPException as e:
        return {"success": False, "error": e.detail}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/browser/javascript", response_model=ApiResponse)
async def execute_javascript(request: JavascriptRequest):
    """Execute JavaScript on the current page"""
    try:
        result = await browser.execute_js(request.script, request.timeout)
        return {"success": True, "data": result}
    except HTTPException as e:
        return {"success": False, "error": e.detail}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/browser/html", response_model=ApiResponse)
async def get_html():
    """Get the HTML of the current page"""
    try:
        html = await browser.get_html()
        return {"success": True, "data": {"html": html}}
    except HTTPException as e:
        return {"success": False, "error": e.detail}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/browser/screenshot", response_model=ApiResponse)
async def get_screenshot():
    """Take a screenshot of the current page"""
    try:
        screenshot = await browser.get_screenshot()
        return {"success": True, "data": {"screenshot": screenshot}}
    except HTTPException as e:
        return {"success": False, "error": e.detail}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/browser/close", response_model=ApiResponse)
async def close_browser(background_tasks: BackgroundTasks):
    """Close the browser"""
    try:
        background_tasks.add_task(browser.close_browser)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/browser/profile", response_model=ApiResponse)
async def get_current_profile():
    """Get the current browser profile name"""
    try:
        profile = await browser.get_current_profile()
        return {"success": True, "data": {"profile": profile}}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/browser/profiles", response_model=ApiResponse)
async def list_profiles():
    """List all available browser profiles"""
    try:
        profiles = [d.name for d in PROFILES_DIR.iterdir() if d.is_dir()]
        return {"success": True, "data": {"profiles": profiles}}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
