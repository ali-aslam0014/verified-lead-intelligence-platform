import os
import sys

# Ensure all candidate paths (current, parent, backend) are in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
backend_dir = os.path.join(parent_dir, "backend")

for candidate in [backend_dir, parent_dir, current_dir]:
    if os.path.exists(candidate) and candidate not in sys.path:
        sys.path.insert(0, candidate)

try:
    from app.main import app
except Exception as e:
    # Fallback to create a diagnostic app if import fails
    from fastapi import FastAPI
    app = FastAPI(title="Backend Startup Diagnostic")
    
    @app.get("/{full_path:path}")
    async def diagnostic_error(full_path: str):
        return {
            "status": "error",
            "message": f"Failed to import app.main: {str(e)}",
            "sys_path": sys.path,
            "cwd": os.getcwd()
        }
