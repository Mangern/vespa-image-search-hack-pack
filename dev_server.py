import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=5001,
        reload=True,
        reload_dirs=["app"],
        log_level="info",
        timeout_keep_alive=0,
        timeout_graceful_shutdown=1,
    )
