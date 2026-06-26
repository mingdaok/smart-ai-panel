# AI Panel Studio - AI圆桌讨论 Web App MVP

## 项目简介
"AI Panel Studio" 是一款本地运行的“AI 圆桌讨论”Web 应用。用户只需输入任意讨论话题并指定参会专家人数，系统即可调用大模型动态生成一届主持人和专家阵容。在演播厅模式下，各路专家（Agent）将围绕话题进行自主举手、抢答、补充与反驳，最终呈现一场沉浸式的 AI 深度讨论实况。

## 技术选型说明（请根据实际开发调整）
* **前端框架**：[React / Vue 3] + [Vite] 
* **后端框架**：[Node.js (Express/NestJS) / Python (FastAPI)] 
* **数据库**：SQLite (题目硬性要求)
* **实时通信**：SSE (Server-Sent Events)，用于将大模型的流式输出和专家状态实时推送到前端。
* **大模型**：Deepseek V4 Pro (通过 API 调用)
* **核心范式**：严格遵循 SDD -> DDD -> TDD 的工程化开发范式。

## 环境变量配置
请在项目根目录下创建一个 `.env` 文件，并配置以下参数（**注意：切勿将 API Key 提交到代码仓库**）：

```env
# 大模型 API 配置
DEEPSEEK_API_KEY=your_deepseek_v4_pro_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# 数据库配置
DB_FILE_PATH=./database/ai_panel.db

# 服务端配置
PORT=3000
```

## 运行指南

### 后端启动
```bash
cd backend
npm install # 或 pip install -r requirements.txt
npm run dev # 或 uvicorn main:app --reload
```

### 前端启动
```bash
cd frontend
npm install
npm run dev
```
打开浏览器访问 `http://localhost:5173` 即可体验。

## 主要 API 列表

| 接口路径 | 方法 | 功能描述 |
| --- | --- | --- |
| `/api/rooms` | POST | 创建一个新的讨论室，输入话题和人数 |
| `/api/rooms` | GET | 获取当前所有的讨论列表 |
| `/api/rooms/:id/experts` | POST | 动态生成主持人与专家阵容 |
| `/api/rooms/:id/stream` | GET | (SSE) 连接演播厅，实时接收讨论事件流、状态和文本流 |
| `/api/rooms/:id/start` | POST | 触发讨论正式开始 |

## 已完成能力与后续改进方向

### 已完成能力
* [x] **动态阵容生成**：根据话题动态生成具备不同立场的专家角色。
* [x] **非线性讨论调度**：实现了自主决定发言顺序的调度器，而非机械式轮流。
* [x] **实时状态呈现**：前端可实时感知每位专家的思考、待机、发言状态。
* [x] **沉浸式 UI**：响应式布局，各区域独立滚动，良好的视觉分隔。

### 后续改进方向
* [ ] **引入更复杂的 Agent 记忆机制**：目前基于上下文窗口，长讨论可能存在遗忘，后续可引入向量数据库。
* [ ] **多模态扩展**：结合 TTS（文字转语音）生成专家的真实语音播报。
* [ ] **中断机制优化**：更精准地模拟人类辩论中“强制打断”的场景。
