import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src")) # Добавляем src в PYTHONPATH

from src._main import _main

if __name__ == "__main__":
    _main()