import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getEtf, getKline } from '../api/client.js'
import KlineChart from '../components/KlineChart.jsx'
import { fmtAmount, fmtPct, fmtPctRaw } from '../utils/format.js'

const PERF_LABELS = {
  weeklyPerformance: '近1周', monthlyPerformance: '近1月', quarterlyPerformance: '近3月',
  yearlyPerformance: '近1年', ytdPerformance: '今年以来', inceptionPerformance: '成立以来',
}

export default function EtfDetailPage() {
  const { code } = useParams()
  const [meta, setMeta] = useState(null)
  const [kline, setKline] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let alive = true
    setError('')
    Promise.all([getEtf(code), getKline(code)])
      .then(([m, k]) => { if (alive) { setMeta(m); setKline(k) } })
      .catch((e) => alive && setError(e.message))
    return () => { alive = false }
  }, [code])

  if (error) return <section><div className="error-banner">{error}</div></section>
  if (!meta) return <section><p className="muted">加载中…</p></section>

  const latest = meta.latest || {}
  const perf = meta.performance || {}
  const perfEntries = Object.entries(PERF_LABELS)
    .filter(([k]) => perf[k] != null)

  return (
    <section>
      <div className="page-head">
        <Link to="/etfs" className="back">← 返回列表</Link>
        <h1>{meta.securityName} <span className="code">{meta.securityCode}</span></h1>
        <div className="change-line">
          最新价 <b className={latest.changePercent >= 0 ? 'pos' : 'neg'}>
            {latest.price != null ? latest.price.toFixed(3) : '-'}
          </b>
          <span className={latest.changePercent >= 0 ? 'pos' : 'neg'}>
            {latest.changePercent != null ? fmtPctRaw(latest.changePercent) : '-'}
          </span>
          <span className="muted">（{latest.date || '-'}）</span>
        </div>
      </div>

      <div className="meta-grid">
        <div className="meta-card"><div className="m-value">{fmtAmount(meta.scale)}</div><div className="m-label">规模</div></div>
        <div className="meta-card"><div className="m-value">{meta.premiumRate != null ? fmtPctRaw(meta.premiumRate) : '-'}</div><div className="m-label">溢价率</div></div>
        <div className="meta-card"><div className="m-value">{meta.trackingIndex || '-'}</div><div className="m-label">跟踪指数</div></div>
        <div className="meta-card"><div className="m-value">{meta.trackIndex || '-'}</div><div className="m-label">指数代码</div></div>
        <div className="meta-card"><div className="m-value">{meta.coverage?.rows || 0} 行</div><div className="m-label">K线覆盖</div></div>
        <div className="meta-card"><div className="m-value">{meta.coverage?.latestDate || '-'}</div><div className="m-label">最新K线日期</div></div>
      </div>

      <div className="perf-bar">
        {perfEntries.map(([k, v]) => (
          <span key={k} className={`perf-chip ${v >= 0 ? 'pos' : 'neg'}`}>
            {PERF_LABELS[k]} {fmtPct(v)}
          </span>
        ))}
        {!perfEntries.length && <span className="muted">无区间收益数据</span>}
      </div>

      <h2>日K线（前复权）</h2>
      {kline ? (
        <KlineChart data={kline} />
      ) : (
        <p className="muted">该标的无 K 线数据</p>
      )}
    </section>
  )
}
