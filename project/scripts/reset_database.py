import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.db import init

if __name__ == "__main__":
    init(reset=True)
    print("Reset this project's synthetic teaching database.")
