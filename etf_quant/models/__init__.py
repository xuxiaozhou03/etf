"""数据模型包：每张表一个模块，各自维护 schema 与读写。

本文件汇总导出各模型类与 ALL_MODELS（决定建表顺序）。
"""

from etf_quant.models.base import ColumnDef, Model
from etf_quant.models.etf_list import EtfList
from etf_quant.models.daily_kline import DailyKline
from etf_quant.models.adjust_factor import AdjustFactor
from etf_quant.models.float_share import FloatShare
from etf_quant.models.crawl_state import CrawlState

ALL_MODELS: list = [EtfList, DailyKline, AdjustFactor, FloatShare, CrawlState]

__all__ = [
    "ColumnDef", "Model", "EtfList", "DailyKline", "AdjustFactor", "FloatShare",
    "CrawlState", "ALL_MODELS",
]
