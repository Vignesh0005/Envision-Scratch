"""
Start both HTTP and WebSocket camera services
"""

import subprocess
import sys
import os
import time
import signal
from threading import Thread

def start_http_server():
    """Start HTTP camera server"""
    print("Starting HTTP Camera Server on port 5000...")
    subprocess.run([sys.executable, "start_server.py"])

def start_websocket_server():
    """Start WebSocket camera server"""
    print("Starting WebSocket Camera Server on port 8765...")
    subprocess.run([sys.executable, "start_websocket_service.py"])

if __name__ == "__main__":
    print("=" * 60)
    print("ENVISION Camera Services")
    print("=" * 60)
    print("Starting both HTTP and WebSocket services...")
    print("HTTP Server: http://localhost:5000")
    print("WebSocket Server: ws://localhost:8765")
    print("Press Ctrl+C to stop all services")
    print("=" * 60)
    
    processes = []
    
    try:
        # Start HTTP server in a separate process
        http_process = subprocess.Popen(
            [sys.executable, "start_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes.append(http_process)
        
        # Wait a bit for HTTP server to start
        time.sleep(2)
        
        # Start WebSocket server in a separate process
        ws_process = subprocess.Popen(
            [sys.executable, "start_websocket_service.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes.append(ws_process)
        
        # Wait for processes
        for process in processes:
            process.wait()
            
    except KeyboardInterrupt:
        print("\nShutting down all services...")
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
        print("All services stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        for process in processes:
            try:
                process.terminate()
            except:
                pass
        sys.exit(1)

