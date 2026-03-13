"""FastAPI应用入口"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routes import etfs, strategy, backtest
from ..web.routes import router as web_router
from ...infrastructure.storage import EtfStore
from config import settings, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    # 启动时
    setup_logging()
    print(f"Starting {settings.app_name} v{settings.app_version}")

    # 确保数据目录存在
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.cache_dir.mkdir(parents=True, exist_ok=True)

    yield

    # 关闭时
    print("Shutting down...")


# 创建应用
app = FastAPI(
    title=settings.app_name,
    description="A股ETF量化回测系统API",
    version=settings.app_version,
    lifespan=lifespan,
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
static_dir = Path(__file__).parent.parent / "web" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# 注册API路由
app.include_router(etfs.router, prefix=f"{settings.api_prefix}/etfs", tags=["ETF数据"])
app.include_router(strategy.router, prefix=f"{settings.api_prefix}/strategies", tags=["策略"])
app.include_router(backtest.router, prefix=f"{settings.api_prefix}/backtest", tags=["回测"])

# 注册Web页面路由
app.include_router(web_router, tags=["页面"])


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok"}


@app.get(f"{settings.api_prefix}/data/status")
async def data_status():
    """数据状态"""
    store = EtfStore(settings.data_dir)
    meta = store.get_metadata()
    return {
        "etf_count": meta["count"],
        "last_updated": meta["updated_at"],
        "version": meta["version"],
    }
