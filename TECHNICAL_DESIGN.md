# A股ETF量化回测系统技术方案

## 文档信息

| 项目名称 | ETF量化回测系统 |
|---------|----------------|
| 版本 | V1.1 |
| 创建日期 | 2026-03-13 |
| 更新日期 | 2026-03-13 |
| 文档类型 | 技术方案文档 |

---

## 1. 技术选型

### 1.1 整体架构选型

采用 **前后端分离** 架构：

```
┌─────────────────────────────────────────────────────────────────┐
│                         前端 (Frontend)                         │
│                      React + TypeScript                         │
└─────────────────────────────────────────────────────────────────┘
                              │ HTTP/WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         后端 (Backend)                          │
│                       Python + FastAPI                          │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 后端语言选择

选择 **Python 3.11+** 作为后端开发语言。

**选型依据**：

| 维度 | Python | Node.js | Go | Java |
|------|--------|---------|-----|------|
| 量化生态 | ★★★★★ | ★★☆☆☆ | ★★☆☆☆ | ★★☆☆☆ |
| 数据处理 | ★★★★★ | ★★★☆☆ | ★★★★☆ | ★★★☆☆ |
| 开发效率 | ★★★★★ | ★★★★☆ | ★★★☆☆ | ★★★☆☆ |
| 学习成本 | ★★★★★ | ★★★★☆ | ★★★☆☆ | ★★★☆☆ |
| 社区支持 | ★★★★★ | ★★★★☆ | ★★★★☆ | ★★★★☆ |

**核心优势**：
- pandas/numpy：金融数据处理事实标准
- akshare/efinance：免费A股数据接口
- scipy：统计分析优化算法
- 成熟回测框架参考

### 1.3 前端技术选择

选择 **React 18 + TypeScript + Vite** 作为前端技术栈。

**选型依据**：

| 维度 | React | Vue 3 | Svelte | Angular |
|------|-------|-------|--------|---------|
| 生态丰富度 | ★★★★★ | ★★★★☆ | ★★★☆☆ | ★★★★☆ |
| TypeScript支持 | ★★★★★ | ★★★★☆ | ★★★★☆ | ★★★★★ |
| 图表库支持 | ★★★★★ | ★★★★☆ | ★★★☆☆ | ★★★★☆ |
| 学习成本 | ★★★☆☆ | ★★★★☆ | ★★★★★ | ★★☆☆☆ |
| 社区活跃度 | ★★★★★ | ★★★★★ | ★★★☆☆ | ★★★★☆ |

**核心优势**：
- ECharts/AntV：丰富的金融图表支持
- Ant Design：企业级UI组件库
- React Query：数据请求状态管理
- Zustand：轻量级状态管理

### 1.4 技术栈总览

```
┌──────────────────────────────────────────────────────────────────────┐
│                          技术栈全景图                                  │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────── 前端 ───────────────────────┐              │
│  │  框架: React 18 + TypeScript + Vite               │              │
│  │  UI库: Ant Design 5                                │              │
│  │  图表: ECharts / AntV G2                           │              │
│  │  状态: Zustand + React Query                       │              │
│  │  样式: Tailwind CSS                                │              │
│  └────────────────────────────────────────────────────┘              │
│                                                                      │
│  ┌─────────────────────── 后端 ───────────────────────┐              │
│  │  框架: FastAPI + Uvicorn                           │              │
│  │  数据处理: Pandas + NumPy + Scipy                  │              │
│  │  数据获取: efinance + akshare                      │              │
│  │  存储: Parquet + JSON                              │              │
│  │  缓存: Joblib + Redis(可选)                        │              │
│  └────────────────────────────────────────────────────┘              │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### 1.5 核心依赖清单

**后端依赖 (pyproject.toml)**：

```toml
[project]
name = "etf-backtest"
version = "1.0.0"
requires-python = ">=3.11"

dependencies = [
    # Web框架
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "pydantic>=2.5.0",

    # 数据处理
    "pandas>=2.1.0",
    "numpy>=1.26.0",
    "scipy>=1.12.0",

    # 数据获取
    "akshare>=1.12.0",
    "efinance>=0.5.0",
    "aiohttp>=3.9.0",

    # 数据存储
    "pyarrow>=15.0.0",

    # 工具库
    "joblib>=1.3.0",
    "python-dateutil>=2.8.0",
]
```

