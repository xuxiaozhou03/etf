# 使用 Qlib

## 量化交易完整功能清单

## 推荐量化交易工具链（自主可控、开源优先）

1. 数据获取与处理：AkShare（A 股、ETF、可转债、REIT，免费且易用）
2. 因子工程与特征分析：Qlib（全流程）、Alphalens（因子分析）、TA-Lib（技术指标）
3. 策略开发与回测：backtrader（灵活、易扩展）、Qlib（集成回测）、bt（策略组合）
4. 策略优化：Optuna、hyperopt（参数调优）
5. 模型训练与集成：scikit-learn、LightGBM、XGBoost、PyTorch（主流机器学习框架）
6. 虚拟盘交易执行与信号推送：backtrader、Qlib + smtplib/yagmail（邮件通知）
7. 结果分析与可视化：Pyfolio、Alphalens、matplotlib、plotly
8. 风险管理：backtrader、bt、Qlib
9. 扩展性与集成：backtrader、Qlib（均为模块化设计，易于集成第三方工具）

以上工具均为主流开源包，支持自主开发和灵活扩展，适合个人和团队量化研究。

1. 数据获取与处理

   - 功能：自动化收集、清洗、格式化多市场行情数据，主要聚焦于 A 股市场，尤其是 ETF、可转债、REIT 等资产类型。
   - 推荐工具：AkShare（唯一推荐，支持 A 股、ETF、可转债、REIT，免费且易用）。

2. 因子工程

   - 功能：特征构建、因子生成、筛选与管理，支持多因子策略。
   - 主流包：Qlib、Alphalens、Pyfolio、TA-Lib。

3. 策略开发

   - 功能：基础策略模板（如动量、均值回归、轮动等），支持自定义策略编写。
   - 主流包：backtrader、zipline、vnpy、bt、pyalgotrade。

4. 回测框架

   - 功能：模拟历史行情下的策略表现，支持多资产类型、资金管理、交易撮合。
   - 主流包：backtrader、zipline、vnpy、bt、pyalgotrade、Qlib。

5. 策略优化

   - 功能：参数调优、批量回测、结果对比，持续提升策略效果。
   - 主流包：Optuna、hyperopt、bt、Qlib。

6. 模型训练与集成

   - 功能：支持机器学习模型训练、预测与集成。
   - 主流包：scikit-learn、LightGBM、XGBoost、PyTorch、Qlib。

7. 虚拟盘交易执行

   - 功能：在虚拟盘环境下进行持仓管理和资金变动模拟，所有交易信号自动发送到指定独立邮箱，便于人工或半自动执行，无需真实下单。
   - 主流包：backtrader（虚拟盘与信号推送可自定义）、Qlib（可集成通知）、第三方邮件库（如 smtplib、yagmail）。

8. 结果分析与可视化

   - 功能：基于虚拟盘交易数据，统计收益率、回撤、夏普比率等指标，展示交易明细、资金曲线等图表。
   - 主流包：Pyfolio、Alphalens、matplotlib、plotly、Qlib。

9. 风险管理

   - 功能：基于虚拟盘持仓和资金变动，进行止损、止盈、仓位控制、风险暴露监控。
   - 主流包：backtrader、bt、Qlib、vnpy。

10. 扩展性与集成
    - 功能：模块化设计，易于扩展第三方数据源、策略库、交易接口。
    - 主流包：backtrader、Qlib、vnpy、zipline。
