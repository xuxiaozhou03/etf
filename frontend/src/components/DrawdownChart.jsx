import { useMemo } from 'react'
import useEChart from '../hooks/useEChart.js'

/** 回撤面积图：策略 vs 基准。drawdown 为 [{date, strategy, benchmark?}]。 */
export default function DrawdownChart({ drawdown, height = 260 }) {
  const option = useMemo(() => {
    if (!drawdown || !drawdown.length) return {}
    const dates = drawdown.map((d) => d.date)
    return {
      animation: false,
      tooltip: { trigger: 'axis', valueFormatter: (v) => (v == null ? '-' : `${(v * 100).toFixed(2)}%`) },
      legend: { top: 4, data: ['策略', '基准'] },
      grid: { left: 56, right: 16, top: 30, bottom: 24 },
      xAxis: { type: 'category', data: dates, axisLine: { lineStyle: { color: '#d0d0d0' } } },
      yAxis: {
        type: 'value', max: 0,
        axisLabel: { formatter: (v) => `${(v * 100).toFixed(0)}%` },
        splitLine: { lineStyle: { color: '#f0f0f0' } },
      },
      dataZoom: [
        { type: 'inside', start: 0, end: 100 },
        { type: 'slider', bottom: 0, height: 16 },
      ],
      series: [
        {
          name: '策略', type: 'line', data: drawdown.map((d) => d.strategy),
          showSymbol: false, lineStyle: { width: 1, color: '#e53935' },
          areaStyle: { color: 'rgba(229,57,53,0.18)' },
        },
        ...(drawdown[0].benchmark != null
          ? [{
              name: '基准', type: 'line', data: drawdown.map((d) => d.benchmark),
              showSymbol: false, lineStyle: { width: 1, color: '#9e9e9e' },
              areaStyle: { color: 'rgba(158,158,158,0.12)' },
            }]
          : []),
      ],
    }
  }, [drawdown])
  const ref = useEChart(option)
  return <div ref={ref} style={{ width: '100%', height }} />
}
