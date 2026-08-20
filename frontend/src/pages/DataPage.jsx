import { useEffect, useRef, useState } from 'react'
import { getDataStats, getUpdateStatus, triggerUpdate } from '../api/client.js'

export default function DataPage() {
  const [stats, setStats] = useState(null)
  const [taskId, setTaskId] = useState('')
  const [task, setTask] = useState(null)
  const [limit, setLimit] = useState(0)
  const [delay, setDelay] = useState(0.3)
  const pollRef = useRef(null)

  const loadStats = () => {
    getDataStats().then(setStats).catch(() => setStats(null))
  }

  useEffect(() => {
    loadStats()
    return () => stopPoll()
  }, [])

  const stopPoll = () => {
    if (pollRef.current) {
      clearInterval(pollRef.current)
      pollRef.current = null
    }
  }

  const startPoll = (id) => {
    stopPoll()
    pollRef.current = setInterval(async () => {
      try {
        const t = await getUpdateStatus(id)
        setTask(t)
        if (t.status !== 'running') {
          stopPoll()
          loadStats()
        }
      } catch (_) { /* 任务可能已消失，继续轮询 */ }
    }, 1500)
  }

  const start = async () => {
    setTask(null)
    try {
      const { taskId: id } = await triggerUpdate(Number(limit) || 0, Number(delay) || 0.1)
      setTaskId(id)
      startPoll(id)
    } catch (e) {
      setTask({ status: 'error', message: e.message })
    }
  }

  const pct = (done, total) => (total ? Math.round((done / total) * 100) : 0)

  return (
    <section>
      <h1>数据管理</h1>

      <div className="stat-grid">
        <div className="stat-card"><div className="stat-value">{stats?.etfCount ?? '-'}</div><div className="stat-label">ETF 总数</div></div>
        <div className="stat-card"><div className="stat-value">{stats?.klineCodes ?? '-'}</div><div className="stat-label">有K线标的</div></div>
        <div className="stat-card"><div className="stat-value">{(stats?.klineRows ?? 0).toLocaleString()}</div><div className="stat-label">K线行数</div></div>
        <div className="stat-card"><div className="stat-value">{stats?.ok ?? '-'} / {stats?.error ?? '-'}</div><div className="stat-label">成功/失败</div></div>
      </div>

      <div className="panel">
        <h3>增量更新</h3>
        <div className="grid-form">
          <div className="field">
            <span className="field-label">限制标的数（0=全部）</span>
            <input type="number" min="0" value={limit} onChange={(e) => setLimit(e.target.value)} />
          </div>
          <div className="field">
            <span className="field-label">请求间隔（秒）</span>
            <input type="number" min="0.05" step="0.05" value={delay} onChange={(e) => setDelay(e.target.value)} />
          </div>
          <button className="btn primary" onClick={start} disabled={!!pollRef.current}>
            {pollRef.current ? '更新中…' : '开始更新'}
          </button>
        </div>

        {task && (
          <div className="task-panel">
            <div className="task-line">
              任务 {task.taskId || taskId}
              {task.status === 'done'
                ? <span className="pos"> 完成</span>
                : task.status === 'error'
                  ? <span className="neg"> 失败：{task.message}</span>
                  : <span> 运行中… {task.total ? pct(task.done, task.total) : 0}%</span>}
            </div>
            <div className="progress">
              <div className="progress-bar" style={{ width: `${pct(task.done, task.total)}%` }} />
            </div>
            <div className="muted small">{task.message}</div>
          </div>
        )}
      </div>

      <h3>K线覆盖明细</h3>
      <div className="table-wrap">
        <table className="data-table">
          <thead>
            <tr><th>代码</th><th>名称</th><th>行数</th><th>起始</th><th>最新</th><th>状态</th></tr>
          </thead>
          <tbody>
            {(stats?.coverage || []).map((c) => (
              <tr key={c.code}>
                <td>{c.code}</td>
                <td>{c.name || '-'}</td>
                <td>{c.rows}</td>
                <td>{c.start || '-'}</td>
                <td>{c.end || '-'}</td>
                <td className={c.status === 'ok' ? 'pos' : 'neg'}>{c.status || '-'}</td>
              </tr>
            ))}
            {!stats?.coverage?.length && <tr><td colSpan="6" className="muted center">暂无K线数据</td></tr>}
          </tbody>
        </table>
      </div>
    </section>
  )
}
