// 数值格式化工具

export function fmtPct(v, digits = 2) {
  if (v == null || Number.isNaN(v)) return '-'
  return `${(v * 100).toFixed(digits)}%`
}

export function fmtNum(v, digits = 2) {
  if (v == null || Number.isNaN(v)) return '-'
  return Number(v).toFixed(digits)
}

export function fmtPctRaw(v, digits = 2) {
  // 已是百分数值（如涨跌幅 1.23）直接加 %
  if (v == null || Number.isNaN(v)) return '-'
  return `${Number(v).toFixed(digits)}%`
}

export function fmtAmount(v) {
  if (v == null || Number.isNaN(v)) return '-'
  if (v >= 1e8) return `${(v / 1e8).toFixed(2)} 亿`
  if (v >= 1e4) return `${(v / 1e4).toFixed(2)} 万`
  return Number(v).toFixed(0)
}

export function fmtDate(v) {
  return v == null ? '-' : String(v)
}
