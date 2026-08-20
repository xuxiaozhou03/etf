import { useEffect, useState } from 'react'
import { getStrategies, runBacktest } from '../api/client.js'
import EtfSelect from '../components/EtfSelect.jsx'
import ParamsForm from '../components/ParamsForm.jsx'
import MetricsCard from '../components/MetricsCard.jsx'
import NavChart from '../components/NavChart.jsx'
import DrawdownChart from '../components/DrawdownChart.jsx'
import PositionChart from '../components/PositionChart.jsx'
import TradesTable from '../components/TradesTable.jsx'

const DEFAULT_COST = { commissionRate: 0.00025, slippage: 0.001, initialCapital: 1000000, rfAnnual: 0 }

export default function BacktestPage() {
  const [strategies, setStrategies] = useState([])
  const [code, setCode] = useState('510300.SH')
  const [strategy, setStrategy] = useState('dual_ma')
  const [params, setParams] = useState({})
  const [cost, setCost] = useState(DEFAULT_COST)
  const [benchmarkCode, setBenchmarkCode] = useState('510300.SH')
  const [running, setRunning] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  useEffect(() => {
    getStrategies().then((list) => {
      setStrategies(list)
      if (list.length) applyDefaults(list[0])
    }).catch(() => setStrategies([]))
  }, [])

  const applyDefaults = (s) => {
    const d = {}
    s.params.forEach((p) => { d[p.name] = p.default })
    setParams(d)
  }

  const onStrategyChange = (name) => {
    setStrategy(name)
    const s = strategies.find((x) => x.name === name)
    if (s) applyDefaults(s)
  }

  const submit = async () => {
    setRunning(true)
    setError('')
    setResult(null)
    try {
      const body = {
        code, strategy, params,
        commission_rate: cost.commissionRate,
        slippage: cost.slippage,
        initial_capital: cost.initialCapital,
        rf_annual: cost.rfAnnual,
        benchmark_code: benchmarkCode,
      }
      const res = await runBacktest(body)
      setResult(res)
    } catch (e) {
      setError(e.message)
    } finally {
      setRunning(false)
    }
  }

  const strat = strategies.find((s) => s.name === strategy)

  return (
    <section>
      <h1>在线回测</h1>
      <div className="two-col">
        <div className="panel">
          <h3>回测参数</h3>
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
            {strat?.description && <p className="muted small">{strat.description}</p>}
          </div>

          <div className="field">
            <span className="field-label">策略参数</span>
            <ParamsForm params={strat?.params || []} value={params} onChange={setParams} />
          </div>

          <div className="field">
            <span className="field-label">佣金（双边/单）</span>
            <input
              type="number" step="0.00005" min="0"
              value={cost.commissionRate}
              onChange={(e) => setCost({ ...cost, commissionRate: parseFloat(e.target.value) || 0 })}
            />
          </div>
          <div className="field">
            <span className="field-label">滑点（单边）</span>
            <input
              type="number" step="0.001" min="0"
              value={cost.slippage}
              onChange={(e) => setCost({ ...cost, slippage: parseFloat(e.target.value) || 0 })}
            />
          </div>
          <div className="field">
            <span className="field-label">初始资金</span>
            <input
              type="number" step="10000" min="10000"
              value={cost.initialCapital}
              onChange={(e) => setCost({ ...cost, initialCapital: parseFloat(e.target.value) || 0 })}
            />
          </div>
          <div className="field">
            <span className="field-label">无风险利率（年）</span>
            <input
              type="number" step="0.01"
              value={cost.rfAnnual}
              onChange={(e) => setCost({ ...cost, rfAnnual: parseFloat(e.target.value) || 0 })}
            />
          </div>
          <div className="field">
            <span className="field-label">基准（ETF 代码）</span>
            <input
              value={benchmarkCode}
              onChange={(e) => setBenchmarkCode(e.target.value.trim())}
              list="benchmarks"
            />
            <datalist id="benchmarks">
              <option value="510300.SH" />{/* 沪深300 */}
              <option value="510500.SH" />{/* 中证500 */}
              <option value="510050.SH" />{/* 上证50 */}
              <option value="159915.SZ" />{/* 创业板 */}
            </datalist>
          </div>

          <button className="btn primary" onClick={submit} disabled={running || !code || !strategy}>
            {running ? '回测中…' : '运行回测'}
          </button>
          {error && <div className="error-banner">{error}</div>}
        </div>

        <div className="result-area">
          {!result && !running && <p className="muted">配置参数后点击「运行回测」查看结果。</p>}
          {running && <p className="muted">计算中，请稍候…</p>}
          {result && (
            <>
              <div className="result-head">
                <b>{result.meta.code} · {strat?.displayName || result.meta.strategy}</b>
                <span className="muted small">
                  {result.meta.dataStart} ~ {result.meta.dataEnd} ·
                  成本 佣{result.meta.cost.commissionRate} 滑{result.meta.cost.slippage} ·
                  基准 {result.benchmarkCode}
                </span>
              </div>
              <MetricsCard metrics={result.metrics} />
              <h3>净值曲线（策略 vs 基准）</h3>
              <NavChart nav={result.nav} />
              <h3>回撤</h3>
              <DrawdownChart drawdown={result.drawdown} />
              <h3>持仓状态</h3>
              <PositionChart position={result.position} />
              <h3>交易记录</h3>
              <TradesTable trades={result.trades} />
            </>
          )}
        </div>
      </div>
    </section>
  )
}
