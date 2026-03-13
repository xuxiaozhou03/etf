# ETF量化回测系统 - 后端

A股ETF量化回测系统后端服务

## 技术栈

- Python 3.11+
- FastAPI
- Pandas / NumPy
- efinance / akshare (数据获取)

## 安装

```bash
# 使用 pip
pip install -e .

# 或使用 poetry
poetry install
```

## 运行

```bash
# 开发模式
uvicorn etf_backtest.interfaces.api.main:app --reload --port 8000

# 或
python -m etf_backtest.interfaces.api.main
```

## API文档

启动后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 项目结构

```
backend/
├── config/                 # 配置
├── src/
│   └── etf_backtest/
│       ├── domain/         # 领域层
│       │   ├── backtest/   # 回测引擎
│       │   ├── strategy/   # 策略引擎
│       │   └── analysis/   # 分析引擎
│       ├── application/    # 应用层
│       ├── infrastructure/ # 基础设施层
│       │   ├── data/       # 数据获取
│       │   └── storage/    # 存储
│       ├── interfaces/     # 接口层
│       │   └── api/        # REST API
│       └── shared/         # 共享模块
├── tests/                  # 测试
└── data/                   # 数据文件
```

## API接口

### ETF相关

- `GET /api/etfs` - 获取ETF列表
- `GET /api/etfs/{code}` - 获取ETF详情
- `GET /api/etfs/{code}/klines` - 获取K线数据

### 策略相关

- `GET /api/strategies` - 获取策略列表
- `GET /api/strategies/{name}` - 获取策略详情

### 回测相关

- `POST /api/backtest` - 创建回测任务
- `GET /api/backtest/{id}` - 查询回测状态
- `GET /api/backtest/{id}/result` - 获取回测结果
