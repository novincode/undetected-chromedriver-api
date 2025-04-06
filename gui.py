import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import requests
import json
import base64
from PIL import Image, ImageTk
import io
import threading
import subprocess
import time
import sys
import os

class BrowserControllerGUI:
    """
    Main GUI class for the Stealth Browser Controller application.
    Provides a user interface to control the undetected-chromedriver API.
    """
    def __init__(self, root):
        # Initialize main window
        self.root = root
        self.root.title("Stealth Browser Controller")
        self.root.geometry("1200x800")
        self.root.minsize(900, 700)
        
        # API base URL
        self.api_url = "http://localhost:8000"
        self.server_process = None
        
        # Create main frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.browser_tab = ttk.Frame(self.notebook)
        self.js_tab = ttk.Frame(self.notebook)
        self.html_tab = ttk.Frame(self.notebook)
        self.screenshot_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.browser_tab, text="Browser Control")
        self.notebook.add(self.js_tab, text="JavaScript")
        self.notebook.add(self.html_tab, text="HTML")
        self.notebook.add(self.screenshot_tab, text="Screenshot")
        
        # Setup each tab
        self._setup_browser_tab()
        self._setup_js_tab()
        self._setup_html_tab()
        self._setup_screenshot_tab()
        self._setup_profile_management()
        
        # Status bar
        status_frame = ttk.Frame(root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Server controls
        self.server_frame = ttk.Frame(root)
        self.server_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        
        self.server_status_var = tk.StringVar()
        self.server_status_var.set("Server: Stopped")
        self.server_status = ttk.Label(self.server_frame, textvariable=self.server_status_var)
        self.server_status.pack(side=tk.LEFT, padx=5)
        
        self.server_button = ttk.Button(self.server_frame, text="Start Server", command=self.toggle_server)
        self.server_button.pack(side=tk.RIGHT, padx=5)
        
    def _setup_browser_tab(self):
        """Setup the browser control tab with all necessary elements"""
        frame = ttk.LabelFrame(self.browser_tab, text="Browser Control")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # URL input
        url_frame = ttk.Frame(frame)
        url_frame.grid(row=0, column=0, columnspan=4, sticky=tk.W+tk.E, padx=5, pady=5)
        
        ttk.Label(url_frame, text="URL:").pack(side=tk.LEFT, padx=5)
        self.url_var = tk.StringVar(value="https://www.example.com")
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=70)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Profile selector
        profile_frame = ttk.Frame(frame)
        profile_frame.grid(row=1, column=0, columnspan=4, sticky=tk.W+tk.E, padx=5, pady=5)
        
        ttk.Label(profile_frame, text="Profile:").pack(side=tk.LEFT, padx=5)
        self.profile_var = tk.StringVar(value="default")
        self.profile_combo = ttk.Combobox(profile_frame, textvariable=self.profile_var, width=25)
        self.profile_combo.pack(side=tk.LEFT, padx=5)
        self.profile_combo['values'] = ['default']  # Will be updated when server starts
        
        # Profile management buttons
        profile_buttons_frame = ttk.Frame(profile_frame)
        profile_buttons_frame.pack(side=tk.LEFT)
        
        self.refresh_profiles_button = ttk.Button(profile_buttons_frame, text="↻", width=3, command=self.refresh_profiles)
        self.refresh_profiles_button.pack(side=tk.LEFT, padx=2)
        
        self.add_profile_button = ttk.Button(profile_buttons_frame, text="+", width=3, command=self.add_profile)
        self.add_profile_button.pack(side=tk.LEFT, padx=2)
        
        # Proxy settings
        proxy_frame = ttk.Frame(frame)
        proxy_frame.grid(row=2, column=0, columnspan=4, sticky=tk.W+tk.E, padx=5, pady=5)
        
        ttk.Label(proxy_frame, text="Proxy:").pack(side=tk.LEFT, padx=5)
        self.proxy_var = tk.StringVar()
        self.proxy_entry = ttk.Entry(proxy_frame, textvariable=self.proxy_var, width=50)
        self.proxy_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Options frame
        options_frame = ttk.Frame(frame)
        options_frame.grid(row=3, column=0, columnspan=4, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Headless mode - Set default to False so the browser is visible
        self.headless_var = tk.BooleanVar(value=False)
        self.headless_check = ttk.Checkbutton(options_frame, text="Headless Mode", variable=self.headless_var)
        self.headless_check.pack(side=tk.LEFT, padx=10)
        
        # Timeout
        ttk.Label(options_frame, text="Timeout:").pack(side=tk.LEFT, padx=5)
        self.timeout_var = tk.IntVar(value=30)
        self.timeout_spin = ttk.Spinbox(options_frame, from_=5, to=120, textvariable=self.timeout_var, width=5)
        self.timeout_spin.pack(side=tk.LEFT, padx=5)
        ttk.Label(options_frame, text="seconds").pack(side=tk.LEFT)
        
        # Buttons frame
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, columnspan=4, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start Browser & Navigate", command=self.start_browser)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.navigate_button = ttk.Button(button_frame, text="Navigate", command=self.navigate)
        self.navigate_button.pack(side=tk.LEFT, padx=5)
        
        self.close_button = ttk.Button(button_frame, text="Close Browser", command=self.close_browser)
        self.close_button.pack(side=tk.LEFT, padx=5)
        
        # Request and response displays
        req_resp_frame = ttk.Frame(frame)
        req_resp_frame.grid(row=5, column=0, columnspan=4, sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=5)
        
        # Request display
        ttk.Label(req_resp_frame, text="Request:").pack(anchor=tk.W, padx=5)
        self.browser_request = scrolledtext.ScrolledText(req_resp_frame, height=6, wrap=tk.WORD)
        self.browser_request.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Response display
        ttk.Label(req_resp_frame, text="Response:").pack(anchor=tk.W, padx=5)
        self.browser_response = scrolledtext.ScrolledText(req_resp_frame, height=8, wrap=tk.WORD)
        self.browser_response.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure grid weights for resizing
        frame.grid_rowconfigure(5, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
    def _setup_js_tab(self):
        """Setup the JavaScript tab for executing scripts in the browser"""
        frame = ttk.LabelFrame(self.js_tab, text="Execute JavaScript")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # JavaScript input
        ttk.Label(frame, text="JavaScript Code:").pack(anchor=tk.W, padx=5, pady=5)
        self.js_code = scrolledtext.ScrolledText(frame, height=8)
        self.js_code.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.js_code.insert(tk.END, "document.title")
        
        # Execution controls
        controls_frame = ttk.Frame(frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Execute button
        self.execute_js_button = ttk.Button(controls_frame, text="Execute JavaScript", command=self.execute_js)
        self.execute_js_button.pack(side=tk.LEFT, padx=5)
        
        # Timeout
        ttk.Label(controls_frame, text="Timeout:").pack(side=tk.LEFT, padx=10)
        self.js_timeout_var = tk.IntVar(value=30)
        self.js_timeout_spin = ttk.Spinbox(controls_frame, from_=5, to=120, textvariable=self.js_timeout_var, width=5)
        self.js_timeout_spin.pack(side=tk.LEFT, padx=2)
        ttk.Label(controls_frame, text="seconds").pack(side=tk.LEFT, padx=2)
        
        # Request and response displays
        ttk.Label(frame, text="Request:").pack(anchor=tk.W, padx=5)
        self.js_request = scrolledtext.ScrolledText(frame, height=6, wrap=tk.WORD)
        self.js_request.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        ttk.Label(frame, text="Response:").pack(anchor=tk.W, padx=5)
        self.js_response = scrolledtext.ScrolledText(frame, height=8, wrap=tk.WORD)
        self.js_response.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def _setup_html_tab(self):
        """Setup the HTML tab for viewing page source"""
        frame = ttk.LabelFrame(self.html_tab, text="Page HTML")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Controls frame
        controls_frame = ttk.Frame(frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Get HTML button
        self.get_html_button = ttk.Button(controls_frame, text="Get Page HTML", command=self.get_html)
        self.get_html_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Request display
        ttk.Label(frame, text="Request:").pack(anchor=tk.W, padx=5)
        self.html_request = scrolledtext.ScrolledText(frame, height=4, wrap=tk.WORD)
        self.html_request.pack(fill=tk.X, expand=False, padx=5, pady=5)
        
        # HTML content display
        ttk.Label(frame, text="HTML Content:").pack(anchor=tk.W, padx=5)
        self.html_display = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
        self.html_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def _setup_screenshot_tab(self):
        """Setup the screenshot tab for capturing browser screenshots"""
        frame = ttk.LabelFrame(self.screenshot_tab, text="Page Screenshot")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Controls frame
        controls_frame = ttk.Frame(frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Get screenshot button
        self.get_screenshot_button = ttk.Button(controls_frame, text="Take Screenshot", command=self.get_screenshot)
        self.get_screenshot_button.pack(side=tk.LEFT, pady=5, padx=5)
        
        # Save screenshot button
        self.save_screenshot_button = ttk.Button(controls_frame, text="Save Screenshot", command=self.save_screenshot)
        self.save_screenshot_button.pack(side=tk.LEFT, pady=5, padx=5)
        self.save_screenshot_button.config(state=tk.DISABLED)
        
        # Request section
        ttk.Label(frame, text="Request:").pack(anchor=tk.W, padx=5)
        self.screenshot_request = scrolledtext.ScrolledText(frame, height=4, wrap=tk.WORD)
        self.screenshot_request.pack(fill=tk.X, expand=False, padx=5, pady=5)
        
        # Screenshot display
        self.screenshot_frame = ttk.LabelFrame(frame, text="Screenshot Preview")
        self.screenshot_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.screenshot_label = ttk.Label(self.screenshot_frame)
        self.screenshot_label.pack(fill=tk.BOTH, expand=True)
        
        # Store the screenshot data
        self.current_screenshot = None
    
    def _setup_profile_management(self):
        """Setup profile management functionality"""
        self.profiles = ["default"]  # Will be populated when server starts
    
    def refresh_profiles(self):
        """Refresh the list of available profiles from the server"""
        self.status_var.set("Refreshing profiles...")
        
        # Show request details immediately
        endpoint = f"{self.api_url}/browser/profiles"
        self.root.update_idletasks()
        
        # Send request in thread to keep UI responsive
        def send_request():
            try:
                response = requests.get(endpoint)
                data = response.json()
                self.root.after(0, lambda: self._update_profiles(data))
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: self._update_profile_error(error_msg))
        
        threading.Thread(target=send_request).start()
    
    def _update_profiles(self, data):
        """Update profiles dropdown with server response"""
        if data.get("success"):
            profiles = data.get('data', {}).get('profiles', [])
            if not profiles:
                profiles = ["default"]
            
            self.profiles = profiles
            self.profile_combo['values'] = profiles
            
            # If current value is not in profiles, set to default
            if self.profile_var.get() not in profiles:
                self.profile_var.set("default")
            
            self.status_var.set("Profiles refreshed")
        else:
            self.status_var.set(f"Error: {data.get('error', 'Failed to refresh profiles')}")
    
    def _update_profile_error(self, error_msg):
        """Update status with profile error message"""
        self.status_var.set(f"Error refreshing profiles: {error_msg}")
    
    def add_profile(self):
        """Add a new browser profile"""
        profile_name = simpledialog.askstring("New Profile", "Enter profile name:")
        if profile_name and profile_name.strip():
            profile_name = profile_name.strip()
            # Add to combobox and select it
            if profile_name not in self.profiles:
                self.profiles.append(profile_name)
                self.profile_combo['values'] = self.profiles
            self.profile_var.set(profile_name)
            self.status_var.set(f"Profile '{profile_name}' will be created on next browser start")
    
    def start_browser(self):
        """Start the browser with the selected profile and navigate to the specified URL"""
        self.status_var.set("Starting browser...")
        
        # Prepare request
        payload = {
            "url": self.url_var.get(),
            "headless": self.headless_var.get(),
            "timeout": self.timeout_var.get(),
            "profile_name": self.profile_var.get()
        }
        
        if self.proxy_var.get():
            payload["proxy"] = self.proxy_var.get()
        
        # Show request details immediately
        endpoint = f"{self.api_url}/browser/start"
        request_info = f"POST {endpoint}\n\n{json.dumps(payload, indent=2)}"
        self.browser_request.delete(1.0, tk.END)
        self.browser_request.insert(tk.END, request_info)
        
        # Clear old response
        self.browser_response.delete(1.0, tk.END)
        self.browser_response.insert(tk.END, "Sending request...")
        self.root.update_idletasks()
        
        # Send request in a separate thread to keep UI responsive
        def send_request():
            try:
                response = requests.post(endpoint, json=payload)
                data = response.json()
                
                # Update UI in the main thread
                self.root.after(0, lambda: self._update_browser_response(data))
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: self._update_browser_error(error_msg))
        
        threading.Thread(target=send_request).start()
    
    def _update_browser_response(self, data):
        """Update response area with server response"""
        # Show response
        self.browser_response.delete(1.0, tk.END)
        self.browser_response.insert(tk.END, json.dumps(data, indent=2))
        
        if data.get("success"):
            profile = data.get('data', {}).get('profile', 'default')
            title = data.get('data', {}).get('title', '')
            self.status_var.set(f"Browser started with profile '{profile}' - {title}")
        else:
            self.status_var.set(f"Error: {data.get('error', 'Unknown error')}")
    
    def _update_browser_error(self, error_msg):
        """Update response area with error message"""
        self.browser_response.delete(1.0, tk.END)
        self.browser_response.insert(tk.END, f"ERROR:\n{error_msg}")
        self.status_var.set(f"Error: {error_msg}")
    
    def navigate(self):
        """Navigate to the specified URL"""
        self.status_var.set("Navigating...")
        
        # Prepare request
        payload = {
            "url": self.url_var.get(),
            "timeout": self.timeout_var.get()
        }
        
        # Show request details immediately
        endpoint = f"{self.api_url}/browser/navigate"
        request_info = f"POST {endpoint}\n\n{json.dumps(payload, indent=2)}"
        self.browser_request.delete(1.0, tk.END)
        self.browser_request.insert(tk.END, request_info)
        
        # Clear old response
        self.browser_response.delete(1.0, tk.END)
        self.browser_response.insert(tk.END, "Sending request...")
        self.root.update_idletasks()
        
        # Send request in thread
        def send_request():
            try:
                response = requests.post(endpoint, json=payload)
                data = response.json()
                self.root.after(0, lambda: self._update_navigate_response(data))
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: self._update_browser_error(error_msg))
        
        threading.Thread(target=send_request).start()
    
    def _update_navigate_response(self, data):
        """Update response area with navigation response"""
        self.browser_response.delete(1.0, tk.END)
        self.browser_response.insert(tk.END, json.dumps(data, indent=2))
        
        if data.get("success"):
            self.status_var.set(f"Navigated to URL - {data.get('data', {}).get('title', '')}")
        else:
            self.status_var.set(f"Error: {data.get('error', 'Unknown error')}")
    
    def close_browser(self):
        """Close the browser"""
        self.status_var.set("Closing browser...")
        
        # Show request details immediately
        endpoint = f"{self.api_url}/browser/close"
        request_info = f"POST {endpoint}\n\n{{}}"
        self.browser_request.delete(1.0, tk.END)
        self.browser_request.insert(tk.END, request_info)
        
        # Clear old response
        self.browser_response.delete(1.0, tk.END)
        self.browser_response.insert(tk.END, "Sending request...")
        self.root.update_idletasks()
        
        # Send request in thread
        def send_request():
            try:
                response = requests.post(endpoint)
                data = response.json()
                self.root.after(0, lambda: self._update_close_response(data))
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: self._update_browser_error(error_msg))
        
        threading.Thread(target=send_request).start()
    
    def _update_close_response(self, data):
        """Update response area with close browser response"""
        self.browser_response.delete(1.0, tk.END)
        self.browser_response.insert(tk.END, json.dumps(data, indent=2))
        
        if data.get("success"):
            self.status_var.set("Browser closed")
        else:
            self.status_var.set(f"Error: {data.get('error', 'Unknown error')}")
    
    def execute_js(self):
        """Execute JavaScript on the current page"""
        self.status_var.set("Executing JavaScript...")
        
        # Prepare request
        script = self.js_code.get(1.0, tk.END).strip()
        payload = {
            "script": script,
            "timeout": self.js_timeout_var.get()
        }
        
        # Show request details immediately
        endpoint = f"{self.api_url}/browser/javascript"
        request_info = f"POST {endpoint}\n\n{json.dumps(payload, indent=2)}"
        self.js_request.delete(1.0, tk.END)
        self.js_request.insert(tk.END, request_info)
        
        # Clear old response
        self.js_response.delete(1.0, tk.END)
        self.js_response.insert(tk.END, "Executing JavaScript...")
        self.root.update_idletasks()
        
        # Send request in thread
        def send_request():
            try:
                response = requests.post(endpoint, json=payload)
                data = response.json()
                self.root.after(0, lambda: self._update_js_response(data))
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: self._update_js_error(error_msg))
        
        threading.Thread(target=send_request).start()
    
    def _update_js_response(self, data):
        """Update response area with JavaScript execution response"""
        self.js_response.delete(1.0, tk.END)
        
        if data.get("success"):
            result = data.get('data', {})
            self.js_response.insert(tk.END, json.dumps(result, indent=2))
            self.status_var.set("JavaScript executed successfully")
        else:
            self.js_response.insert(tk.END, f"ERROR: {data.get('error', 'Unknown error')}")
            self.status_var.set(f"Error: {data.get('error', 'Unknown error')}")
    
    def _update_js_error(self, error_msg):
        """Update JavaScript response area with error message"""
        self.js_response.delete(1.0, tk.END)
        self.js_response.insert(tk.END, f"ERROR:\n{error_msg}")
        self.status_var.set(f"Error: {error_msg}")
    
    def get_html(self):
        """Get the HTML of the current page"""
        self.status_var.set("Getting HTML...")
        
        # Show request details immediately
        endpoint = f"{self.api_url}/browser/html"
        request_info = f"GET {endpoint}"
        self.html_request.delete(1.0, tk.END)
        self.html_request.insert(tk.END, request_info)
        
        # Clear old response
        self.html_display.delete(1.0, tk.END)
        self.html_display.insert(tk.END, "Fetching HTML...")
        self.root.update_idletasks()
        
        # Send request in thread
        def send_request():
            try:
                response = requests.get(endpoint)
                data = response.json()
                self.root.after(0, lambda: self._update_html_response(data))
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: self._update_html_error(error_msg))
        
        threading.Thread(target=send_request).start()
    
    def _update_html_response(self, data):
        """Update HTML display with server response"""
        self.html_display.delete(1.0, tk.END)
        
        if data.get("success"):
            html_content = data.get('data', {}).get('html', '')
            self.html_display.insert(tk.END, html_content)
            self.status_var.set("HTML retrieved successfully")
        else:
            self.html_display.insert(tk.END, f"ERROR: {data.get('error', 'Unknown error')}")
            self.status_var.set(f"Error: {data.get('error', 'Unknown error')}")
    
    def _update_html_error(self, error_msg):
        """Update HTML display with error message"""
        self.html_display.delete(1.0, tk.END)
        self.html_display.insert(tk.END, f"ERROR:\n{error_msg}")
        self.status_var.set(f"Error: {error_msg}")
    
    def get_screenshot(self):
        """Get a screenshot of the current page"""
        self.status_var.set("Taking screenshot...")
        
        # Show request details immediately
        endpoint = f"{self.api_url}/browser/screenshot"
        request_info = f"GET {endpoint}"
        self.screenshot_request.delete(1.0, tk.END)
        self.screenshot_request.insert(tk.END, request_info)
        self.root.update_idletasks()
        
        # Send request in thread
        def send_request():
            try:
                response = requests.get(endpoint)
                data = response.json()
                self.root.after(0, lambda: self._update_screenshot_response(data))
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: self._update_screenshot_error(error_msg))
        
        threading.Thread(target=send_request).start()
    
    def _update_screenshot_response(self, data):
        """Update screenshot display with server response"""
        if data.get("success"):
            screenshot_base64 = data.get('data', {}).get('screenshot', '')
            if screenshot_base64:
                # Store the screenshot data
                self.current_screenshot = screenshot_base64
                
                # Convert base64 to image
                screenshot_bytes = base64.b64decode(screenshot_base64)
                image = Image.open(io.BytesIO(screenshot_bytes))
                
                # Resize to fit the frame
                frame_width = self.screenshot_frame.winfo_width()
                frame_height = self.screenshot_frame.winfo_height()
                
                # Ensure we have valid dimensions
                if frame_width <= 1:
                    frame_width = 800
                if frame_height <= 1:
                    frame_height = 600
                
                # Calculate scaling ratio
                img_width, img_height = image.size
                ratio = min(frame_width / img_width, frame_height / img_height)
                new_width = int(img_width * ratio)
                new_height = int(img_height * ratio)
                
                # Resize image
                resized_image = image.resize((new_width, new_height), Image.LANCZOS)
                
                # Convert to PhotoImage
                tk_image = ImageTk.PhotoImage(resized_image)
                
                # Update label
                self.screenshot_label.config(image=tk_image)
                self.screenshot_label.image = tk_image  # Keep a reference
                
                # Enable save button
                self.save_screenshot_button.config(state=tk.NORMAL)
                
                self.status_var.set(f"Screenshot taken successfully")
            else:
                self.status_var.set("Error: No screenshot data received")
        else:
            self.status_var.set(f"Error: {data.get('error', 'Unknown error')}")
    
    def _update_screenshot_error(self, error_msg):
        """Update screenshot status with error message"""
        self.status_var.set(f"Error: {error_msg}")
    
    def save_screenshot(self):
        """Save the current screenshot to a file"""
        if not self.current_screenshot:
            messagebox.showerror("Error", "No screenshot to save")
            return
        
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Convert base64 to image and save
                screenshot_bytes = base64.b64decode(self.current_screenshot)
                image = Image.open(io.BytesIO(screenshot_bytes))
                image.save(file_path)
                self.status_var.set(f"Screenshot saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save screenshot: {str(e)}")
                self.status_var.set(f"Error saving screenshot: {str(e)}")
    
    def toggle_server(self):
        """Start or stop the FastAPI server"""
        if self.server_process is None:
            # Start server
            try:
                # Get the path to the app.py file
                app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
                
                # Start the server as a subprocess
                self.server_process = subprocess.Popen([sys.executable, app_path])
                
                self.server_button.config(text="Stop Server")
                self.server_status_var.set("Server: Starting...")
                
                # Wait a moment for the server to start
                self.root.after(2000, self.check_server_status)
            except Exception as e:
                messagebox.showerror("Server Error", f"Failed to start server: {str(e)}")
        else:
            # Stop server
            try:
                self.server_process.terminate()
                self.server_process = None
                self.server_button.config(text="Start Server")
                self.server_status_var.set("Server: Stopped")
            except Exception as e:
                messagebox.showerror("Server Error", f"Failed to stop server: {str(e)}")

    def check_server_status(self):
        """Check if the server is running by making a test request"""
        try:
            response = requests.get(f"{self.api_url}/docs", timeout=1)
            if response.status_code == 200:
                self.server_status_var.set("Server: Running")
                # Refresh profiles once server is running
                self.refresh_profiles()
            else:
                self.server_status_var.set(f"Server: Error (Status {response.status_code})")
        except:
            # Server might still be starting
            self.root.after(1000, self.check_server_status)

def main():
    """Main entry point for the application"""
    root = tk.Tk()
    app = BrowserControllerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
