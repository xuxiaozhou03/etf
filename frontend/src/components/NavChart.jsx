import { useMemo } from 'react'
import useEChart from '../hooks/useEChart.js'

/** 净值曲线：策略 vs 基准。nav 为 [{date, strategy, benchmark?}]。 */
export default function NavChart({ nav, height = 360 }) {
  const option = useMemo(() => {
    if (!nav || !nav.length) return {}
    const dates = nav.map((d) => d.date)
    return {
      animation: false,
      tooltip: { trigger: 'axis', valueFormatter: (v) => Number(v).toFixed(3) },
      legend: { top: 4, data: ['策略', '基准'] },
      grid: { left: 56, right: 16, top: 34, bottom: 24 },
      xAxis: { type: 'category', data: dates, axisLine: { lineStyle: { color: '#d0d0d0' } } },
      yAxis: { scale: true, splitLine: { lineStyle: { color: '#f0f0f0' } } },
      dataZoom: [
        { type: 'inside', start: 0, end: 100 },
        { type: 'slider', bottom: 0, height: 16 },
      ],
      series: [
        {
          name: '策略', type: 'line', data: nav.map((d) => d.strategy),
          showSymbol: false, lineStyle: { width: 1.5, color: '#3f51b5' },
          areaStyle: { opacity: 0.05 },
        },
        ...(nav[0].benchmark != null
          ? [{
              name: '基准', type: 'line', data: nav.map((d) => d.benchmark),
              showSymbol: false, lineStyle: { width: 1.5, color: '#9e9e9e' },
            }]
          : []),
      ],
    }
  }, [nav])
  const ref = useEChart(option)
  return <div ref={ref} style={{ width: '100%', height }} />
}
