import { useMemo } from 'react'
import useEChart from '../hooks/useEChart.js'

/**
 * 参数热力图：x = paramX 取值，y = paramY 取值，z = 目标指标。
 * rows: 网格结果行；paramX/paramY: 两维参数名；metric: 指标键。
 */
export default function Heatmap({ rows, paramX, paramY, metric, height = 440 }) {
  const option = useMemo(() => {
    if (!rows || !rows.length || !paramX || !paramY) return {}
    const xs = [...new Set(rows.map((r) => r[paramX]))].sort((a, b) => a - b)
    const ys = [...new Set(rows.map((r) => r[paramY]))].sort((a, b) => b - a)
    const xIdx = new Map(xs.map((v, i) => [v, i]))
    const yIdx = new Map(ys.map((v, i) => [v, i]))
    const vals = rows
      .filter((r) => r[metric] != null)
      .map((r) => [xIdx.get(r[paramX]), yIdx.get(r[paramY]), r[metric]])
    return {
      animation: false,
      tooltip: {
        formatter: (p) => `${paramX}=${p.value[0] == null ? '' : xs[p.value[0]]}, ${paramY}=${p.value[1] == null ? '' : ys[p.value[1]]}<br/>${metric}: ${p.value[2] == null ? '-' : p.value[2].toFixed(4)}`,
      },
      grid: { left: 64, right: 80, top: 24, bottom: 48 },
      xAxis: { type: 'category', data: xs.map(String), splitArea: { show: true } },
      yAxis: { type: 'category', data: ys.map(String), splitArea: { show: true } },
      visualMap: {
        min: Math.min(...vals.map((v) => v[2])),
        max: Math.max(...vals.map((v) => v[2])),
        orient: 'vertical',
        right: 8,
        top: 'center',
        calculable: true,
        inRange: { color: ['#26a69a', '#ffb300', '#e53935'] },
        formatter: (v) => v.toFixed(3),
      },
      series: [
        {
          type: 'heatmap',
          data: vals,
          label: { show: true, fontSize: 10, formatter: (p) => (p.value[2] == null ? '' : p.value[2].toFixed(3)) },
          emphasis: { itemStyle: { borderColor: '#333', borderWidth: 1 } },
        },
      ],
    }
  }, [rows, paramX, paramY, metric])
  const ref = useEChart(option)
  return <div ref={ref} style={{ width: '100%', height }} />
}
