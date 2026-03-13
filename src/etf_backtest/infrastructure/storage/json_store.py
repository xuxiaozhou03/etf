"""JSON文件存储"""

import json
from datetime import datetime, date
from pathlib import Path
from typing import Any, TypeVar, Type
import pandas as pd
from pydantic import BaseModel

from ...shared.exceptions import DataError
from config import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


class JSONEncoder(json.JSONEncoder):
    """自定义JSON编码器"""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, pd.Timestamp):
            return obj.strftime("%Y-%m-%d")
        elif hasattr(obj, "model_dump"):
            return obj.model_dump()
        return super().default(obj)


class JSONStore:
    """JSON文件存储"""

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def read(self) -> dict:
        """读取JSON文件"""
        if not self.file_path.exists():
            return {}

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {self.file_path}, {e}")
            raise DataError(f"JSON解析失败: {e}")

    def write(self, data: dict | list) -> None:
        """写入JSON文件"""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2, cls=JSONEncoder)
        except Exception as e:
            logger.error(f"写入JSON失败: {self.file_path}, {e}")
            raise DataError(f"写入JSON失败: {e}")

    def read_model(self, model_class: Type[T]) -> T | None:
        """读取并解析为Pydantic模型"""
        data = self.read()
        if not data:
            return None
        return model_class(**data)

    def write_model(self, model: BaseModel) -> None:
        """写入Pydantic模型"""
        self.write(model.model_dump())


class EtfStore:
    """ETF数据存储"""

    def __init__(self, data_dir: str | Path = "./data"):
        self.data_dir = Path(data_dir)
        self.etf_file = self.data_dir / "etfs.json"
        self._store = JSONStore(self.etf_file)

    def load_etfs(self) -> list[dict]:
        """加载ETF列表"""
        data = self._store.read()
        return data.get("etfs", [])

    def save_etfs(self, etfs: list[dict], version: str = "1.0") -> None:
        """保存ETF列表"""
        data = {
            "version": version,
            "updated_at": datetime.now().strftime("%Y-%m-%d"),
            "etfs": etfs,
        }
        self._store.write(data)

    def get_etf(self, code: str) -> dict | None:
        """获取单个ETF"""
        etfs = self.load_etfs()
        for etf in etfs:
            if etf.get("code") == code:
                return etf
        return None

    def get_etf_codes(self) -> list[str]:
        """获取所有ETF代码"""
        etfs = self.load_etfs()
        return [etf.get("code") for etf in etfs if etf.get("code")]

    def get_metadata(self) -> dict:
        """获取元数据"""
        data = self._store.read()
        return {
            "version": data.get("version", "unknown"),
            "updated_at": data.get("updated_at", "unknown"),
            "count": len(data.get("etfs", [])),
        }
