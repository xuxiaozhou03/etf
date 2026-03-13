"""配置管理模块"""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # 应用配置
    app_name: str = "ETF量化回测系统"
    app_version: str = "0.1.0"
    debug: bool = False

    # API配置
    api_prefix: str = "/api"
    cors_origins: list[str] = ["*"]

    # 数据配置
    data_dir: Path = Path("./data")
    cache_dir: Path = Path("./data/cache")
    cache_expire_hours: int = 24

    # 回测配置
    default_initial_capital: float = 1_000_000.0
    default_commission_rate: float = 0.0003
    default_min_commission: float = 5.0
    default_stamp_duty_rate: float = 0.001
    default_transfer_fee_rate: float = 0.00001
    default_slippage_rate: float = 0.001

    # 日志配置
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 确保目录存在
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)


# 全局配置实例
settings = Settings()
