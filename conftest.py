import os
import sys

# Ensure project root is on sys.path so tests can import project modules reliably
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Make sure Django settings are available as an environment variable for subprocesses
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
