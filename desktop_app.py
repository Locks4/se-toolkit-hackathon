"""
Goal Tracker Desktop App Launcher
This launches the web app in a native Windows window using Edge/Chrome App Mode.
"""
import subprocess
import sys
import os
import time
import webbrowser
import signal

def start_backend():
    """Start the FastAPI backend server"""
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
    
    # Start uvicorn server
    process = subprocess.Popen(
        [sys.executable, 'main.py'],
        cwd=backend_dir,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    return process

def wait_for_server(url='http://localhost:8000', timeout=30):
    """Wait for the server to be ready"""
    import urllib.request
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            urllib.request.urlopen(url)
            return True
        except:
            time.sleep(0.5)
    return False

def open_app_in_window():
    """Open the app in Edge/Chrome App Mode (looks like native window)"""
    # Try Edge first, then Chrome
    edge_paths = [
        os.path.expandvars(r'%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe'),
        os.path.expandvars(r'%ProgramFiles%\Microsoft\Edge\Application\msedge.exe'),
        os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe'),
    ]
    
    chrome_paths = [
        os.path.expandvars(r'%ProgramFiles%\Google\Chrome\Application\chrome.exe'),
        os.path.expandvars(r'%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe'),
        os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe'),
    ]
    
    browser_path = None
    
    # Try Edge first
    for path in edge_paths:
        if os.path.exists(path):
            browser_path = path
            break
    
    # Try Chrome if Edge not found
    if not browser_path:
        for path in chrome_paths:
            if os.path.exists(path):
                browser_path = path
                break
    
    if browser_path:
        app_url = 'http://localhost:8000'
        subprocess.Popen([
            browser_path,
            f'--app={app_url}',
            '--window-size=1400,900',
            '--no-first-run',
            '--no-default-browser-check'
        ])
    else:
        # Fallback to default browser
        webbrowser.open('http://localhost:8000')

def main():
    print("=" * 60)
    print("  Goal Tracker - Starting Desktop App")
    print("=" * 60)
    print()
    print("Starting backend server...")
    
    # Start backend
    backend_process = start_backend()
    
    # Wait for server to be ready
    print("Waiting for server to start...")
    if wait_for_server():
        print("✓ Server is ready!")
        print()
        print("Opening Goal Tracker in desktop window...")
        open_app_in_window()
        print()
        print("=" * 60)
        print("  Goal Tracker is now running!")
        print("=" * 60)
        print()
        print("Keep this window open. Close it to exit the app.")
        print()
        
        # Keep the script running
        try:
            backend_process.wait()
        except KeyboardInterrupt:
            print("\nShutting down...")
            backend_process.terminate()
    else:
        print("✗ Server failed to start")
        backend_process.terminate()
        sys.exit(1)

if __name__ == '__main__':
    main()