**前端依赖 (package.json)**：

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.22.0",
    "antd": "^5.15.0",
    "@ant-design/icons": "^5.3.0",
    "echarts": "^5.5.0",
    "echarts-for-react": "^3.0.0",
    "@tanstack/react-query": "^5.24.0",
    "zustand": "^4.5.0",
    "axios": "^1.6.0",
    "dayjs": "^1.11.0"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "vite": "^5.1.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "tailwindcss": "^3.4.0",
    "@vitejs/plugin-react": "^4.2.0"
  }
}
```

---

## 2. 系统架构

### 2.1 整体架构图

```
┌──────────────────────────────────────────────────────────────────────────┐
│                              前端应用                                     │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐            │
│  │  首页      │ │  ETF列表   │ │  策略管理  │ │  回测分析  │            │
│  │  Dashboard │ │  数据管理  │ │  策略配置  │ │  报告展示  │            │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘            │
│                              │                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    状态管理 (Zustand + React Query)              │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              │                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    API客户端 (Axios)                             │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP/REST API
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                              后端服务                                     │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    API层 (FastAPI Routes)                        │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              │                                           │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐            │
│  │ 数据服务   │ │ 回测服务   │ │ 策略服务   │ │ 分析服务   │            │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘            │
│                              │                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    领域层 (回测引擎/策略引擎/分析引擎)            │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              │                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    基础设施层 (数据获取/存储/缓存)                │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────┘
```

### 2.2 项目目录结构

```
etf-backtest/
├── backend/                          # 后端项目
│   ├── pyproject.toml
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py               # 配置管理
│   │   └── logging.py                # 日志配置
│   │
│   └── src/
│       └── etf_backtest/
│           ├── __init__.py
│           ├── domain/               # 领域层
│           │   ├── backtest/         # 回测引擎
│           │   ├── strategy/         # 策略引擎
│           │   └── analysis/         # 分析引擎
│           │
│           ├── application/          # 应用层
│           │   ├── services/
│           │   └── dto/
│           │
│           ├── infrastructure/       # 基础设施层
│           │   ├── data/
│           │   ├── storage/
│           │   └── cache/
│           │
│           └── interfaces/           # 接口层
│               └── api/
│                   ├── main.py
│                   └── routes/
│
├── frontend/                         # 前端项目
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   │
│   ├── public/
│   │
│   └── src/
│       ├── main.tsx                  # 入口文件
│       ├── App.tsx                   # 根组件
│       │
│       ├── api/                      # API客户端
│       │   ├── client.ts
│       │   ├── etfs.ts
│       │   ├── backtest.ts
│       │   └── strategy.ts
│       │
│       ├── components/               # 通用组件
│       │   ├── Layout/
│       │   │   ├── MainLayout.tsx
│       │   │   └── Sidebar.tsx
│       │   ├── Charts/
│       │   │   ├── NavChart.tsx      # 净值曲线图
│       │   │   ├── DrawdownChart.tsx # 回撤曲线图
│       │   │   ├── ReturnHeatmap.tsx # 收益热力图
│       │   │   └── TradeChart.tsx    # K线买卖点图
│       │   └── common/
│       │       ├── MetricCard.tsx    # 指标卡片
│       │       ├── EtfSelector.tsx   # ETF选择器
│       │       └── DateRangePicker.tsx
│       │
│       ├── pages/                    # 页面组件
│       │   ├── Home/
│       │   │   └── index.tsx         # 首页
│       │   ├── Etfs/
│       │   │   ├── index.tsx         # ETF列表
│       │   │   └── Detail.tsx        # ETF详情
│       │   ├── Strategy/
│       │   │   ├── index.tsx         # 策略列表
│       │   │   └── Create.tsx        # 创建策略
│       │   ├── Backtest/
│       │   │   ├── index.tsx         # 回测配置
│       │   │   └── Result.tsx        # 回测结果
│       │   └── Report/
│       │       └── index.tsx         # 报告页面
│       │
│       ├── stores/                   # 状态管理
│       │   ├── useBacktestStore.ts
│       │   └── useEtfStore.ts
│       │
│       ├── hooks/                    # 自定义Hooks
│       │   ├── useBacktest.ts
│       │   └── useKlines.ts
│       │
│       ├── types/                    # 类型定义
│       │   ├── etf.ts
│       │   ├── backtest.ts
│       │   └── strategy.ts
│       │
│       └── styles/                   # 样式文件
│           └── global.css
│
├── data/                             # 数据目录
│   ├── etfs.json
│   └── cache/
│
├── docs/                             # 文档目录
│
└── docker-compose.yml                # Docker编排
```

---

## 3. 前端详细设计

### 3.1 页面规划

| 页面 | 路由 | 功能描述 |
|-----|------|---------|
| 首页 | `/` | 系统概览、快捷入口、最近回测 |
| ETF列表 | `/etfs` | ETF筛选、列表展示、数据更新 |
| ETF详情 | `/etfs/:code` | 单个ETF详情、历史K线图 |
| 策略列表 | `/strategies` | 内置策略列表、参数说明 |
| 创建回测 | `/backtest/create` | 回测配置、策略选择、参数设置 |
| 回测结果 | `/backtest/:id` | 绩效指标、图表展示、交易记录 |
| 报告导出 | `/report/:id` | 完整报告、导出功能 |

### 3.2 页面布局设计

```
┌────────────────────────────────────────────────────────────────────┐
│  Logo    首页  ETF  策略  回测  报告                    用户设置  │
├────────────┬───────────────────────────────────────────────────────┤
│            │                                                       │
│   侧边栏    │                    主内容区                           │
│            │                                                       │
│  ┌──────┐  │  ┌─────────────────────────────────────────────────┐  │
│  │快捷操作│  │  │                                                 │  │
│  ├──────┤  │  │                                                 │  │
│  │最近回测│  │  │                                                 │  │
│  ├──────┤  │  │                                                 │  │
│  │常用ETF│  │  │                                                 │  │
│  └──────┘  │  └─────────────────────────────────────────────────┘  │
│            │                                                       │
└────────────┴───────────────────────────────────────────────────────┘
```

### 3.3 核心页面设计

#### 3.3.1 首页 (Dashboard)

```tsx
// src/pages/Home/index.tsx

