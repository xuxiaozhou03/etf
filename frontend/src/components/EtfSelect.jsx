import { useEffect, useState } from 'react'
import { getEtfs } from '../api/client.js'

/** 标的搜索选择器：加载 287 只 ETF，支持代码/名称过滤，返回选中的 code。 */
export default function EtfSelect({ value, onChange }) {
  const [all, setAll] = useState([])
  const [kw, setKw] = useState('')

  useEffect(() => {
    let alive = true
    getEtfs({ sort: 'scale', order: 'desc' })
      .then((list) => alive && setAll(list))
      .catch(() => alive && setAll([]))
    return () => { alive = false }
  }, [])

  const filtered = kw
    ? all.filter((e) =>
        e.securityCode.toUpperCase().includes(kw.toUpperCase()) ||
        String(e.securityName || '').toUpperCase().includes(kw.toUpperCase()))
    : all

  return (
    <div className="etf-select">
      <input
        className="search-input"
        placeholder="搜索代码 / 名称…"
        value={kw}
        onChange={(e) => setKw(e.target.value)}
      />
      <select value={value || ''} onChange={(e) => onChange(e.target.value)} size={6}>
        {filtered.map((e) => (
          <option key={e.securityCode} value={e.securityCode}>
            {e.securityCode} {e.securityName}
          </option>
        ))}
      </select>
    </div>
  )
}
