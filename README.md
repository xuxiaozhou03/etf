# etf

这是一个最小的 Node.js + TypeScript 项目模板（示例）。

快速开始：

```bash
# 在项目根目录下
npm install

# 开发模式（自动重启）
npm run dev

# 构建到 dist/
npm run build

# 运行构建产物
npm start
```

说明：

- 源码放在 `src/`，后端服务器入口为 `src/server.ts`（Koa）。
- 编译产物放在 `dist/`

运行：

```bash
# 使用开发模式（会使用 ts-node-dev 监测并重启）
PORT=3001 npm run dev

# 或者构建后运行生产代码
npm run build
PORT=3001 npm start
```

下一步建议：

- 添加 ESLint + Prettier
- 添加单元测试（Jest / Vitest）
- 添加 CI（GitHub Actions）
