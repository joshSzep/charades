import django
import os
import sys
from pathlib import Path


# Add src directory to Python path
src_dir = str(Path(__file__).parent.parent / "src")
sys.path.append(src_dir)


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "charades.config.settings")
django.setup()
