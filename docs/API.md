# AI Panel Studio - 核心 API 契约文档

本项目采用 FastAPI 提供 RESTful API 与 SSE 实时流服务。以下是核心接口定义。

## 1. 房间管理模块

### 1.1 创建讨论室
**请求方式**：`POST /api/rooms`
**功能说明**：初始化一个新的讨论室记录。

**Request Body (application/json)**
```json
{
  "topic": "人工智能是否会完全取代程序员？",
  "expert_count": 4
}
```

**Response (201 Created)**
```json
{
  "id": "e8efa8db-359b-4be7-abda-387fe4e60e8d",
  "topic": "人工智能是否会完全取代程序员？",
  "expert_count": 4,
  "status": "waiting",
  "created_at": "2026-06-26T23:22:00Z"
}
```

### 1.2 获取房间列表
**请求方式**：`GET /api/rooms`
**功能说明**：获取历史创建的讨论室列表，按时间倒序排列。

**Response (200 OK)**
```json
[
  {
    "id": "e8efa8db...",
    "topic": "人工智能是否会完全取代程序员？",
    "status": "finished",
    "created_at": "..."
  }
]
```

## 2. 专家生成与调度模块

### 2.1 动态生成专家阵容
**请求方式**：`POST /api/rooms/{room_id}/experts`
**功能说明**：触发大模型，根据房间的 `topic` 和 `expert_count` 动态生成主持人和专家画像。

**Response (200 OK)**
```json
{
  "host": {
    "id": "uuid",
    "name": "陈静雅",
    "title": "中立主持人",
    "stance": "中立",
    "role": "host"
  },
  "experts": [
    {
      "id": "uuid",
      "name": "李极客",
      "title": "资深全栈开发",
      "stance": "认为 AI 只是辅助工具，不可能取代人类",
      "role": "expert",
      "color": "#3B82F6"
    }
  ]
}
```

### 2.2 启动正式讨论
**请求方式**：`POST /api/rooms/{room_id}/start`
**功能说明**：唤醒后台异步调度引擎，大模型开始依据策略自动进行回合制或抢答制发言。

**Response (200 OK)**
```json
{
  "message": "Discussion started successfully",
  "room_id": "e8efa8db..."
}
```

## 3. SSE 实时通信协议 (核心)

### 3.1 建立实时连接
**请求方式**：`GET /api/rooms/{room_id}/stream`
**功能说明**：建立 Server-Sent Events 持久连接，接收实时状态流。

**Event Types (事件类型)**:

1. `room.status`：房间宏观状态流转
```json
// data
{"room_id": "...", "status": "discussing"}
```

2. `expert.state`：专家级微观状态流转（支持打字机特效的 Public Thought）
```json
// data
{
  "expert_id": "...",
  "name": "李极客",
  "status": "preparing",
  "public_thought": "我必须反驳他关于算力的观点..."
}
```

3. `transcript.line`：实时聊天文本输出
```json
// data
{
  "expert_id": "...",
  "name": "李极客",
  "content": "刚才提到的算力瓶颈根本不成立！",
  "line_type": "argument",
  "sequence_num": 12
}
```

4. `insight.update`：实时提取的共识与分歧更新
```json
// data
{
  "consensus": [{"content": "大家一致认为 AI 极大提高了基础代码的编写效率"}],
  "disagreement": [{"content": "关于 AI 是否具备真正的逻辑推理能力，双方存在本质分歧"}]
}
```
