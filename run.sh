#!/bin/bash
# 启动脚本

cd "$(dirname "$0")"

# 检查是否安装依赖
if ! python -c "import fastapi" 2>/dev/null; then
    echo "正在安装依赖..."
    pip install -e .
fi

# 启动服务
echo "启动ETF回测系统..."
echo "访问地址: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo ""

uvicorn etf_backtest.interfaces.api.main:app --host 0.0.0.0 --port 8000 --reload
