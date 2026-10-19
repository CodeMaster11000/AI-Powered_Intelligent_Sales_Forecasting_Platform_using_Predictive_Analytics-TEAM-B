import subprocess
import time
import sys
import os

# Enable utf-8 on Windows stdout if possible
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def main():
    print("=" * 70)
    print(">> Starting SalesGenie AI Dual-Microservice Runtime")
    print("   * Backend: FastAPI REST microservice (http://127.0.0.1:8000)")
    print("   * Frontend: Streamlit presentation layer (http://localhost:8501)")
    print("   * AI Layer: LangGraph Multi-Agent Orchestration (Jayant Vaibhav)")
    print("=" * 70)
    
    # 1. Start FastAPI Backend via uvicorn
    backend_cmd = [
        sys.executable, "-m", "uvicorn", 
        "backend.app.main:app", 
        "--host", "127.0.0.1", 
        "--port", "8000"
    ]
    
    backend_proc = subprocess.Popen(backend_cmd)
    print(">> Initializing FastAPI backend microservices on port 8000...")
    time.sleep(2)
    
    # 2. Start Streamlit Frontend
    streamlit_cmd = [
        sys.executable, "-m", "streamlit", "run", 
        "frontend/app.py", 
        "--server.port", "8501", 
        "--server.headless", "true"
    ]
    
    print(">> Launching Streamlit dashboard on http://localhost:8501 ...")
    try:
        frontend_proc = subprocess.Popen(streamlit_cmd)
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\n>> Shutting down SalesGenie AI services...")
    finally:
        backend_proc.terminate()
        try:
            frontend_proc.terminate()
        except Exception:
            pass
        print(">> Shutdown complete.")

if __name__ == "__main__":
    main()
