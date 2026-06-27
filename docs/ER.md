# AI Panel Studio - 数据库实体关系图 (ER Diagram)

本项目采用轻量级的 SQLite 作为核心数据存储，整体架构围绕“演播厅 (Room)”进行多表关联。

## Mermaid ER 图

```mermaid
erDiagram
    Room ||--o{ Expert : "has many (1:N)"
    Room ||--o{ TranscriptLine : "has many (1:N)"
    Room ||--o{ Insight : "has many (1:N)"
    Expert ||--o{ TranscriptLine : "speaks (1:N)"

    Room {
        string id PK "UUID"
        string topic "讨论话题"
        int expert_count "期望的专家人数"
        string status "状态: waiting/generating/ready/discussing/finished/stopped"
        datetime created_at
        datetime updated_at
    }

    Expert {
        string id PK "UUID"
        string room_id FK "关联房间"
        string name "专家姓名 (大模型生成)"
        string title "专家头衔/职业"
        string stance "核心立场/偏见"
        string color "UI专属配色 (Hex)"
        string role "角色: host/expert"
        int position "UI排列顺序"
        string current_status "当前状态: idle/preparing/speaking"
        string public_thought "公开思考过程 (打字机效果呈现)"
        datetime created_at
    }

    TranscriptLine {
        string id PK "UUID"
        string room_id FK "关联房间"
        string expert_id FK "关联发言人"
        string name "发言人姓名冗余"
        string color "配色冗余"
        string content "发言具体内容"
        string line_type "类型: opening/question/argument/closing"
        int sequence_num "发言顺序"
        datetime created_at
    }

    Insight {
        string id PK "UUID"
        string room_id FK "关联房间"
        string type "类型: consensus(共识) / disagreement(分歧)"
        string content "洞察内容"
        int version "提取批次版本"
        datetime created_at
        datetime updated_at
    }
```

## 设计说明
1. **反范式设计**：在 `TranscriptLine` 中冗余了 `name` 和 `color` 字段，以极大地提升 SSE 流式推送时的查询性能，避免了高频的多表 Join。
2. **状态流转追踪**：`Expert` 表中的 `current_status` 和 `public_thought` 支撑了前端演播厅的实时生命力表现。
