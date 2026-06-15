import subprocess
import os
import time

def main():
    print("Starting CounselAI Services...")
    print("=========================================")
    print("Press Ctrl+C in this terminal to stop all services.")
    print("=========================================\n")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Define commands and their working directories
    services = [
        {
            "name": "Java Backend (Port 8080)",
            "cmd": "mvnw.cmd spring-boot:run",
            "cwd": os.path.join(base_dir, "backend")
        },
        {
            "name": "AI Service (Port 8001)",
            "cmd": ".\\venv\\Scripts\\python.exe -m uvicorn main:app --port 8001 --host 0.0.0.0",
            "cwd": os.path.join(base_dir, "ai-service")
        },
        {
            "name": "React Frontend (Port 5173)",
            "cmd": "npm run dev",
            "cwd": os.path.join(base_dir, "frontend")
        }
    ]

    processes = []
    for service in services:
        try:
            # We remove CREATE_NEW_CONSOLE so they output in the same terminal
            p = subprocess.Popen(service['cmd'], cwd=service['cwd'], shell=True)
            processes.append((service['name'], p))
        except Exception as e:
            print(f"Failed to start {service['name']}: {e}")

    try:
        # Keep the main process alive to catch Ctrl+C
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nCtrl+C detected! Stopping all services...")
        
        # Kill all child processes gracefully
        for name, p in processes:
            print(f"Terminating {name}...")
            if os.name == 'nt':
                # On Windows, shell=True runs inside cmd.exe, so we kill the whole process tree (/T)
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(p.pid)], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                p.terminate()
                
        print("All services stopped successfully. Goodbye!")

if __name__ == "__main__":
    main()
