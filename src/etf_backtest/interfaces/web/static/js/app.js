// 工具函数

function showLoading() {
    // 显示加载状态
}

function hideLoading() {
    // 隐藏加载状态
}

function formatNumber(num, decimals = 2) {
    if (num === null || num === undefined) return '-';
    return num.toLocaleString('zh-CN', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
}

function formatPercent(num, decimals = 2) {
    if (num === null || num === undefined) return '-';
    return (num * 100).toFixed(decimals) + '%';
}

function formatMoney(num) {
    if (num === null || num === undefined) return '-';
    if (Math.abs(num) >= 1e8) {
        return (num / 1e8).toFixed(2) + '亿';
    } else if (Math.abs(num) >= 1e4) {
        return (num / 1e4).toFixed(2) + '万';
    }
    return num.toLocaleString('zh-CN');
}

// API 请求封装
async function apiGet(url) {
    const response = await fetch(url);
    return response.json();
}

async function apiPost(url, data) {
    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return response.json();
}

// ECharts 主题
const chartTheme = {
    color: ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1', '#13c2c2'],
    backgroundColor: 'transparent',
    textStyle: {
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial'
    }
};
