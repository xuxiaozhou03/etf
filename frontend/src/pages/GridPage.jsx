import { useEffect, useState } from 'react'
import { getStrategies, runGrid } from '../api/client.js'
import EtfSelect from '../components/EtfSelect.jsx'
import Heatmap from '../components/Heatmap.jsx'
import { fmtNum, fmtPct } from '../utils/format.js'

const DEFAULT_GRIDS = {
  dual_ma: { fast: '5,10,20,30', slow: '20,40,60,120' },
  bollinger: { window: '10,20,30,40', k: '1.5,2,2.5,3' },
  rsi: { window: '6,14,21', buy: '20,30', sell: '70,80' },
  buy_hold: {},
}

const METRIC_OPTIONS = [
  { key: 'annualReturn', label: '年化收益率' },
  { key: 'totalReturn', label: '总收益率' },
  { key: 'sharpe', label: '夏普比率' },
  { key: 'sortino', label: '索提诺' },
  { key: 'calmar', label: '卡玛比率' },
  { key: 'maxDrawdown', label: '最大回撤' },
  { key: 'winRate', label: '胜率' },
  { key: 'tradeCount', label: '交易次数' },
]

const TABLE_METRICS = ['totalReturn', 'annualReturn', 'maxDrawdown', 'sharpe', 'winRate', 'tradeCount']

export default function GridPage() {
  const [strategies, setStrategies] = useState([])
  const [code, setCode] = useState('510300.SH')
  const [strategy, setStrategy] = useState('dual_ma')
  const [grids, setGrids] = useState(DEFAULT_GRIDS.dual_ma)
  const [sortBy, setSortBy] = useState('annualReturn')
  const [running, setRunning] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  useEffect(() => {
    getStrategies().then((list) => {
      setStrategies(list)
      if (list.length) setGrids(DEFAULT_GRIDS[list[0].name] || {})
    }).catch(() => setStrategies([]))
  }, [])

  const onStrategyChange = (name) => {
    setStrategy(name)
    setResult(null)
    setGrids(DEFAULT_GRIDS[name] || {})
  }

  const submit = async () => {
    setRunning(true)
    setError('')
    setResult(null)
    try {
      const paramGrids = {}
      for (const [name, csv] of Object.entries(grids)) {
        const vals = String(csv).split(',').map((s) => Number(s.trim())).filter((n) => !Number.isNaN(n))
        if (vals.length) paramGrids[name] = vals
      }
      if (!Object.keys(paramGrids).length) throw new Error('请至少为一个参数填写网格取值')
      const body = { code, strategy, param_grids: paramGrids, sort_by: sortBy, limit: 500 }
      const res = await runGrid(body)
      setResult(res)
    } catch (e) {
      setError(e.message)
    } finally {
      setRunning(false)
    }
  }

  const strat = strategies.find((s) => s.name === strategy)
  const paramNames = result?.paramNames || strat?.params.map((p) => p.name) || []

  return (
    <section>
      <h1>参数网格扫描</h1>
      <div className="panel">
        <div className="grid-form">
          <div className="field">
            <span className="field-label">标的</span>
            <EtfSelect value={code} onChange={setCode} />
          </div>
          <div className="field">
            <span className="field-label">策略</span>
            <select value={strategy} onChange={(e) => onStrategyChange(e.target.value)}>
              {strategies.map((s) => (
                <option key={s.name} value={s.name}>{s.displayName}</option>
              ))}
            </select>
          </div>
          {strat?.params.map((p) => (
            <div className="field" key={p.name}>
              <span className="field-label">{p.label}（逗号分隔取值）</span>
              <input
                value={grids[p.name] ?? ''}
                placeholder={p.default}
                onChange={(e) => setGrids({ ...grids, [p.name]: e.target.value })}
              />
            </div>
          ))}
          <div className="field">
            <span className="field-label">排序指标</span>
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
              {METRIC_OPTIONS.map((m) => (
                <option key={m.key} value={m.key}>{m.label}</option>
              ))}
            </select>
          </div>
          <button className="btn primary" onClick={submit} disabled={running}>
            {running ? '扫描中…' : '扫描网格'}
          </button>
        </div>
        {error && <div className="error-banner">{error}</div>}
      </div>

      {result && (
        <>
          <div className="result-head">
            <b>{result.code} · {strat?.displayName} · {result.rows.length} 组合</b>
            <span className="muted small">按 {METRIC_OPTIONS.find((m) => m.key === result.sortBy)?.label} 降序</span>
          </div>

          {paramNames.length >= 2 && (
            <>
              <h3>参数热力图（{result.sortBy}）</h3>
              <Heatmap rows={result.rows} paramX={paramNames[0]} paramY={paramNames[1]} metric={result.sortBy} />
            </>
          )}

          <h3>批量对比表</h3>
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  {paramNames.map((p) => <th key={p}>{p}</th>)}
                  {TABLE_METRICS.map((m) => (
                    <th key={m}>{METRIC_OPTIONS.find((x) => x.key === m)?.label || m}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {result.rows.map((r, i) => (
                  <tr key={i}>
                    {paramNames.map((p) => <td key={p}>{fmtNum(r[p], 4)}</td>)}
                    <td>{fmtPct(r.totalReturn)}</td>
                    <td>{fmtPct(r.annualReturn)}</td>
                    <td className="neg">{fmtPct(r.maxDrawdown)}</td>
                    <td>{fmtNum(r.sharpe)}</td>
                    <td>{fmtPct(r.winRate)}</td>
                    <td>{r.tradeCount}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </section>
  )
}