import React from 'react';
import { Row, Col, Card, Statistic, Button, List, Tag } from 'antd';
import {
  RiseOutlined,
  FallOutlined,
  StockOutlined,
  CalendarOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { NavChart } from '@/components/Charts/NavChart';
import { useQuery } from '@tanstack/react-query';
import { getRecentBacktests } from '@/api/backtest';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const { data: recentBacktests } = useQuery({
    queryKey: ['recentBacktests'],
    queryFn: getRecentBacktests,
  });

  return (
    <div className="p-6">
      {/* 快捷操作 */}
      <Row gutter={[16, 16]} className="mb-6">
        <Col span={6}>
          <Card
            hoverable
            className="text-center"
            onClick={() => navigate('/backtest/create')}
          >
            <StockOutlined className="text-4xl text-blue-500 mb-2" />
            <div className="text-lg font-medium">新建回测</div>
          </Card>
        </Col>
        <Col span={6}>
          <Card hoverable className="text-center">
            <CalendarOutlined className="text-4xl text-green-500 mb-2" />
            <div className="text-lg font-medium">ETF列表</div>
          </Card>
        </Col>
        <Col span={6}>
          <Card hoverable className="text-center">
            <div className="text-4xl text-purple-500 mb-2">📈</div>
            <div className="text-lg font-medium">策略库</div>
          </Card>
        </Col>
        <Col span={6}>
          <Card hoverable className="text-center">
            <div className="text-4xl text-orange-500 mb-2">📊</div>
            <div className="text-lg font-medium">历史报告</div>
          </Card>
        </Col>
      </Row>

      {/* 统计概览 */}
      <Row gutter={[16, 16]} className="mb-6">
        <Col span={6}>
          <Card>
            <Statistic
              title="ETF数量"
              value={1000}
              suffix="只"
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="回测次数"
              value={128}
              suffix="次"
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="策略数量"
              value={6}
              suffix="个"
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="数据更新"
              value="今日"
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 最近回测 */}
      <Row gutter={[16, 16]}>
        <Col span={16}>
          <Card title="最近回测">
            <List
              dataSource={recentBacktests?.slice(0, 5) || []}
              renderItem={(item) => (
                <List.Item
                  actions={[
                    <Button type="link" onClick={() => navigate(`/backtest/${item.id}`)}>
                      查看
                    </Button>,
                  ]}
                >
                  <List.Item.Meta
                    title={item.name}
                    description={`${item.strategy} | ${item.startDate} ~ ${item.endDate}`}
                  />
                  <Tag color={item.totalReturn >= 0 ? 'green' : 'red'}>
                    {item.totalReturn >= 0 ? <RiseOutlined /> : <FallOutlined />}
                    {(item.totalReturn * 100).toFixed(2)}%
                  </Tag>
                </List.Item>
              )}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card title="快速回测">
            {/* 快速回测表单 */}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Home;
```

#### 3.3.2 回测配置页

```tsx
// src/pages/Backtest/index.tsx

import React, { useState } from 'react';
import {
  Card,
  Form,
  Select,
  DatePicker,
  InputNumber,
  Button,
  Space,
  Divider,
  Collapse,
  Slider,
  message,
} from 'antd';
import { PlayCircleOutlined, SaveOutlined } from '@ant-design/icons';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { createBacktest } from '@/api/backtest';
import { useQuery } from '@tanstack/react-query';
import { getStrategies } from '@/api/strategy';
import { getEtfList } from '@/api/etfs';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;

const BacktestCreate: React.FC = () => {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const [selectedStrategy, setSelectedStrategy] = useState<string>();

  // 获取策略列表
  const { data: strategies } = useQuery({
    queryKey: ['strategies'],
    queryFn: getStrategies,
  });

  // 获取ETF列表
  const { data: etfs } = useQuery({
    queryKey: ['etfs'],
    queryFn: getEtfList,
  });

  // 创建回测
  const createMutation = useMutation({
    mutationFn: createBacktest,
    onSuccess: (data) => {
      message.success('回测任务已创建');
      navigate(`/backtest/${data.backtestId}`);
    },
    onError: () => {
      message.error('创建失败');
    },
  });

  const handleSubmit = async () => {
    const values = await form.validateFields();
    createMutation.mutate({
      ...values,
      startDate: values.dateRange[0].format('YYYY-MM-DD'),
      endDate: values.dateRange[1].format('YYYY-MM-DD'),
    });
  };

  // 当前选中策略的参数定义
  const currentStrategy = strategies?.find((s) => s.name === selectedStrategy);

  return (
    <div className="p-6">
      <Card title="新建回测" className="max-w-4xl mx-auto">
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            initialCapital: 1000000,
            commission: 0.0003,
            slippage: 0.001,
            dateRange: [dayjs().subtract(3, 'year'), dayjs()],
          }}
        >
          {/* 基本信息 */}
          <Form.Item
            name="name"
            label="回测名称"
            rules={[{ required: true, message: '请输入回测名称' }]}
          >
            <input
              type="text"
              className="w-full px-3 py-2 border rounded-md"
              placeholder="例如：双均线策略-沪深300"
            />
          </Form.Item>

          <Form.Item
            name="strategy"
            label="选择策略"
            rules={[{ required: true, message: '请选择策略' }]}
          >
            <Select
              placeholder="请选择策略"
              onChange={setSelectedStrategy}
              options={strategies?.map((s) => ({
                label: `${s.displayName} - ${s.description}`,
                value: s.name,
              }))}
            />
          </Form.Item>

          {/* 策略参数 */}
          {currentStrategy && (
            <Collapse className="mb-4">
              <Collapse.Panel header="策略参数" key="params">
                {currentStrategy.params.map((param) => (
                  <Form.Item
                    key={param.name}
                    name={['params', param.name]}
                    label={param.description}
                    initialValue={param.default}
                  >
                    {param.type === 'number' ? (
                      <Slider
                        min={param.min}
                        max={param.max}
                        marks={{
                          [param.min!]: param.min,
                          [param.max!]: param.max,
                        }}
                      />
                    ) : (
                      <Select
                        options={param.options?.map((o) => ({
                          label: o,
                          value: o,
                        }))}
                      />
                    )}
                  </Form.Item>
                ))}
              </Collapse.Panel>
            </Collapse>
          )}

          <Form.Item
            name="etfs"
            label="选择ETF"
            rules={[{ required: true, message: '请选择至少一个ETF' }]}
          >
            <Select
              mode="multiple"
              placeholder="搜索并选择ETF"
              showSearch
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              options={etfs?.map((e) => ({
                label: `${e.code} - ${e.name}`,
                value: e.code,
              }))}
            />
          </Form.Item>

          <Form.Item
            name="dateRange"
            label="回测区间"
            rules={[{ required: true, message: '请选择回测区间' }]}
          >
            <RangePicker className="w-full" />
          </Form.Item>

          <Divider>高级设置</Divider>

          <div className="grid grid-cols-3 gap-4">
            <Form.Item name="initialCapital" label="初始资金">
              <InputNumber
                className="w-full"
                formatter={(value) => `¥ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                parser={(value) => value!.replace(/\¥\s?|(,*)/g, '') as any}
              />
            </Form.Item>

            <Form.Item name="commission" label="佣金率">
              <InputNumber className="w-full" step={0.0001} min={0} max={0.01} />
            </Form.Item>

            <Form.Item name="slippage" label="滑点率">
              <InputNumber className="w-full" step={0.001} min={0} max={0.01} />
            </Form.Item>
          </div>

          <Form.Item className="mt-6">
            <Space>
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                onClick={handleSubmit}
                loading={createMutation.isPending}
              >
                开始回测
              </Button>
              <Button icon={<SaveOutlined />}>保存配置</Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default BacktestCreate;
```

#### 3.3.3 回测结果页

```tsx
// src/pages/Backtest/Result.tsx

import React from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Table,
  Tabs,
  Tag,
  Space,
  Button,
  Descriptions,
} from 'antd';
import {
  RiseOutlined,
  FallOutlined,
  DownloadOutlined,
  ShareAltOutlined,
} from '@ant-design-icons';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getBacktestResult } from '@/api/backtest';
import { NavChart } from '@/components/Charts/NavChart';
import { DrawdownChart } from '@/components/Charts/DrawdownChart';
import { ReturnHeatmap } from '@/components/Charts/ReturnHeatmap';
import { MetricCard } from '@/components/common/MetricCard';

const BacktestResult: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  const { data: result, isLoading } = useQuery({
    queryKey: ['backtest', id],
    queryFn: () => getBacktestResult(id!),
    enabled: !!id,
  });

  if (isLoading || !result) {
    return <div className="p-6">加载中...</div>;
  }

  const { summary, trades, dailyValues } = result;

  return (
    <div className="p-6">
      {/* 标题栏 */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">{result.name}</h1>
        <Space>
          <Button icon={<DownloadOutlined />}>导出报告</Button>
          <Button icon={<ShareAltOutlined />}>分享</Button>
        </Space>
      </div>

      {/* 核心指标 */}
      <Row gutter={[16, 16]} className="mb-6">
        <Col span={4}>
          <MetricCard
            title="总收益率"
            value={summary.totalReturn}
            format="percent"
            trend={summary.totalReturn >= 0 ? 'up' : 'down'}
          />
        </Col>
        <Col span={4}>
          <MetricCard
            title="年化收益"
            value={summary.annualizedReturn}
            format="percent"
            trend={summary.annualizedReturn >= 0 ? 'up' : 'down'}
          />
        </Col>
        <Col span={4}>
          <MetricCard
            title="最大回撤"
            value={summary.maxDrawdown}
            format="percent"
            trend="down"
          />
        </Col>
        <Col span={4}>
          <MetricCard title="夏普比率" value={summary.sharpeRatio} format="number" />
        </Col>
        <Col span={4}>
          <MetricCard title="胜率" value={summary.winRate} format="percent" />
        </Col>
        <Col span={4}>
          <MetricCard title="交易次数" value={summary.tradeCount} format="number" />
        </Col>
      </Row>

      {/* 图表区域 */}
      <Tabs
        defaultActiveKey="nav"
        items={[
          {
            key: 'nav',
            label: '净值曲线',
            children: (
              <Card>
                <NavChart data={dailyValues} />
              </Card>
            ),
          },
          {
            key: 'drawdown',
            label: '回撤分析',
            children: (
              <Card>
                <DrawdownChart data={dailyValues} />
              </Card>
            ),
          },
          {
            key: 'heatmap',
            label: '月度收益',
            children: (
              <Card>
                <ReturnHeatmap data={dailyValues} />
              </Card>
            ),
          },
        ]}
      />

      {/* 详细指标 */}
      <Row gutter={[16, 16]} className="mt-6">
        <Col span={12}>
          <Card title="收益指标">
            <Descriptions column={2}>
              <Descriptions.Item label="总收益率">
                <Tag color={summary.totalReturn >= 0 ? 'green' : 'red'}>
                  {(summary.totalReturn * 100).toFixed(2)}%
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="年化收益">
                {(summary.annualizedReturn * 100).toFixed(2)}%
              </Descriptions.Item>
              <Descriptions.Item label="累计收益">
                {(summary.cumulativeReturn * 100).toFixed(2)}%
              </Descriptions.Item>
              <Descriptions.Item label="日均收益">
                {(summary.dailyAvgReturn * 100).toFixed(4)}%
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="风险指标">
            <Descriptions column={2}>
              <Descriptions.Item label="最大回撤">
                {(summary.maxDrawdown * 100).toFixed(2)}%
              </Descriptions.Item>
              <Descriptions.Item label="年化波动率">
                {(summary.annualizedVolatility * 100).toFixed(2)}%
              </Descriptions.Item>
              <Descriptions.Item label="夏普比率">
                {summary.sharpeRatio.toFixed(2)}
              </Descriptions.Item>
              <Descriptions.Item label="卡玛比率">
                {summary.calmarRatio.toFixed(2)}
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
      </Row>

      {/* 交易记录 */}
      <Card title="交易记录" className="mt-6">
        <Table
          dataSource={trades}
          rowKey="id"
          columns={[
            {
              title: '日期',
              dataIndex: 'date',
              key: 'date',
              sorter: true,
            },
            {
              title: '代码',
              dataIndex: 'code',
              key: 'code',
            },
            {
              title: '名称',
              dataIndex: 'name',
              key: 'name',
            },
            {
              title: '方向',
              dataIndex: 'direction',
              key: 'direction',
              render: (dir: string) => (
                <Tag color={dir === 'buy' ? 'green' : 'red'}>
                  {dir === 'buy' ? '买入' : '卖出'}
                </Tag>
              ),
            },
            {
              title: '数量',
              dataIndex: 'shares',
              key: 'shares',
              align: 'right',
            },
            {
              title: '价格',
              dataIndex: 'price',
              key: 'price',
              align: 'right',
              render: (v: number) => v.toFixed(3),
            },
            {
              title: '金额',
              dataIndex: 'amount',
              key: 'amount',
              align: 'right',
              render: (v: number) => v.toLocaleString(),
            },
            {
              title: '手续费',
              dataIndex: 'commission',
              key: 'commission',
              align: 'right',
              render: (v: number) => v.toFixed(2),
            },
          ]}
          pagination={{ pageSize: 20 }}
        />
      </Card>
    </div>
  );
};

export default BacktestResult;
```

### 3.4 核心图表组件

#### 3.4.1 净值曲线图

```tsx
// src/components/Charts/NavChart.tsx

import React, { useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import { EChartsOption } from 'echarts';
import dayjs from 'dayjs';

interface NavChartProps {
  data: Array<{
    date: string;
    value: number;
    benchmarkValue?: number;
  }>;
}

export const NavChart: React.FC<NavChartProps> = ({ data }) => {
  const option: EChartsOption = useMemo(() => {
    const dates = data.map((d) => dayjs(d.date).format('YYYY-MM-DD'));
    const values = data.map((d) => d.value / data[0].value);
    const benchmarkValues = data.map((d) =>
      d.benchmarkValue ? d.benchmarkValue / data[0].benchmarkValue : null
    );

    return {
      tooltip: {
        trigger: 'axis',
        formatter: (params: any) => {
          const date = params[0].axisValue;
          let html = `<div class="font-medium">${date}</div>`;
          params.forEach((item: any) => {
            const value = (item.value * 100 - 100).toFixed(2);
            html += `
              <div class="flex justify-between gap-4">
                <span>${item.marker} ${item.seriesName}</span>
                <span class="font-medium">${value}%</span>
              </div>
            `;
          });
          return html;
        },
      },
      legend: {
        data: ['策略净值', '基准净值'],
        bottom: 0,
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '10%',
        containLabel: true,
      },
      xAxis: {
        type: 'category',
        data: dates,
        boundaryGap: false,
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          formatter: (value: number) => `${((value - 1) * 100).toFixed(0)}%`,
        },
      },
      series: [
        {
          name: '策略净值',
          type: 'line',
          data: values,
          smooth: true,
          lineStyle: { width: 2 },
          areaStyle: {
            opacity: 0.1,
          },
        },
        {
          name: '基准净值',
          type: 'line',
          data: benchmarkValues,
          smooth: true,
          lineStyle: { width: 1, type: 'dashed' },
        },
      ],
    };
  }, [data]);

  return (
    <ReactECharts
      option={option}
      style={{ height: 400 }}
      notMerge
      lazyUpdate
    />
  );
};
```

#### 3.4.2 回撤曲线图

```tsx
// src/components/Charts/DrawdownChart.tsx

import React, { useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import { EChartsOption } from 'echarts';
import dayjs from 'dayjs';

interface DrawdownChartProps {
  data: Array<{ date: string; value: number }>;
}

export const DrawdownChart: React.FC<DrawdownChartProps> = ({ data }) => {
  const option: EChartsOption = useMemo(() => {
    const dates = data.map((d) => dayjs(d.date).format('YYYY-MM-DD'));

    // 计算回撤
    let peak = data[0].value;
    const drawdowns = data.map((d) => {
      peak = Math.max(peak, d.value);
      return (peak - d.value) / peak;
    });

    return {
      tooltip: {
        trigger: 'axis',
        formatter: (params: any) => {
          const date = params[0].axisValue;
          const drawdown = (params[0].value * 100).toFixed(2);
          return `
            <div class="font-medium">${date}</div>
            <div>回撤: ${drawdown}%</div>
          `;
        },
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true,
      },
      xAxis: {
        type: 'category',
        data: dates,
        boundaryGap: false,
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          formatter: (value: number) => `${(value * 100).toFixed(0)}%`,
        },
        max: 0,
      },
      series: [
        {
          type: 'line',
          data: drawdowns.map((d) => -d),
          lineStyle: { width: 1 },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(255, 77, 79, 0.3)' },
                { offset: 1, color: 'rgba(255, 77, 79, 0.05)' },
              ],
            },
          },
        },
      ],
    };
  }, [data]);

  return (
    <ReactECharts
      option={option}
      style={{ height: 300 }}
      notMerge
      lazyUpdate
    />
  );
};
```

### 3.5 API客户端设计

```tsx
// src/api/client.ts

import axios from 'axios';

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  timeout: 30000,
});

// 响应拦截器
client.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.detail || '请求失败';
    return Promise.reject(new Error(message));
  }
);

export default client;
```

```tsx
// src/api/backtest.ts

import client from './client';

export interface BacktestCreateRequest {
  name: string;
  strategy: string;
  params: Record<string, any>;
  etfs: string[];
  startDate: string;
  endDate: string;
  initialCapital: number;
  commission: number;
  slippage: number;
  benchmark?: string;
}

export interface BacktestResult {
  id: string;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  summary: {
    totalReturn: number;
    annualizedReturn: number;
    maxDrawdown: number;
    sharpeRatio: number;
    winRate: number;
    tradeCount: number;
  };
  dailyValues: Array<{
    date: string;
    value: number;
    benchmarkValue?: number;
  }>;
  trades: Array<{
    id: string;
    date: string;
    code: string;
    name: string;
    direction: 'buy' | 'sell';
    shares: number;
    price: number;
    amount: number;
    commission: number;
  }>;
}

export const createBacktest = async (
  data: BacktestCreateRequest
): Promise<{ backtestId: string; status: string }> => {
  return client.post('/backtest', data);
};

export const getBacktestStatus = async (
  id: string
): Promise<{ status: string; progress: number }> => {
  return client.get(`/backtest/${id}`);
};

export const getBacktestResult = async (id: string): Promise<BacktestResult> => {
  return client.get(`/backtest/${id}/result`);
};

export const getRecentBacktests = async (): Promise<BacktestResult[]> => {
  return client.get('/backtest', { params: { limit: 10 } });
};
```

### 3.6 状态管理设计

```tsx
// src/stores/useBacktestStore.ts

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface BacktestConfig {
  strategy: string;
  params: Record<string, any>;
  etfs: string[];
  startDate: string;
  endDate: string;
  initialCapital: number;
  commission: number;
  slippage: number;
}

interface BacktestStore {
  // 当前配置
  currentConfig: BacktestConfig | null;

  // 历史配置
  configHistory: BacktestConfig[];

  // 操作
  setCurrentConfig: (config: BacktestConfig) => void;
  saveToHistory: (config: BacktestConfig) => void;
  clearHistory: () => void;
}

export const useBacktestStore = create<BacktestStore>()(
  persist(
    (set) => ({
      currentConfig: null,
      configHistory: [],

      setCurrentConfig: (config) => set({ currentConfig: config }),

      saveToHistory: (config) =>
        set((state) => ({
          configHistory: [config, ...state.configHistory].slice(0, 20),
        })),

      clearHistory: () => set({ configHistory: [] }),
    }),
    {
      name: 'backtest-storage',
    }
  )
);
```

---

## 4. 后端详细设计

### 4.1 数据层设计

```python
# src/etf_backtest/infrastructure/data/provider.py

from abc import ABC, abstractmethod
from datetime import date
import pandas as pd


class DataProvider(ABC):
    """数据提供者抽象基类"""

    @abstractmethod
    async def get_etf_list(self) -> pd.DataFrame:
        """获取ETF列表"""
        pass

    @abstractmethod
    async def get_klines(
        self,
        code: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> pd.DataFrame:
        """获取K线数据"""
        pass

    @abstractmethod
    async def get_realtime_quote(self, codes: list[str]) -> pd.DataFrame:
        """获取实时行情"""
        pass
```

### 4.2 回测引擎核心

```python
# src/etf_backtest/domain/backtest/engine.py

from dataclasses import dataclass, field
from datetime import date
import pandas as pd
import numpy as np

from .types import BacktestConfig, Order, Position, Trade, DailyValue
from .matcher import OrderMatcher
from .portfolio import Portfolio
from .cost import CostModel
from ..strategy.base import Strategy
from ..strategy.context import StrategyContext


class BacktestResult:
    """回测结果"""

    def __init__(self):
        self.daily_values: list[DailyValue] = []
        self.trades: list[Trade] = []
        self.orders: list[Order] = []


class BacktestEngine:
    """回测引擎"""

    def __init__(self, config: BacktestConfig, data_provider):
        self.config = config
        self.data_provider = data_provider
        self.matcher = OrderMatcher(config)
        self.portfolio = Portfolio(config.initial_capital)
        self.cost_model = CostModel(
            commission_rate=config.commission_rate,
            min_commission=config.min_commission,
            stamp_duty_rate=config.stamp_duty_rate,
            slippage_rate=config.slippage_rate,
        )
        self.result = BacktestResult()
        self._kline_data: dict[str, pd.DataFrame] = {}
        self._trading_dates: list[date] = []

    async def load_data(self, codes: list[str]) -> None:
        """加载K线数据"""
        for code in codes:
            df = await self.data_provider.get_klines(
                code, self.config.start_date, self.config.end_date
            )
            self._kline_data[code] = df

        if codes:
            df = list(self._kline_data.values())[0]
            self._trading_dates = df.index.get_level_values('date').unique().to_list()

    def run(self, strategy: Strategy) -> BacktestResult:
        """执行回测"""
        codes = strategy.get_target_codes()
        context = StrategyContext(
            engine=self,
            portfolio=self.portfolio,
            kline_data=self._kline_data,
        )

        strategy.init(context)

        for trade_date in self._trading_dates:
            self._update_positions_price(trade_date)
            bars = self._get_bars(trade_date, codes)
            strategy.on_bar(context, bars)
            self._process_orders(trade_date)
            self._record_daily_value(trade_date)

        strategy.on_end(context)
        return self.result

    # ... 其他方法
```

### 4.3 API路由设计

```python
# src/etf_backtest/interfaces/api/routes/backtest.py

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from datetime import date
import uuid

router = APIRouter()


class BacktestRequest(BaseModel):
    name: str
    strategy: str
    params: dict = {}
    etfs: list[str]
    start_date: date
    end_date: date
    initial_capital: float = 1000000.0
    commission: float = 0.0003
    slippage: float = 0.001
    benchmark: str = "000300"


class BacktestResponse(BaseModel):
    backtest_id: str
    status: str


tasks = {}


@router.post("/", response_model=BacktestResponse)
async def create_backtest(request: BacktestRequest, background_tasks: BackgroundTasks):
    backtest_id = f"bt_{uuid.uuid4().hex[:8]}"
    tasks[backtest_id] = {"status": "pending", "progress": 0, "result": None}
    background_tasks.add_task(run_backtest, backtest_id, request)
    return BacktestResponse(backtest_id=backtest_id, status="pending")


@router.get("/{backtest_id}")
async def get_backtest_status(backtest_id: str):
    if backtest_id not in tasks:
        raise HTTPException(status_code=404, detail="Backtest not found")
    return tasks[backtest_id]


@router.get("/{backtest_id}/result")
async def get_backtest_result(backtest_id: str):
    if backtest_id not in tasks:
        raise HTTPException(status_code=404, detail="Backtest not found")
    task = tasks[backtest_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Backtest not completed")
    return task["result"]
```

---

## 5. 部署方案

### 5.1 开发环境

```bash
# 后端
cd backend
poetry install
poetry run uvicorn etf_backtest.interfaces.api.main:app --reload --port 8000

# 前端
cd frontend
pnpm install
pnpm dev
```

### 5.2 Docker部署

```yaml
# docker-compose.yml

version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - PYTHONUNBUFFERED=1

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    environment:
      - VITE_API_URL=http://backend:8000/api
```

### 5.3 生产部署

```nginx
# nginx.conf

server {
    listen 80;
    server_name example.com;

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
}
```

---

## 6. 开发里程碑

| 阶段 | 时间 | 后端任务 | 前端任务 |
|-----|------|---------|---------|
| Phase 1 | Week 1-2 | 数据层、API框架 | 项目搭建、布局组件 |
| Phase 2 | Week 3-4 | 回测引擎核心 | 回测配置页、ETF列表页 |
| Phase 3 | Week 5-6 | 策略引擎、分析引擎 | 结果展示页、图表组件 |
| Phase 4 | Week 7-8 | 优化、文档 | 报告导出、部署上线 |

---

## 7. 附录

### 7.1 API接口清单

| 接口 | 方法 | 描述 |
|-----|------|------|
| `/api/etfs` | GET | 获取ETF列表 |
| `/api/etfs/{code}` | GET | 获取ETF详情 |
| `/api/etfs/{code}/klines` | GET | 获取K线数据 |
| `/api/strategies` | GET | 获取策略列表 |
| `/api/backtest` | POST | 创建回测任务 |
| `/api/backtest/{id}` | GET | 查询回测状态 |
| `/api/backtest/{id}/result` | GET | 获取回测结果 |
| `/api/backtest/{id}/report` | GET | 获取HTML报告 |

### 7.2 前端路由清单

| 路由 | 页面 | 描述 |
|-----|------|------|
| `/` | Home | 首页Dashboard |
| `/etfs` | EtfList | ETF列表页 |
| `/etfs/:code` | EtfDetail | ETF详情页 |
| `/strategies` | StrategyList | 策略列表页 |
| `/backtest/create` | BacktestCreate | 创建回测页 |
| `/backtest/:id` | BacktestResult | 回测结果页 |
| `/report/:id` | Report | 报告页面 |
