# AI Panel Studio - 智能多 Agent 圆桌演播厅 (Web App MVP)

> 基于大模型（Deepseek V4 Pro）驱动的多智能体自主调度演播厅。

## 📖 项目简介
"AI Panel Studio" 是一款沉浸式的“AI 圆桌讨论”Web 应用。
用户只需输入任意讨论话题并指定参会专家人数，系统即可动态生成一届主持人和专家阵容。在演播厅模式下，各路专家（Agent）将围绕话题进行自主举手、抢答、补充与反驳，最终呈现一场沉浸式的 AI 深度讨论实况。

本项目不仅仅是一个大模型对话包装壳，而是深入底层实现了一套 **多智能体非线性调度引擎（Multi-Agent Scheduler）**，通过实时计算立场相关度、发言冷却值和 NLP 定向点名识别，让 AI 的交锋更接近真实人类圆桌派。

## 🎯 核心能力与技术亮点

* **动态阵容生成**：根据话题动态生成具备不同立场的专家角色（包括姓名、Title、核心立场）。
* **非线性讨论调度引擎**：摒弃机械式轮流发言，基于 `(关键词重合度 * 0.4) + (反驳偏好 * 0.35) + (点名强制加权) - (发言冷却惩罚)` 算法动态抢麦。
* **实时状态与流式响应**：基于 SSE (Server-Sent Events) 的流式传输，前端可实时感知每位专家的思考（Public Thought）、待机、发言状态，呈现打字机效果。
* **实时共识与分歧提取**：在辩论过程中，后台静默提炼当前讨论的共识与分歧点，实时更新到控制台。
* **沉浸式 UI/UX 设计**：采用现代暗黑系 UI 设计，各区域独立滚动，状态响应灵敏。

## 🛠 技术架构与开发范式

### 技术栈
* **前端**：React 18 + Vite + TypeScript + TailwindCSS / Custom CSS
* **后端**：Python + FastAPI + aiosqlite (原生轻量 SQLite 访问)
* **大模型**：Deepseek V4 Pro
* **通信协议**：RESTful API + Server-Sent Events (SSE)

### 开发范式：SDD -> DDD -> TDD
本项目全程在 Claude Code + Deepseek V4 Pro 的加持下，严格遵循了现代 AI 软件工程化标准：
1. **SDD (Spec-Driven Development)**：在写第一行代码前，完成详尽的数据库表设计（ER）与 API 契约设计。
2. **DDD (Design-Driven Development)**：基于真实交互流设计 UI，确保视觉与状态机的双向解耦。
3. **TDD (Test-Driven Development)**：核心业务（如 Scheduler 算分引擎）通过测试用例驱动开发，确保重构过程的安全闭环。

## 🚀 快速启动指南

### 1. 环境变量配置
请在项目根目录下创建一个 `.env` 文件，填入以下参数（**切勿将 API Key 提交到代码仓库**）：

```env
# 大模型 API 配置
DEEPSEEK_API_KEY=your_deepseek_v4_pro_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v4

# 数据库配置
DB_FILE_PATH=./database/ai_panel.db

# 服务端配置
PORT=3000
```

### 2. 一键启动
本项目提供了一键双端启动脚本。在 Windows 环境下：
直接双击项目根目录下的 **`start.bat`** 即可。
* 脚本会自动启动 FastAPI 后端（端口 3000）并开启热更新。
* 脚本会自动启动 Vite 前端（端口 5174）。
* 浏览器访问前端地址即可体验。

*(如果是 Mac/Linux 环境，请分别在 frontend 和 backend 目录下执行 `npm run dev` 和 `uvicorn main:app --reload`)*

## 📡 核心 API 契约

| 接口路径 | 方法 | 功能描述 |
| --- | --- | --- |
| `/api/rooms` | POST | 创建一个新的讨论室，输入话题和人数 |
| `/api/rooms` | GET | 获取当前所有的讨论列表 |
| `/api/rooms/{id}/experts` | POST | 调用 LLM 动态生成主持人与专家阵容 |
| `/api/rooms/{id}/stream` | GET | (核心) SSE 接口：实时接收讨论事件流、状态和文本流 |
| `/api/rooms/{id}/start` | POST | 触发讨论引擎正式开始演播 |

*(更多详细接口契约与数据库模型请参见 `docs/` 目录)*

## 🔮 改进与未来演进路线

1. **Agent 记忆优化**：引入轻量级向量库，解决长对局下 LLM 的上下文遗忘问题。
2. **多模态扩展 (TTS)**：未来可接入语音合成接口，为不同性格的专家提供定制化语音播报，进一步提升现场感。
3. **引入强制打断机制**：目前为等待发言完毕后根据算分决定下一位，未来可引入 `WebRTC` 或高频心跳实现人类辩论中的“抢白”与“打断”。

## 📂 核心交付物快速导航

1. **完整项目源码**：`frontend/` 和 `backend/` 文件夹
2. **数据库初始化脚本**：`database/schema.sql`
3. **至少 5 条样例数据**：`database/init_5_mock_data.sql`
4. **开发文档 (含 ER 图)**：`docs/PRD.md`、`docs/ER.md`
5. **API 文档**：`docs/API.md`
6. **测试代码**：`tests/` 文件夹
