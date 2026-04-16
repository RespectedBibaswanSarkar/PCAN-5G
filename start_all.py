import subprocess
import os
import sys
import time
import webbrowser


def print_banner():
    """Print welcome banner."""
    print("\n" + "="*80)
    print("  5G CROSS-LAYER DQN PCAN-5G RESEARCH PLATFORM v2.0")
    print("  Baseline vs Optimized Comparison with IEEE-Standard Graph Generation")
    print("="*80)
    print("\n  NEW FEATURES:")
    print("    [NEW] Dual-phase controlled experiments (Baseline vs PCAN-5G)")
    print("    [NEW] Identical initial conditions for fair comparison")
    print("    [NEW] Comprehensive data logging to CSV")
    print("    [NEW] IEEE-standard publication-quality graphs (PNG @ 300 DPI, PDF)")
    print("    [NEW] Multi-scenario automated experiments (low/medium/high traffic)")
    print("    [NEW] Manual parameter control (traffic, thresholds, failure rates)")
    print("    [NEW] REST API for experiment orchestration")
    print("    [NEW] Real-time topology visualization")
    print("\n" + "="*80 + "\n")


def print_urls():
    """Print important URLs."""
    print("\n" + "-"*80)
    print("  IMPORTANT URLS:")
    print("-"*80)
    print("  Backend API:             http://localhost:8000")
    print("  API Documentation:       http://localhost:8000/docs")
    print("  Interactive API Tester:  http://localhost:8000/redoc")
    print("  Frontend Dashboard:      http://localhost:5173")
    print("-"*80 + "\n")


def print_quick_start():
    """Print quick start guide."""
    print("\n" + "-"*80)
    print("  QUICK START GUIDE:")
    print("-"*80)
    print("  1. Run Single Experiment:")
    print("     POST http://localhost:8000/experiment/run")
    print(
        "     {\"scenario\": \"medium_traffic\", \"num_steps\": 100, \"optimized_episodes\": 3}")
    print("")
    print("  2. Run Multi-Scenario Experiments:")
    print("     POST http://localhost:8000/experiment/run-multi-scenario")
    print(
        "     {\"scenarios\": [\"low_traffic\", \"medium_traffic\", \"high_congestion\"]}")
    print("")
    print("  3. Control Parameters:")
    print("     POST http://localhost:8000/parameters/update")
    print("     {\"traffic_scenario\": \"high\", \"congestion_threshold\": 0.7}")
    print("")
    print("  4. Get Results:")
    print("     GET http://localhost:8000/data/comparison-table")
    print("     GET http://localhost:8000/graphs/list")
    print("")
    print("  5. Standalone Experiments:")
    print("     cd backend && python run_experiments.py")
    print("-"*80 + "\n")


def run_commands():
    """Start all components."""
    # Adjust paths for Windows
    backend_dir = os.path.join(os.getcwd(), "backend")
    frontend_dir = os.path.join(os.getcwd(), "frontend")

    print_banner()
    print("Starting 5G PCAN-5G Research Platform...\n")

    # Check if directories exist
    if not os.path.exists(backend_dir):
        print(f"ERROR: Backend directory not found: {backend_dir}")
        sys.exit(1)

    if not os.path.exists(frontend_dir):
        print(f"ERROR: Frontend directory not found: {frontend_dir}")
        sys.exit(1)

    # Install dependencies if needed
    print("  [0/3] Checking dependencies...")
    try:
        # Install Python backend dependencies
        print("       Checking Python dependencies...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"],
            cwd=backend_dir,
            check=True,
            capture_output=True
        )
        print("       [OK] Python dependencies checked")
    except Exception as e:
        print(f"       [WARN] Warning: Could not verify Python dependencies: {e}")

    try:
        # Install Node dependencies
        print("       Checking Node.js dependencies...")
        subprocess.run(
            ["npm", "install", "--silent"],
            cwd=frontend_dir,
            shell=True,
            check=True,
            capture_output=True
        )
        print("       [OK] Node.js dependencies checked")
    except Exception as e:
        print(f"       [WARN] Warning: Could not verify Node dependencies: {e}")

    # Start Backend
    print("  [1/3] Launching FastAPI Backend (Port 8000)...")
    try:
        backend_process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=backend_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
        )
        print("       [OK] Backend starting (new window)...")
    except Exception as e:
        print(f"       [FAIL] Failed to start backend: {e}")
        sys.exit(1)

    # Give backend time to start
    print("       Waiting for backend to initialize...")
    time.sleep(4)

    # Start Frontend
    print("  [2/3] Launching Vite Frontend (Port 5173)...")
    try:
        frontend_process = subprocess.Popen(
            "npm run dev",
            cwd=frontend_dir,
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
        )
        print("       [OK] Frontend starting (new window)...")
    except Exception as e:
        print(f"       [FAIL] Failed to start frontend: {e}")
        backend_process.terminate()
        sys.exit(1)

    # Wait for services to fully start
    print("       Waiting for frontend to initialize...")
    time.sleep(4)

    # Display information
    print_urls()
    print_quick_start()

    print("="*80)
    print("  [OK] All services started successfully!")
    print("  Press Ctrl+C to shutdown all services")
    print("="*80 + "\n")

    # Try to open browser
    try:
        webbrowser.open('http://localhost:5173')
        print("  Opening frontend in default browser...\n")
    except:
        pass

    # Keep services running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n" + "="*80)
        print("  Shutting down all services...")
        print("="*80)

        backend_process.terminate()
        frontend_process.terminate()

        try:
            backend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_process.kill()

        try:
            backend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            frontend_process.kill()

        print("  [OK] All services stopped")
        print("  Output files preserved in: ./logs and ./graphs")
        print("="*80 + "\n")
        sys.exit(0)


if __name__ == "__main__":
    run_commands()
