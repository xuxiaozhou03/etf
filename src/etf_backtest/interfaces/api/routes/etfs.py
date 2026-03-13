"""ETF相关路由"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Query, HTTPException, Depends

from ...application.dto import Response, EtfListItem, EtfDetail, KlineItem, KlineResponse
from ...infrastructure.storage import EtfStore
from ...infrastructure.data import EfinanceProvider
from config import settings

router = APIRouter()


def get_etf_store() -> EtfStore:
    """获取ETF存储实例"""
    return EtfStore(settings.data_dir)


def get_data_provider() -> EfinanceProvider:
    """获取数据提供者实例"""
    return EfinanceProvider(cache_dir=settings.cache_dir)


@router.get("", response_model=Response)
async def get_etfs(
    category: Optional[str] = Query(None, description="分类筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    store: EtfStore = Depends(get_etf_store),
):
    """获取ETF列表"""
    etfs = store.load_etfs()

    # 筛选
    if category:
        etfs = [e for e in etfs if e.get("category") == category]

    if keyword:
        keyword_lower = keyword.lower()
        etfs = [
            e for e in etfs
            if keyword_lower in e.get("code", "").lower()
            or keyword_lower in e.get("name", "").lower()
        ]

    # 分页
    total = len(etfs)
    start = (page - 1) * page_size
    end = start + page_size
    etf_list = etfs[start:end]

    return Response(data={
        "list": etf_list,
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.get("/{code}", response_model=Response)
async def get_etf(
    code: str,
    store: EtfStore = Depends(get_etf_store),
):
    """获取ETF详情"""
    etf = store.get_etf(code)

    if not etf:
        raise HTTPException(status_code=404, detail=f"ETF {code} not found")

    return Response(data=etf)


@router.get("/{code}/klines", response_model=Response)
async def get_klines(
    code: str,
    start_date: Optional[str] = Query(None, description="起始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    limit: Optional[int] = Query(None, description="返回条数"),
    provider: EfinanceProvider = Depends(get_data_provider),
    store: EtfStore = Depends(get_etf_store),
):
    """获取K线数据"""
    # 解析日期
    start = date.fromisoformat(start_date) if start_date else None
    end = date.fromisoformat(end_date) if end_date else None

    try:
        df = await provider.get_klines(code, start, end)

        if df.empty:
            return Response(data={
                "code": code,
                "name": "",
                "klines": [],
            })

        # 限制条数
        if limit:
            df = df.tail(limit)

        # 获取ETF名称
        etf = store.get_etf(code)
        name = etf.get("name", "") if etf else ""

        # 转换为列表
        df = df.reset_index()
        klines = []

        for _, row in df.iterrows():
            klines.append({
                "date": row["date"].strftime("%Y-%m-%d") if hasattr(row["date"], "strftime") else str(row["date"])[:10],
                "open": float(row.get("open", 0)),
                "high": float(row.get("high", 0)),
                "low": float(row.get("low", 0)),
                "close": float(row.get("close", 0)),
                "volume": float(row.get("volume", 0)),
                "amount": float(row.get("amount", 0)),
                "turnover_rate": float(row.get("turnover_rate", 0)),
                "change_pct": float(row.get("change_pct", 0)),
            })

        return Response(data={
            "code": code,
            "name": name,
            "klines": klines,
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{code}/quote", response_model=Response)
async def get_quote(
    code: str,
    provider: EfinanceProvider = Depends(get_data_provider),
):
    """获取实时行情"""
    try:
        df = await provider.get_realtime_quote([code])

        if df.empty:
            raise HTTPException(status_code=404, detail=f"ETF {code} quote not found")

        quote = df.iloc[0].to_dict()
        return Response(data=quote)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
