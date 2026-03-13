"""常量定义"""

# 交易相关
TRADING_DAYS_PER_YEAR = 252
RISK_FREE_RATE = 0.015  # 无风险利率

# ETF类型
ETF_TYPE_SH = 0  # 上证
ETF_TYPE_SZ = 1  # 深证

# ETF分类
ETF_CATEGORIES = {
    "wide": "宽基",
    "industry": "行业",
    "theme": "主题",
    "commodity": "商品",
    "cross_border": "跨境",
    "bond": "债券",
    "money": "货币",
}

# 常用指数代码
INDEX_CODES = {
    "000300": "沪深300",
    "000905": "中证500",
    "000852": "中证1000",
    "000016": "上证50",
    "399006": "创业板指",
    "000688": "科创50",
}

# 指数代码映射（东方财富格式）
INDEX_CODE_MAP = {
    "000300": "sh000300",
    "000905": "sh000905",
    "000852": "sh000852",
    "000016": "sh000016",
    "399006": "sz399006",
    "000688": "sh000688",
}

# 涨跌停限制
LIMIT_UP_PCT = 0.10   # 涨停10%
LIMIT_DOWN_PCT = 0.10  # 跌停10%

# ST股票涨跌停限制
ST_LIMIT_UP_PCT = 0.05
ST_LIMIT_DOWN_PCT = 0.05
