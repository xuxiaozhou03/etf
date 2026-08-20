import { useMemo } from 'react'
import useEChart from '../hooks/useEChart.js'

/** 持仓状态阶梯图（0 空仓 / 1 满仓）。position 为 [{date, position}]。 */
export default function PositionChart({ position, height = 140 }) {
  const option = useMemo(() => {
    if (!position || !position.length) return {}
    const dates = position.map((d) => d.date)
    return {
      animation: false,
      tooltip: { trigger: 'axis', valueFormatter: (v) => (v === 1 ? '满仓' : '空仓') },
      grid: { left: 40, right: 16, top: 16, bottom: 24 },
      xAxis: { type: 'category', data: dates, show: false },
      yAxis: { min: 0, max: 1, splitNumber: 1, axisLabel: { formatter: (v) => (v === 1 ? '持' : '空') } },
      dataZoom: [
        { type: 'inside', start: 0, end: 100 },
        { type: 'slider', bottom: 0, height: 16 },
      ],
      series: [
        {
          type: 'line',
          data: position.map((d) => d.position),
          step: 'end',
          showSymbol: false,
          lineStyle: { width: 2, color: '#1e88e5' },
          areaStyle: { color: 'rgba(30,136,229,0.15)' },
        },
      ],
    }
  }, [position])
  const ref = useEChart(option)
  return <div ref={ref} style={{ width: '100%', height }} />
}
