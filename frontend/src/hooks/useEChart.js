import { useEffect, useRef } from 'react'
import * as echarts from 'echarts'

/**
 * ECharts 生命周期 hook：init 一次、随 option 更新、ResizeObserver 自适应、卸载 dispose。
 * 返回一个 ref，挂在容器 div 上即可。
 */
export default function useEChart(option) {
  const ref = useRef(null)
  const chartRef = useRef(null)
  const lastOption = useRef(null)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    const chart = echarts.init(el)
    chartRef.current = chart
    const ro = new ResizeObserver(() => chart.resize())
    ro.observe(el)
    return () => {
      ro.disconnect()
      chart.dispose()
      chartRef.current = null
      lastOption.current = null
    }
  }, [])

  // 仅在 option 引用变化时全量更新；避免无关重渲染重置用户的缩放/图例状态
  useEffect(() => {
    if (chartRef.current && lastOption.current !== option) {
      chartRef.current.setOption(option, true)
      lastOption.current = option
    }
  })

  return ref
}
