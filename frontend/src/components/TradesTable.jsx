import { useState } from 'react'
import { fmtNum, fmtPct } from '../utils/format.js'

/** 交易记录表（round-trip）：买入 → 卖出，含收益与持仓天数。 */
export default function TradesTable({ trades }) {
  const [limit, setLimit] = useState(50)
  if (!trades || !trades.length) return <p className="muted">无交易记录（策略全程未开仓）</p>

  const shown = trades.slice(0, limit)
  const totalReturn = trades.reduce((s, t) => s + t.returnPct, 0)
  const avgDays = trades.reduce((s, t) => s + t.holdDays, 0) / trades.length

  return (
    <div>
      <div className="summary-line">
        共 {trades.length} 笔 · 平均收益 <b>{fmtPct(totalReturn / trades.length)}</b> · 平均持仓{' '}
        <b>{fmtNum(avgDays, 1)}</b> 天
      </div>
      <div className="table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              <th>#</th><th>买入日期</th><th>买入价</th><th>卖出日期</th>
              <th>卖出价</th><th>收益率</th><th>持仓(天)</th>
            </tr>
          </thead>
          <tbody>
            {shown.map((t, i) => (
              <tr key={i}>
                <td>{i + 1}</td>
                <td>{t.buyDate}</td>
                <td>{fmtNum(t.buyPrice, 4)}</td>
                <td>{t.sellDate}</td>
                <td>{fmtNum(t.sellPrice, 4)}</td>
                <td className={t.returnPct >= 0 ? 'pos' : 'neg'}>{fmtPct(t.returnPct)}</td>
                <td>{t.holdDays}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {trades.length > limit && (
        <button className="btn ghost" onClick={() => setLimit((l) => l + 100)}>
          加载更多（剩余 {trades.length - limit} 笔）
        </button>
      )}
    </div>
  )
}
