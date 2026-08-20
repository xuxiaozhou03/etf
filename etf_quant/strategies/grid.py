"""参数网格生成：多参数笛卡尔积。"""

from __future__ import annotations

import itertools
from typing import Dict, List


def make_grid(param_grids: Dict[str, list]) -> List[dict]:
    """参数网格笛卡尔积 → 参数组合列表。

    例：{'fast': [5, 10, 20], 'slow': [20, 40, 60]} → 9 组。
    """
    keys = list(param_grids.keys())
    if not keys:
        return [{}]
    values = [param_grids[k] for k in keys]
    return [dict(zip(keys, combo)) for combo in itertools.product(*values)]
