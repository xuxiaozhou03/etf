import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getEtfs } from '../api/client.js'
import { fmtAmount, fmtDate, fmtPctRaw } from '../utils/format.js'

const COLUMNS = [
  { key: 'securityCode', label: '代码', sortable: true },
  { key: 'securityName', label: '名称', sortable: true },
  { key: 'price', label: '最新价', sortable: true },
  { key: 'changePercent', label: '涨跌幅', sortable: true },
  { key: 'scale', label: '规模', sortable: true },
  { key: 'premiumRate', label: '溢价率', sortable: true },
  { key: 'trackingIndex', label: '跟踪指数', sortable: true },
  { key: 'date', label: '数据日期', sortable: true },
]

export default function EtfListPage() {
  const navigate = useNavigate()
  const [rows, setRows] = useState([])
  const [search, setSearch] = useState('')
  const [sort, setSort] = useState({ key: 'scale', order: 'desc' })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let alive = true
    setLoading(true)
    getEtfs({ sort: sort.key, order: sort.order })
      .then((list) => alive && setRows(list))
      .catch((e) => alive && setError(e.message))
      .finally(() => alive && setLoading(false))
    return () => { alive = false }
  }, [sort])

  const filtered = useMemo(() => {
    const q = search.trim().toUpperCase()
    if (!q) return rows
    return rows.filter((r) =>
      r.securityCode.toUpperCase().includes(q) ||
      String(r.securityName || '').toUpperCase().includes(q))
  }, [rows, search])

  const onSort = (key) => {
    setSort((s) => (s.key === key
      ? { key, order: s.order === 'desc' ? 'asc' : 'desc' }
      : { key, order: 'desc' }))
  }

  return (
    <section>
      <div className="page-head">
        <h1>ETF 行情列表</h1>
        <span className="muted">{rows.length} 只</span>
        <input
          className="search-input grow"
          placeholder="搜索代码 / 名称（如 510300 或 沪深300）"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>
      {error && <div className="error-banner">加载失败：{error}</div>}
      {loading ? (
        <p className="muted">加载中…</p>
      ) : (
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                {COLUMNS.map((c) => (
                  <th
                    key={c.key}
                    className={c.sortable ? 'sortable' : ''}
                    onClick={() => c.sortable && onSort(c.key)}
                  >
                    {c.label}
                    {sort.key === c.key && <span className="sort-mark">{sort.order === 'desc' ? ' ↓' : ' ↑'}</span>}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map((r) => (
                <tr key={r.securityCode} onClick={() => navigate(`/etfs/${r.securityCode}`)}>
                  <td>{r.securityCode}</td>
                  <td>{r.securityName}</td>
                  <td>{r.latest?.price != null ? r.latest.price.toFixed(3) : '-'}</td>
                  <td className={r.latest?.changePercent >= 0 ? 'pos' : 'neg'}>
                    {r.latest?.changePercent != null ? fmtPctRaw(r.latest.changePercent) : '-'}
                  </td>
                  <td>{fmtAmount(r.scale)}</td>
                  <td className={r.premiumRate > 0 ? 'pos' : r.premiumRate < 0 ? 'neg' : ''}>
                    {r.premiumRate != null ? fmtPctRaw(r.premiumRate) : '-'}
                  </td>
                  <td className="muted">{r.trackingIndex || '-'}</td>
                  <td>{fmtDate(r.latest?.date)}</td>
                </tr>
              ))}
              {!filtered.length && (
                <tr><td colSpan={COLUMNS.length} className="muted center">无匹配标的</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
