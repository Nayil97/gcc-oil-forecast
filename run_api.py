#!/usr/bin/env python
"""Script to run the FastAPI application with proper path setup."""

import sys
from pathlib import Path

# Add necessary paths BEFORE any imports
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir / "src"))
sys.path.insert(0, str(root_dir))

# Now import and run
if __name__ == "__main__":
    import uvicorn
    # Use the module path with proper setup
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=False)
