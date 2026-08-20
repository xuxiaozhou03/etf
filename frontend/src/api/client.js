// API 客户端：所有请求走相对路径 /api，开发期由 Vite 代理到 127.0.0.1:8000，
// 生产期由 FastAPI 托管同源提供。

async function request(path, options = {}) {
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = await res.json()
      detail = body.detail || JSON.stringify(body)
    } catch (_) { /* 非 JSON 错误体，保留状态文本 */ }
    throw new Error(detail)
  }
  return res.json()
}

export const getEtfs = (opts = {}) => {
  const q = new URLSearchParams()
  if (opts.search) q.set('search', opts.search)
  if (opts.sort) q.set('sort', opts.sort)
  if (opts.order) q.set('order', opts.order)
  const qs = q.toString()
  return request(`/api/etfs${qs ? '?' + qs : ''}`)
}

export const getEtf = (code) => request(`/api/etfs/${encodeURIComponent(code)}`)
export const getKline = (code, ma = '5,10,20,60') =>
  request(`/api/etfs/${encodeURIComponent(code)}/kline?ma=${ma}`)
export const getStrategies = () => request('/api/strategies')
export const runBacktest = (body) => request('/api/backtest', { method: 'POST', body: JSON.stringify(body) })
export const runGrid = (body) => request('/api/backtest/grid', { method: 'POST', body: JSON.stringify(body) })
export const getDataStats = () => request('/api/data/stats')
export const triggerUpdate = (limit = 0, delay = 0.3) =>
  request(`/api/data/update?limit=${limit}&delay=${delay}`, { method: 'POST' })
export const getUpdateStatus = (taskId) => request(`/api/data/update/${taskId}`)
