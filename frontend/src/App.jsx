import { BrowserRouter, Routes, Route, NavLink, Navigate } from 'react-router-dom'
import EtfListPage from './pages/EtfListPage.jsx'
import EtfDetailPage from './pages/EtfDetailPage.jsx'
import BacktestPage from './pages/BacktestPage.jsx'
import GridPage from './pages/GridPage.jsx'
import DataPage from './pages/DataPage.jsx'

export default function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <header className="topbar">
          <div className="brand">ETF 量化回测</div>
          <nav className="nav">
            <NavLink to="/etfs" end>行情</NavLink>
            <NavLink to="/backtest">回测</NavLink>
            <NavLink to="/grid">网格</NavLink>
            <NavLink to="/data">数据</NavLink>
          </nav>
        </header>
        <main className="content">
          <Routes>
            <Route path="/" element={<Navigate to="/etfs" replace />} />
            <Route path="/etfs" element={<EtfListPage />} />
            <Route path="/etfs/:code" element={<EtfDetailPage />} />
            <Route path="/backtest" element={<BacktestPage />} />
            <Route path="/grid" element={<GridPage />} />
            <Route path="/data" element={<DataPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
