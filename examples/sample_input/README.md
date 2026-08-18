# Aurora Dev Console

> 面向本地 AI Coding 的统一桌面控制台。

## 核心问题
- CLI 工具分散，项目和会话难统一管理
- 环境配置与依赖安装对新用户不友好
- Runtime 输出、任务进度和错误诊断缺少统一可视反馈

## 特性
- 项目与工作区管理
- Chat / Terminal 双视图
- 环境检测与安装引导
- Runtime 任务控制与进度事件
- SQLite 本地状态持久化
- GitHub 仓库浏览

## 技术栈
- Tauri v2 + Rust + Tokio
- React 18 + TypeScript + Vite + Zustand
- xterm.js
- SQLite / rusqlite
- Vitest + Cargo Check + GitHub Actions
