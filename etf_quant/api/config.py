"""API 层全局配置。"""

from __future__ import annotations

from pathlib import Path

DB_PATH = str(Path(__file__).resolve().parent.parent.parent / "data" / "etf.db")
