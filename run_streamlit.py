#!/usr/bin/env python
"""Script to run the Streamlit application with proper path setup."""

import sys
from pathlib import Path

# Add necessary paths
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir / "src"))
sys.path.insert(0, str(root_dir / "app"))
sys.path.insert(0, str(root_dir))

if __name__ == "__main__":
    import streamlit.web.cli as stcli
    
    sys.argv = ["streamlit", "run", str(root_dir / "app" / "Home.py")]
    sys.exit(stcli.main())
