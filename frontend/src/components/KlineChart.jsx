import { useMemo } from 'react'
import useEChart from '../hooks/useEChart.js'

const UP = '#ef5350'
const DOWN = '#26a69a'

/** 前复权日K蜡烛图 + MA + 成交量（双 grid，联动缩放）。data 为 /api/etfs/{code}/kline 返回值。 */
export default function KlineChart({ data, height = 520 }) {
  const option = useMemo(() => {
    if (!data || !data.dates) return {}
    const dates = data.dates
    const maKeys = Object.keys(data.ma || {})
    const volume = data.volume.map((v, i) => ({
      value: v,
      itemStyle: { color: data.ohlc[i][1] >= data.ohlc[i][0] ? UP : DOWN },
    }))
    const maSeries = maKeys.map((p) => ({
      name: `MA${p}`,
      type: 'line',
      data: data.ma[p],
      smooth: true,
      symbol: 'none',
      lineStyle: { width: 1 },
      emphasis: { disabled: true },
    }))
    return {
      animation: false,
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' },
        valueFormatter: (v) => (v == null ? '-' : Number(v).toFixed(3)),
      },
      legend: { data: ['K线', ...maKeys], top: 4, itemWidth: 14, itemHeight: 8 },
      axisPointer: { link: [{ xAxisIndex: 'all' }] },
      grid: [
        { left: 56, right: 16, top: 34, height: '56%' },
        { left: 56, right: 16, top: '74%', height: '14%' },
      ],
      xAxis: [
        { type: 'category', data: dates, gridIndex: 0, axisLine: { lineStyle: { color: '#d0d0d0' } } },
        { type: 'category', data: dates, gridIndex: 1, axisLabel: { show: false }, axisLine: { lineStyle: { color: '#d0d0d0' } } },
      ],
      yAxis: [
        { scale: true, gridIndex: 0, splitLine: { lineStyle: { color: '#f0f0f0' } } },
        { scale: true, gridIndex: 1, axisLabel: { show: false }, splitLine: { show: false } },
      ],
      dataZoom: [
        { type: 'inside', xAxisIndex: [0, 1], start: 50, end: 100 },
        { type: 'slider', xAxisIndex: [0, 1], bottom: 0, height: 18 },
      ],
      series: [
        {
          name: 'K线',
          type: 'candlestick',
          data: data.ohlc,
          itemStyle: { color: UP, color0: DOWN, borderColor: UP, borderColor0: DOWN },
        },
        ...maSeries,
        {
          name: '成交量',
          type: 'bar',
          data: volume,
          xAxisIndex: 1,
          yAxisIndex: 1,
        },
      ],
    }
  }, [data])
  const ref = useEChart(option)
  return <div ref={ref} style={{ width: '100%', height }} />
}
