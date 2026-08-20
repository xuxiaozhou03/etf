# ETF量化回测系统

个人研究的本地 A 股 ETF 日线量化回测工具。需求与方案见 [docs/PRD.md](docs/PRD.md)。

## 数据爬虫（当前阶段）

数据源：
- ETF 列表/快照：红火箭 `hongsehuojian.com`（一次全量 1640 只，含规模/成交额/分类/区间业绩）
- 日K线：芝士财富 `stock.cheesefortune.com`（`dayKV2` 接口，全量历史，含复权因子）

### 安装

```bash
pip install -r requirements.txt
```

### 执行

```bash
# 1. 全量爬取（ETF 列表 + 全部日K线，落库 data/etf.db；已成功的标的自动跳过，可中断续跑）
python scripts/crawl.py

# 2. 小规模试跑（如只抓 10 只，或指定代码）
python scripts/crawl.py --limit 10
python scripts/crawl.py --codes 510300.SH,159915.SZ

# 3. 数据校验（统计 + 字段约束检查）
python scripts/verify.py
```

常用参数：`--db` 指定库路径、`--delay` 请求间隔（默认 0.3s）、`--force` 强制重抓、`--list-only` 只抓列表。

### 落库结构（SQLite）

- `etf_list`：ETF 元数据（代码/名称/规模/溢价率/追踪指数）；价格、成交额、区间业绩由日K线实时推导，不落库
- `daily_kline`：日K线（code, date, open, close, high, low, prev_close, volume, amount）
- `adjust_factors`：复权因子（分红日才有记录）
- `float_shares`：流通份额（按日记录）
- `crawl_state`：抓取状态（断点续传用）

说明：芝士财富 `dayKV2` 的 `t` 参数与 `zstokv1` 头需按前端算法动态生成（已破解并内置，见 `etf_quant/datasource/kline.py`）。
