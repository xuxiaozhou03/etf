#!/usr/bin/env python3
"""Web 服务入口：启动 FastAPI + 托管前端。

用法：python run.py  →  http://127.0.0.1:8000
"""

from __future__ import annotations

import uvicorn

if __name__ == "__main__":
    uvicorn.run("etf_quant.api.app:app", host="127.0.0.1", port=8000)
