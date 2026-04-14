# 肝功能报告分析系统 - 前端

基于 React 18 + Vite + Tailwind CSS 构建的肝功能报告智能分析前端应用。

## 技术栈

- **框架**: React 18 + Vite 5
- **样式**: Tailwind CSS 3
- **路由**: React Router v6
- **图表**: Recharts 2
- **HTTP**: Axios
- **状态管理**: Context API

## 快速开始

```bash
# 安装依赖
npm install

# 启动开发服务器 (端口 3000)
npm run dev

# 生产构建
npm run build

# 预览生产构建
npm run preview
```

## 目录结构

```
src/
├── constants/      # 常量定义 (指标信息、风险等级)
├── context/        # 全局状态管理
├── hooks/          # 自定义 React Hooks
├── services/       # API 服务层
├── utils/          # 工具函数
├── components/     # 可复用组件
│   ├── common/     # 通用基础组件
│   └── layout/     # 布局组件
└── pages/          # 页面组件
```

## 页面路由

| 路径 | 页面 | 说明 |
|------|------|------|
| `/` | 首页 | 产品介绍与功能概览 |
| `/upload` | 上传报告 | 文件上传与进度展示 |
| `/results/:id` | 分析结果 | 指标详情、风险评分、健康建议 |
| `/dashboard` | 控制台 | 数据概览与趋势图表 |
| `/history` | 历史记录 | 报告列表与筛选 |

## 后端 API

前端通过 Vite proxy 将 `/api` 请求转发至 `http://localhost:5000`。

主要接口：
- `POST /api/reports/upload` - 上传报告文件
- `GET /api/reports/analysis/{id}` - 获取分析结果
- `GET /api/health` - 健康检查
