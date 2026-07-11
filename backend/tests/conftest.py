import sys
from pathlib import Path

# backend/ をフラット import (from config import ...) できるようにする
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
