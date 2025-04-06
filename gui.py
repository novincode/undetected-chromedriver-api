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
import socket

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
        
        # Set application icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app-icon.png")
        if os.path.exists(icon_path):
            try:
                icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, icon)
            except Exception as e:
                print(f"Failed to load application icon: {e}")
        
        # API base URL
        self.api_url = "http://localhost:8000"
        self.server_process = None
        self.browser_started = False  # Track browser state
        
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
        self.status_bar.pack(fill=tk.X, expand=True)
        
    def _setup_browser_tab(self):
        """Setup the browser control tab with all necessary elements"""
        frame = ttk.LabelFrame(self.browser_tab, text="Browser Control")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # URL input with navigate button next to it
        url_frame = ttk.Frame(frame)
        url_frame.grid(row=0, column=0, columnspan=4, sticky=tk.W+tk.E, padx=5, pady=5)
        
        ttk.Label(url_frame, text="URL:").pack(side=tk.LEFT, padx=5)
        self.url_var = tk.StringVar(value="https://www.example.com")
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=70)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Navigate button next to URL
        self.navigate_button = ttk.Button(url_frame, text="Navigate", command=self.navigate)
        self.navigate_button.pack(side=tk.LEFT, padx=5)
        
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
        
        # Server status indicator in options frame
        ttk.Separator(options_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=15, fill=tk.Y)
        self.server_status_var = tk.StringVar()
        self.server_status_var.set("Server: Stopped")
        ttk.Label(options_frame, textvariable=self.server_status_var).pack(side=tk.LEFT, padx=5)
        
        # Buttons frame - Reorganized with server controls
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, columnspan=4, pady=10)
        
        # Server button first
        self.server_button = ttk.Button(button_frame, text="Start Server", command=self.toggle_server)
        self.server_button.pack(side=tk.LEFT, padx=5)
        
        # Add separator
        ttk.Separator(button_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=15, fill=tk.Y)
        
        # Browser control buttons
        self.browser_buttons_frame = ttk.Frame(button_frame)
        self.browser_buttons_frame.pack(side=tk.LEFT)
        
        # Will show either Start Browser or Close Browser depending on state
        self.browser_button = ttk.Button(self.browser_buttons_frame, text="Start Browser", command=self.toggle_browser)
        self.browser_button.pack(side=tk.LEFT, padx=5)
        
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
        
        # Initialize button states
        self.update_button_states()
        
    def update_button_states(self):
        """Update button states based on browser and server status"""
        server_running = self.server_process is not None
        
        # Update server button text
        if server_running:
            self.server_button.config(text="Stop Server")
        else:
            self.server_button.config(text="Start Server")
            
        # Update browser control buttons
        if not server_running:
            # Disable browser controls if server is not running
            self.browser_button.config(state=tk.DISABLED)
            self.navigate_button.config(state=tk.DISABLED)
        else:
            # Enable browser button
            self.browser_button.config(state=tk.NORMAL)
            
            # Set browser button text and navigation based on browser state
            if self.browser_started:
                self.browser_button.config(text="Close Browser")
                self.navigate_button.config(state=tk.NORMAL)
            else:
                self.browser_button.config(text="Start Browser")
                self.navigate_button.config(state=tk.DISABLED)
    
    def toggle_browser(self):
        """Toggle browser state - starts or closes the browser depending on current state"""
        if self.browser_started:
            self.close_browser()
        else:
            self.start_browser()
    
    def start_browser(self):
        """Start the browser with the selected profile"""
        self.status_var.set("Starting browser...")
        
        # Prepare request - include URL, which is required by the API
        payload = {
            "url": self.url_var.get(),  # URL is required
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
        
        # Disable buttons during operation to prevent multiple clicks
        self.browser_button.config(state=tk.DISABLED)
        
        # Send request in a separate thread to keep UI responsive
        def send_request():
            try:
                response = requests.post(endpoint, json=payload)
                data = response.json()
                
                # Update UI in the main thread
                self.root.after(0, lambda: self._update_browser_start_response(data))
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: self._update_browser_error(error_msg))
        
        threading.Thread(target=send_request).start()
    
    def _update_browser_start_response(self, data):
        """Update response area with browser start response"""
        # Show response
        self.browser_response.delete(1.0, tk.END)
        self.browser_response.insert(tk.END, json.dumps(data, indent=2))
        
        if data.get("success"):
            self.browser_started = True
            profile = data.get('data', {}).get('profile', 'default')
            self.status_var.set(f"Browser started with profile '{profile}'")
        else:
            self.status_var.set(f"Error: {data.get('error', 'Unknown error')}")
            
        # Update button states
        self.update_button_states()
    
    def navigate(self):
        """Navigate to the specified URL"""
        if not self.browser_started:
            messagebox.showinfo("Browser Not Started", "Please start the browser first.")
            return
            
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
        
        # Disable navigate button during operation
        self.navigate_button.config(state=tk.DISABLED)
        
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
            
        # Re-enable navigate button
        self.navigate_button.config(state=tk.NORMAL)
    
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
            self.browser_started = False
            self.status_var.set("Browser closed")
            # Update button states
            self.update_button_states()
        else:
            self.status_var.set(f"Error: {data.get('error', 'Unknown error')}")
            
        # Ensure browser button is enabled
        self.browser_button.config(state=tk.NORMAL)
    
    def _update_browser_error(self, error_msg):
        """Update browser response area with error message"""
        self.browser_response.delete(1.0, tk.END)
        self.browser_response.insert(tk.END, f"ERROR:\n{error_msg}")
        self.status_var.set(f"Error: {error_msg}")
    
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
    
    def execute_js(self):
        """Execute JavaScript on the current page"""
        if not self.browser_started:
            messagebox.showinfo("Browser Not Started", "Please start the browser first.")
            return
            
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
        
        # Disable button during operation
        self.execute_js_button.config(state=tk.DISABLED)
        
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
        
        # Re-enable execute button
        self.execute_js_button.config(state=tk.NORMAL)

    def _update_js_error(self, error_msg):
        """Update JavaScript response area with error message"""
        self.js_response.delete(1.0, tk.END)
        self.js_response.insert(tk.END, f"ERROR:\n{error_msg}")
        self.status_var.set(f"Error: {error_msg}")
        
        # Re-enable execute button
        self.execute_js_button.config(state=tk.NORMAL)
    
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
    
    def get_html(self):
        """Get the HTML of the current page"""
        if not self.browser_started:
            messagebox.showinfo("Browser Not Started", "Please start the browser first.")
            return
            
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
        
        # Disable button during operation
        self.get_html_button.config(state=tk.DISABLED)
        
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
        
        # Re-enable get HTML button
        self.get_html_button.config(state=tk.NORMAL)
    
    def _update_html_error(self, error_msg):
        """Update HTML display with error message"""
        self.html_display.delete(1.0, tk.END)
        self.html_display.insert(tk.END, f"ERROR:\n{error_msg}")
        self.status_var.set(f"Error: {error_msg}")
        
        # Re-enable get HTML button
        self.get_html_button.config(state=tk.NORMAL)
    
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
    
    def get_screenshot(self):
        """Get a screenshot of the current page"""
        if not self.browser_started:
            messagebox.showinfo("Browser Not Started", "Please start the browser first.")
            return
            
        self.status_var.set("Taking screenshot...")
        
        # Show request details immediately
        endpoint = f"{self.api_url}/browser/screenshot"
        request_info = f"GET {endpoint}"
        self.screenshot_request.delete(1.0, tk.END)
        self.screenshot_request.insert(tk.END, request_info)
        self.root.update_idletasks()
        
        # Disable button during operation
        self.get_screenshot_button.config(state=tk.DISABLED)
        
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
    
    def is_server_running(self):
        """Check if the API server is already running"""
        try:
            response = requests.get(f"{self.api_url}/docs", timeout=0.5)
            return response.status_code == 200
        except:
            return False

    def check_port_available(self, port=8000):
        """Check if the specified port is available"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        available = False
        try:
            sock.bind(("0.0.0.0", port))
            available = True
        except:
            available = False
        finally:
            sock.close()
        return available

    def toggle_server(self):
        """Start or stop the FastAPI server"""
        # Show request details in browser request/response area
        self.browser_request.delete(1.0, tk.END)
        self.browser_response.delete(1.0, tk.END)
        
        if self.server_process is None:
            # Check if server is already running
            if self.is_server_running():
                # Server is already running, just use it
                self.browser_request.insert(tk.END, "Server is already running at http://localhost:8000\nUsing existing server.")
                self.browser_response.insert(tk.END, "Connected to existing server.")
                self.server_status_var.set("Server: Running (External)")
                self.server_process = True  # Use a truthy value to indicate external server
                self.update_button_states()
                # Refresh profiles
                self.refresh_profiles()
                return
            
            # Check if port is available
            if not self.check_port_available(8000):
                self.browser_request.insert(tk.END, "Port 8000 is already in use, but server is not responding.")
                self.browser_response.insert(tk.END, "ERROR: Port 8000 is already in use by another application.\nPlease free the port and try again.")
                messagebox.showerror("Server Error", "Port 8000 is already in use by another application.\nPlease free the port and try again.")
                return
            
            # Start server
            try:
                # Get the path to the app.py file
                app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
                
                # Show request info
                self.browser_request.insert(tk.END, f"Starting server process:\n{sys.executable} {app_path}")
                
                # Start the server as a subprocess
                self.server_process = subprocess.Popen([sys.executable, app_path], 
                                                     stderr=subprocess.PIPE, 
                                                     stdout=subprocess.PIPE)
                
                self.server_status_var.set("Server: Starting...")
                self.browser_response.insert(tk.END, "Server process started. Waiting for API to become available...")
                
                # Wait a moment for the server to start
                self.root.after(100, self.check_server_status)
            except Exception as e:
                error_msg = str(e)
                self.browser_response.insert(tk.END, f"ERROR: Failed to start server\n{error_msg}")
                messagebox.showerror("Server Error", f"Failed to start server: {error_msg}")
        else:
            # Stop server
            try:
                # Show request info
                self.browser_request.insert(tk.END, "Stopping server process...")
                
                # If it's an external server, we don't actually stop it
                if self.server_process is True:
                    self.browser_response.insert(tk.END, "Disconnected from external server.\nNote: The server was started externally and will continue running.")
                    self.server_process = None
                else:
                    self.server_process.terminate()
                    self.server_process = None
                    self.browser_response.insert(tk.END, "Server process terminated successfully.")
                
                self.server_status_var.set("Server: Stopped")
                self.browser_started = False  # Reset browser state when server stops
            except Exception as e:
                error_msg = str(e)
                self.browser_response.insert(tk.END, f"ERROR: Failed to stop server\n{error_msg}")
                messagebox.showerror("Server Error", f"Failed to stop server: {error_msg}")
        
        # Update button states
        self.update_button_states()

    def check_server_status(self):
        """Check if the server is running by making a test request"""
        try:
            response = requests.get(f"{self.api_url}/docs", timeout=0.5)
            if response.status_code == 200:
                self.server_status_var.set("Server: Running")
                self.browser_response.insert(tk.END, "\nServer is now running and API is available.")
                # Refresh profiles once server is running
                self.refresh_profiles()
                # Update button states
                self.update_button_states()
                return
        except:
            pass
            
        # Check if the process is still running
        if isinstance(self.server_process, subprocess.Popen):
            if self.server_process.poll() is not None:
                # Process has terminated
                stdout, stderr = self.server_process.communicate()
                self.server_process = None
                self.server_status_var.set("Server: Failed to start")
                error_txt = stderr.decode('utf-8', errors='replace') if stderr else "Unknown error"
                self.browser_response.insert(tk.END, f"\nServer failed to start:\n{error_txt}")
                self.update_button_states()
                return
        
        # Wait longer and try again
        self.browser_response.insert(tk.END, ".")
        self.root.update_idletasks()  # Update UI immediately
        self.root.after(500, self.check_server_status)  # Check again after 500ms

def main():
    """Main entry point for the application"""
    root = tk.Tk()
    app = BrowserControllerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
