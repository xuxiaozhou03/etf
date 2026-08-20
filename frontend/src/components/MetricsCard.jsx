import { fmtPct, fmtNum } from '../utils/format.js'

/** 回测指标卡：百分比类 + 比率类 + 计数类。metrics 为 /api/backtest 返回的 metrics 对象。 */
export default function MetricsCard({ metrics }) {
  if (!metrics) return null
  const cards = [
    { label: '总收益率', value: fmtPct(metrics.totalReturn), accent: metrics.totalReturn >= 0 },
    { label: '年化收益率', value: fmtPct(metrics.annualReturn), accent: metrics.annualReturn >= 0 },
    { label: '年化波动率', value: fmtPct(metrics.annualVol), accent: null },
    { label: '最大回撤', value: fmtPct(metrics.maxDrawdown), accent: false },
    { label: '夏普比率', value: fmtNum(metrics.sharpe), accent: metrics.sharpe >= 1 },
    { label: '索提诺', value: fmtNum(metrics.sortino), accent: metrics.sortino >= 1 },
    { label: '卡玛比率', value: fmtNum(metrics.calmar), accent: metrics.calmar >= 1 },
    { label: '胜率', value: fmtPct(metrics.winRate), accent: (metrics.winRate || 0) >= 0.5 },
    { label: '盈亏比', value: fmtNum(metrics.profitLossRatio), accent: (metrics.profitLossRatio || 0) >= 1 },
    { label: '交易次数', value: fmtNum(metrics.tradeCount, 0), accent: null },
    { label: '年化换手', value: `${fmtNum(metrics.annualTurnover)} 次`, accent: null },
    { label: '平均持仓', value: `${fmtNum(metrics.avgHoldDays, 1)} 天`, accent: null },
  ]
  if (metrics.alpha != null) {
    cards.push(
      { label: 'Alpha', value: fmtPct(metrics.alpha), accent: metrics.alpha >= 0 },
      { label: 'Beta', value: fmtNum(metrics.beta), accent: null },
      { label: '信息比率', value: fmtNum(metrics.infoRatio), accent: metrics.infoRatio >= 0 },
    )
  }
  const peak = metrics.maxDrawdownPeak ? `${metrics.maxDrawdownPeak} ~ ${metrics.maxDrawdownTrough}` : null

  return (
    <div className="metrics">
      {cards.map((c) => (
        <div className={`metric ${c.accent == null ? '' : c.accent ? 'good' : 'bad'}`} key={c.label}>
          <div className="metric-value">{c.value}</div>
          <div className="metric-label">{c.label}</div>
        </div>
      ))}
      {peak && (
        <div className="metric">
          <div className="metric-value small">{peak}</div>
          <div className="metric-label">回撤区间</div>
        </div>
      )}
    </div>
  )
}
