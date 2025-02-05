import sys
from pathlib import Path

# Add src directory to Python path
src_dir = str(Path(__file__).parent.parent / "src")
sys.path.append(src_dir)
