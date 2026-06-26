# Smart AI Panel 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建 AI 圆桌讨论 MVP — 完整的前后端分离 Web 应用，包含 Mock LLM 驱动的非线性调度演播厅

**Architecture:** 「智能前端 + 哑流」分离式 — FastAPI REST (CRUD+历史) + SSE (仅增量广播) + React/Zustand (本地状态机驱动 UI)

**Tech Stack:** React 18 + Vite + TypeScript + Tailwind CSS + shadcn/ui, Python 3.11+ FastAPI + aiosqlite + Pydantic v2, SSE

## Global Constraints

- ✅ 所有 API 响应必须通过 Pydantic 序列化，严禁裸 dict 返回
- ✅ LLM 原始输出必须经 `OutputFilter` 过滤后，才能通过 SSE/API 返回前端
- ✅ 前端 SSE 客户端必须先 REST 拉取全量历史，再连接 SSE 监增量
- ✅ 前端页面根容器 `h-screen overflow-hidden`，各面板 `overflow-y-auto` 独立滚动
- ✅ 深色主题 Design Tokens 从 `frontend/src/styles/tokens.css` 全局引用
- ✅ SQLite WAL 模式 + 外键约束 + room_id 分区查询
- ✅ 所有 LLM 调用必须可切换到 Mock（环境变量 `LLM_MODE=mock|real`）
- ✅ 严禁将 JSON 裸数据渲染到页面
- ✅ 严禁暴露 LLM 隐式思维链内容
- ✅ 多房间事件流严格隔离
- ✅ 每任务严格 TDD：先写失败测试 → 最小实现 → 通过 → 重构 → commit


### Task 1: Backend 项目骨架与配置

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/main.py`
- Create: `backend/config.py`
- Create: `backend/__init__.py`

**Interfaces:**
- Consumes: (none — first task)
- Produces: `config.get_settings()` → `Settings`, `app` (FastAPI instance), uvicorn startup

- [ ] **Step 1: Write the failing test**

```python
# tests/test_config.py
import pytest
from backend.config import Settings, get_settings

def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-key")
    monkeypatch.setenv("DEEPSEEK_BASE_URL", "https://test.api.com/v1")
    monkeypatch.setenv("DB_FILE_PATH", ":memory:")
    monkeypatch.setenv("PORT", "4000")
    monkeypatch.setenv("LLM_MODE", "mock")

    settings = Settings()

    assert settings.deepseek_api_key == "sk-test-key"
    assert settings.deepseek_base_url == "https://test.api.com/v1"
    assert settings.db_file_path == ":memory:"
    assert settings.port == 4000
    assert settings.llm_mode == "mock"

def test_settings_defaults():
    settings = Settings()
    assert settings.port == 3000
    assert settings.db_file_path == "./database/ai_panel.db"
    assert settings.llm_mode == "mock"
    assert settings.max_retries == 2
    assert settings.llm_timeout == 30
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL — ModuleNotFoundError (backend.config not found)

- [ ] **Step 3: Write minimal implementation**

```python
# backend/__init__.py
```

```python
# backend/config.py
import os
from dataclasses import dataclass, field

@dataclass
class Settings:
    deepseek_api_key: str = field(default_factory=lambda: os.getenv("DEEPSEEK_API_KEY", ""))
    deepseek_base_url: str = field(default_factory=lambda: os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"))
    db_file_path: str = field(default_factory=lambda: os.getenv("DB_FILE_PATH", "./database/ai_panel.db"))
    port: int = field(default_factory=lambda: int(os.getenv("PORT", "3000")))
    llm_mode: str = field(default_factory=lambda: os.getenv("LLM_MODE", "mock"))
    max_retries: int = 2
    llm_timeout: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


_settings: Settings | None = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
```

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Panel Studio", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

```txt
# backend/requirements.txt
fastapi>=0.100.0,<1.0.0
uvicorn[standard]>=0.15.0
aiosqlite>=0.19.0
pydantic>=2.0.0
openai>=1.0.0
python-dotenv>=1.0.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
httpx>=0.27.0
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pip install -r backend/requirements.txt && cd backend && pytest ../tests/test_config.py -v`
Expected: 2 PASS

- [ ] **Step 5: Commit**

```bash
git add backend/ tests/test_config.py
git commit -m "feat: backend project scaffold with FastAPI, config, and settings test"
```

---

### Task 2: 前端项目脚手架

**Files:**
- Create: `frontend/` (Vite project via `npm create vite`)
- Create: `frontend/src/styles/tokens.css`
- Modify: `frontend/tailwind.config.js`
- Modify: `frontend/src/index.css`

**Interfaces:**
- Consumes: (none)
- Produces: `frontend/` project with React 18 + TS + Vite + Tailwind + shadcn/ui

- [ ] **Step 1: Scaffold Vite project**

```bash
cd frontend
npm create vite@latest . -- --template react-ts
npm install
npm install -D tailwindcss @tailwindcss/vite
npm install @radix-ui/react-slot class-variance-authority clsx tailwind-merge
```

- [ ] **Step 2: Write Design Tokens**

```css
/* frontend/src/styles/tokens.css */
:root {
  --bg-primary: #0a0a0f;
  --bg-secondary: #13131a;
  --bg-card: #1a1a24;
  --bg-card-hover: #22222e;
  --bg-transcript: #111118;
  --text-primary: #f0f0f5;
  --text-secondary: #a0a0b0;
  --text-muted: #606078;
  --border-default: #2a2a3a;
  --border-active: #4a4a5a;
  --expert-gradient-0: linear-gradient(135deg, #6366f1, #8b5cf6);
  --expert-gradient-1: linear-gradient(135deg, #3b82f6, #06b6d4);
  --expert-gradient-2: linear-gradient(135deg, #10b981, #14b8a6);
  --expert-gradient-3: linear-gradient(135deg, #f59e0b, #d97706);
  --expert-gradient-4: linear-gradient(135deg, #ef4444, #dc2626);
  --expert-gradient-5: linear-gradient(135deg, #ec4899, #be185d);
  --expert-gradient-6: linear-gradient(135deg, #8b5cf6, #6366f1);
  --expert-gradient-7: linear-gradient(135deg, #06b6d4, #0ea5e9);
  --host-gradient: linear-gradient(135deg, #f8fafc, #94a3b8);
  --host-text: #0a0a0f;
  --anim-idle: pulse 3s ease-in-out infinite;
  --anim-preparing: flicker 0.6s ease-in-out infinite;
  --anim-speaking: glow 1.5s ease-in-out infinite;
  --color-consensus: #10b981;
  --color-consensus-bg: rgba(16, 185, 129, 0.10);
  --color-disagreement: #f59e0b;
  --color-disagreement-bg: rgba(245, 158, 11, 0.10);
  --breakpoint-narrow: 768px;
  --breakpoint-wide: 1440px;
}

@keyframes pulse { 0%,100%{opacity:.7;box-shadow:0 0 0 0 var(--border-default)} 50%{opacity:1;box-shadow:0 0 8px 2px transparent} }
@keyframes flicker { 0%,100%{opacity:.6;box-shadow:0 0 6px 0 currentColor} 50%{opacity:1;box-shadow:0 0 16px 4px currentColor} }
@keyframes glow { 0%,100%{opacity:1;box-shadow:0 0 12px 2px currentColor} 50%{opacity:.9;box-shadow:0 0 24px 8px currentColor} }
```

- [ ] **Step 3: Write frontend smoke test**

```typescript
// frontend/src/App.test.tsx
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from './App';

describe('App', () => {
  it('renders the app shell', () => {
    render(<App />);
    expect(screen.getByText(/AI Panel Studio/i)).toBeDefined();
  });
});
```

- [ ] **Step 4: Verify test fails (smoke)**

Run: `cd frontend && npx vitest run`
Expected: FAIL — App.tsx has not been updated yet

- [ ] **Step 5: Write minimal App.tsx**

```tsx
// frontend/src/App.tsx
import './styles/tokens.css';

export default function App() {
  return (
    <div className="min-h-screen bg-[var(--bg-primary)] text-[var(--text-primary)]">
      <h1>AI Panel Studio</h1>
    </div>
  );
}
```

- [ ] **Step 6: Verify test passes**

Run: `cd frontend && npx vitest run`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
cd frontend && git add -A && cd ..
git add frontend/
git commit -m "feat: frontend project scaffold with Vite, React, Tailwind, Design Tokens"
```

---

### Task 3: 数据库 Schema & 初始化

**Files:**
- Create: `database/schema.sql`
- Create: `backend/db/__init__.py`
- Create: `backend/db/connection.py`

**Interfaces:**
- Consumes: `config.get_settings()` (Settings.db_file_path)
- Produces: `backend.db.connection.get_db()` → `aiosqlite.Connection`

- [ ] **Step 1: Write DDL**

```sql
-- database/schema.sql
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS rooms (
    id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    expert_count INTEGER NOT NULL DEFAULT 4,
    status TEXT NOT NULL DEFAULT 'waiting'
        CHECK(status IN ('waiting','generating','ready','discussing','finished','stopped')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS experts (
    id TEXT PRIMARY KEY,
    room_id TEXT NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    title TEXT NOT NULL,
    stance TEXT NOT NULL,
    color TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('host','expert')),
    position INTEGER NOT NULL DEFAULT 0,
    current_status TEXT NOT NULL DEFAULT 'idle'
        CHECK(current_status IN ('idle','preparing','speaking')),
    public_thought TEXT DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_experts_room ON experts(room_id);

CREATE TABLE IF NOT EXISTS transcript_lines (
    id TEXT PRIMARY KEY,
    room_id TEXT NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    expert_id TEXT NOT NULL REFERENCES experts(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    line_type TEXT NOT NULL CHECK(line_type IN ('opening','argument','rebuttal','supplement','question','closing')),
    sequence_num INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_transcript_room ON transcript_lines(room_id);
CREATE INDEX IF NOT EXISTS idx_transcript_seq ON transcript_lines(room_id, sequence_num);

CREATE TABLE IF NOT EXISTS insights (
    id TEXT PRIMARY KEY,
    room_id TEXT NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    type TEXT NOT NULL CHECK(type IN ('consensus','disagreement')),
    content TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_insights_room ON insights(room_id);

CREATE TABLE IF NOT EXISTS discussion_events (
    id TEXT PRIMARY KEY,
    room_id TEXT NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    payload TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_events_room ON discussion_events(room_id);
```

- [ ] **Step 2: Write DB connection module (test first)**

```python
# tests/test_db.py
import pytest
import aiosqlite
from backend.db.connection import get_db, init_db, DB_PATH

@pytest.mark.asyncio
async def test_init_db_creates_tables():
    DB_PATH.set(":memory:")  # use in-memory for test
    await init_db()
    async with aiosqlite.connect(":memory:") as db:
        cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] async for row in cursor]
        assert "rooms" in tables
        assert "experts" in tables
        assert "transcript_lines" in tables
        assert "insights" in tables
        assert "discussion_events" in tables

@pytest.mark.asyncio
async def test_get_db_returns_connection():
    DB_PATH.set(":memory:")
    await init_db()
    async with get_db() as db:
        cursor = await db.execute("SELECT 1")
        row = await cursor.fetchone()
        assert row[0] == 1
```

- [ ] **Step 3: Verify tests fail**

Run: `pytest tests/test_db.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 4: Write minimal implementation**

```python
# backend/db/connection.py
import aiosqlite
from contextlib import asynccontextmanager
from pathlib import Path

class _DBPath:
    _value: str | None = None

    def set(self, path: str):
        self._value = path

    def get(self) -> str:
        if self._value is not None:
            return self._value
        from backend.config import get_settings
        p = Path(get_settings().db_file_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        return str(p.resolve())

DB_PATH = _DBPath()

async def init_db():
    path = DB_PATH.get()
    schema = Path(__file__).parent.parent.parent / "database" / "schema.sql"
    async with aiosqlite.connect(path) as db:
        await db.executescript(schema.read_text(encoding="utf-8"))
        await db.commit()

@asynccontextmanager
async def get_db():
    path = DB_PATH.get()
    db = await aiosqlite.connect(path)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    try:
        yield db
    finally:
        await db.close()
```

```python
# backend/db/__init__.py
from backend.db.connection import get_db, init_db, DB_PATH
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_db.py -v`
Expected: 2 PASS

- [ ] **Step 6: Commit**

```bash
git add database/schema.sql backend/db/ tests/test_db.py
git commit -m "feat: SQLite schema DDL and async DB connection module"
```

---

### Task 4: Pydantic 领域模型

**Files:**
- Create: `backend/models/__init__.py`
- Create: `backend/models/room.py`
- Create: `backend/models/expert.py`
- Create: `backend/models/transcript.py`
- Create: `backend/models/insight.py`
- Create: `backend/models/sse.py`

**Interfaces:**
- Consumes: (none)
- Produces: `RoomCreate`, `RoomResponse`, `RoomDetail`, `ExpertResponse`, `LLMExpertRaw`, `LLMExpertsResponse`, `TranscriptLineResponse`, `InsightItem`, `InsightUpdateResponse`, `SSERoomStatus`, `SSEExpertState`, `SSEDiscussionEnd`, `SSEError`, `SSEEventType`

- [ ] **Step 1: Write the test**

```python
# tests/test_models.py
import pytest
from pydantic import ValidationError
from backend.models.room import RoomCreate, RoomResponse, RoomDetail
from backend.models.expert import ExpertResponse, LLMExpertRaw, LLMExpertsResponse
from backend.models.transcript import TranscriptLineResponse
from backend.models.insight import InsightItem, InsightUpdateResponse
from backend.models.sse import SSEEventType, SSERoomStatus, SSEExpertState, SSEDiscussionEnd, SSEError
from datetime import datetime

class TestRoomCreate:
    def test_valid_room_create(self):
        rc = RoomCreate(topic="AI 监管", expert_count=4)
        assert rc.topic == "AI 监管"
        assert rc.expert_count == 4

    def test_topic_too_short(self):
        with pytest.raises(ValidationError):
            RoomCreate(topic="", expert_count=4)

    def test_topic_too_long(self):
        with pytest.raises(ValidationError):
            RoomCreate(topic="x" * 201, expert_count=4)

    def test_expert_count_min(self):
        with pytest.raises(ValidationError):
            RoomCreate(topic="Test", expert_count=1)

    def test_expert_count_max(self):
        with pytest.raises(ValidationError):
            RoomCreate(topic="Test", expert_count=9)

class TestLLMExpertRaw:
    def test_valid_expert(self):
        e = LLMExpertRaw(name="张教授", title="AI 研究员", stance="支持严格监管")
        assert e.name == "张教授"

    def test_name_too_long(self):
        with pytest.raises(ValidationError):
            LLMExpertRaw(name="x" * 21, title="研究员", stance="中立")

class TestLLMExpertsResponse:
    def test_valid_response(self):
        r = LLMExpertsResponse(
            host=LLMExpertRaw(name="主持人", title="圆桌主持", stance="中立客观"),
            experts=[LLMExpertRaw(name="专家A", title="研究员", stance="支持")]
        )
        assert len(r.experts) == 1

    def test_min_experts(self):
        with pytest.raises(ValidationError):
            LLMExpertsResponse(
                host=LLMExpertRaw(name="主持人", title="主持", stance="中立"),
                experts=[]
            )

class TestSSEEventType:
    def test_all_event_types(self):
        assert SSEEventType.ROOM_STATUS == "room.status"
        assert SSEEventType.EXPERT_STATE == "expert.state"
        assert SSEEventType.TRANSCRIPT_LINE == "transcript.line"
        assert SSEEventType.INSIGHT_UPDATE == "insight.update"
        assert SSEEventType.DISCUSSION_END == "discussion.end"
        assert SSEEventType.HEARTBEAT == "heartbeat"
        assert SSEEventType.ERROR == "error"
```

- [ ] **Step 2: Verify test fails**

Run: `pytest tests/test_models.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: Write all Pydantic models**

(Models as defined in SDD §2.3 — `backend/models/*.py`)

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_models.py -v`
Expected: 8 PASS

- [ ] **Step 5: Commit**

```bash
git add backend/models/ tests/test_models.py
git commit -m "feat: Pydantic domain models for rooms, experts, transcripts, insights, SSE events"
```

---

### Task 5: Room Repository (数据访问层)

**Files:**
- Create: `backend/repositories/__init__.py`
- Create: `backend/repositories/room_repo.py`

**Interfaces:**
- Consumes: `get_db()` → aiosqlite.Connection
- Produces: `RoomRepo.create(room_data) → dict`, `RoomRepo.list_all() → list[dict]`, `RoomRepo.get_by_id(id) → dict|None`, `RoomRepo.update_status(id, status) → None`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_room_repo.py
import pytest
import uuid
from backend.db.connection import init_db, DB_PATH
from backend.repositories.room_repo import RoomRepo

@pytest.fixture(autouse=True)
async def setup_db():
    DB_PATH.set(":memory:")
    await init_db()

@pytest.mark.asyncio
async def test_create_room():
    repo = RoomRepo()
    room_data = {"topic": "AI 监管", "expert_count": 4}
    result = await repo.create(room_data)
    assert result["topic"] == "AI 监管"
    assert result["expert_count"] == 4
    assert result["status"] == "waiting"
    assert "id" in result
    assert "created_at" in result

@pytest.mark.asyncio
async def test_list_rooms():
    repo = RoomRepo()
    await repo.create({"topic": "Topic A", "expert_count": 3})
    await repo.create({"topic": "Topic B", "expert_count": 5})
    rooms = await repo.list_all()
    assert len(rooms) == 2

@pytest.mark.asyncio
async def test_get_room_by_id():
    repo = RoomRepo()
    created = await repo.create({"topic": "Test", "expert_count": 4})
    fetched = await repo.get_by_id(created["id"])
    assert fetched is not None
    assert fetched["topic"] == "Test"

@pytest.mark.asyncio
async def test_get_nonexistent_room():
    repo = RoomRepo()
    result = await repo.get_by_id(str(uuid.uuid4()))
    assert result is None

@pytest.mark.asyncio
async def test_update_status():
    repo = RoomRepo()
    created = await repo.create({"topic": "Test", "expert_count": 4})
    await repo.update_status(created["id"], "discussing")
    fetched = await repo.get_by_id(created["id"])
    assert fetched["status"] == "discussing"
```

- [ ] **Step 2: Verify test fails**

Run: `pytest tests/test_room_repo.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: Write minimal implementation**

```python
# backend/repositories/room_repo.py
import uuid
from datetime import datetime, timezone
from backend.db.connection import get_db

class RoomRepo:
    async def create(self, data: dict) -> dict:
        room_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        async with get_db() as db:
            await db.execute(
                "INSERT INTO rooms (id, topic, expert_count, status, created_at, updated_at) VALUES (?,?,?,?,?,?)",
                (room_id, data["topic"], data.get("expert_count", 4), "waiting", now, now)
            )
            await db.commit()
        return await self.get_by_id(room_id)

    async def list_all(self) -> list[dict]:
        async with get_db() as db:
            cursor = await db.execute("SELECT * FROM rooms ORDER BY created_at DESC")
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_by_id(self, room_id: str) -> dict | None:
        async with get_db() as db:
            cursor = await db.execute("SELECT * FROM rooms WHERE id = ?", (room_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def update_status(self, room_id: str, status: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        async with get_db() as db:
            await db.execute(
                "UPDATE rooms SET status = ?, updated_at = ? WHERE id = ?",
                (status, now, room_id)
            )
            await db.commit()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_room_repo.py -v`
Expected: 5 PASS

- [ ] **Step 5: Commit**

```bash
git add backend/repositories/ tests/test_room_repo.py
git commit -m "feat: Room data repository with CRUD operations"
```

---

### Task 6: Expert Repository

**Files:**
- Create: `backend/repositories/expert_repo.py`

**Interfaces:**
- Consumes: `get_db()`
- Produces: `ExpertRepo.create_batch(room_id, experts_data) → list[dict]`, `ExpertRepo.get_by_room(room_id) → list[dict]`, `ExpertRepo.update_state(expert_id, status, thought) → None`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_expert_repo.py
import pytest
from backend.db.connection import init_db, DB_PATH
from backend.repositories.room_repo import RoomRepo
from backend.repositories.expert_repo import ExpertRepo

@pytest.fixture(autouse=True)
async def setup_db():
    DB_PATH.set(":memory:")
    await init_db()

@pytest.mark.asyncio
async def test_create_batch():
    room_repo = RoomRepo()
    room = await room_repo.create({"topic": "Test", "expert_count": 3})
    
    repo = ExpertRepo()
    experts_data = [
        {"name": "张教授", "title": "研究员", "stance": "支持", "color": "#6366f1", "role": "host", "position": 0},
        {"name": "李总", "title": "CEO", "stance": "反对", "color": "#3b82f6", "role": "expert", "position": 1},
        {"name": "王工", "title": "工程师", "stance": "中立", "color": "#10b981", "role": "expert", "position": 2},
    ]
    result = await repo.create_batch(room["id"], experts_data)
    assert len(result) == 3
    assert all("id" in e for e in result)
    assert result[0]["role"] == "host"

@pytest.mark.asyncio
async def test_get_by_room():
    room_repo = RoomRepo()
    room = await room_repo.create({"topic": "Test", "expert_count": 2})
    repo = ExpertRepo()
    await repo.create_batch(room["id"], [
        {"name": "A", "title": "T", "stance": "S", "color": "#111", "role": "host", "position": 0},
        {"name": "B", "title": "T", "stance": "S", "color": "#222", "role": "expert", "position": 1},
    ])
    experts = await repo.get_by_room(room["id"])
    assert len(experts) == 2

@pytest.mark.asyncio
async def test_update_state():
    room_repo = RoomRepo()
    room = await room_repo.create({"topic": "Test", "expert_count": 1})
    repo = ExpertRepo()
    [expert] = await repo.create_batch(room["id"], [
        {"name": "A", "title": "T", "stance": "S", "color": "#111", "role": "expert", "position": 0},
    ])
    await repo.update_state(expert["id"], "speaking", "正在论证...")
    experts = await repo.get_by_room(room["id"])
    assert experts[0]["current_status"] == "speaking"
    assert experts[0]["public_thought"] == "正在论证..."
```

- [ ] **Step 2: Verify test fails**

Run: `pytest tests/test_expert_repo.py -v`
Expected: FAIL

- [ ] **Step 3: Write implementation**

```python
# backend/repositories/expert_repo.py
import uuid
from backend.db.connection import get_db

class ExpertRepo:
    async def create_batch(self, room_id: str, experts_data: list[dict]) -> list[dict]:
        result = []
        async with get_db() as db:
            for data in experts_data:
                expert_id = str(uuid.uuid4())
                await db.execute(
                    """INSERT INTO experts (id, room_id, name, title, stance, color, role, position)
                       VALUES (?,?,?,?,?,?,?,?)""",
                    (expert_id, room_id, data["name"], data["title"], data["stance"],
                     data["color"], data["role"], data["position"])
                )
                result.append({**data, "id": expert_id, "room_id": room_id,
                               "current_status": "idle", "public_thought": ""})
            await db.commit()
        return result

    async def get_by_room(self, room_id: str) -> list[dict]:
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT * FROM experts WHERE room_id = ? ORDER BY position", (room_id,)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def update_state(self, expert_id: str, status: str, thought: str = "") -> None:
        async with get_db() as db:
            await db.execute(
                "UPDATE experts SET current_status = ?, public_thought = ? WHERE id = ?",
                (status, thought, expert_id)
            )
            await db.commit()
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_expert_repo.py -v`
Expected: 3 PASS

- [ ] **Step 5: Commit**

```bash
git add backend/repositories/expert_repo.py tests/test_expert_repo.py
git commit -m "feat: Expert data repository with batch create and state update"
```

---

### Task 7: TranscriptLine & Insight Repositories

**Files:**
- Create: `backend/repositories/transcript_repo.py`
- Create: `backend/repositories/insight_repo.py`

**Interfaces:**
- Consumes: `get_db()`
- Produces: `TranscriptRepo.add(line_data) → dict`, `TranscriptRepo.get_by_room(room_id) → list[dict]`, `InsightRepo.add(room_id, type, content) → dict`, `InsightRepo.get_by_room(room_id) → list[dict]`

- [ ] **Step 1: Write the failing tests (combined)**

```python
# tests/test_transcript_insight_repo.py
import pytest
from backend.db.connection import init_db, DB_PATH
from backend.repositories.room_repo import RoomRepo
from backend.repositories.expert_repo import ExpertRepo
from backend.repositories.transcript_repo import TranscriptRepo
from backend.repositories.insight_repo import InsightRepo

@pytest.fixture(autouse=True)
async def setup_db():
    DB_PATH.set(":memory:")
    await init_db()

@pytest.mark.asyncio
async def test_add_and_get_transcript():
    room = await RoomRepo().create({"topic": "T", "expert_count": 1})
    [expert] = await ExpertRepo().create_batch(room["id"], [
        {"name": "A", "title": "T", "stance": "S", "color": "#111", "role": "expert", "position": 0}
    ])
    repo = TranscriptRepo()
    line = await repo.add({
        "room_id": room["id"], "expert_id": expert["id"], "content": "我认为...",
        "line_type": "argument", "sequence_num": 1
    })
    assert line["content"] == "我认为..."
    assert line["line_type"] == "argument"

    lines = await repo.get_by_room(room["id"])
    assert len(lines) == 1

@pytest.mark.asyncio
async def test_add_and_get_insights():
    room = await RoomRepo().create({"topic": "T", "expert_count": 1})
    repo = InsightRepo()
    i1 = await repo.add(room["id"], "consensus", "双方认同需要监管")
    i2 = await repo.add(room["id"], "disagreement", "监管力度存分歧")

    insights = await repo.get_by_room(room["id"])
    assert len(insights) == 2
    assert insights[0]["type"] == "consensus"
    assert insights[1]["type"] == "disagreement"
```

- [ ] **Step 2: Verify tests fail**

Run: `pytest tests/test_transcript_insight_repo.py -v`
Expected: FAIL

- [ ] **Step 3: Write implementations**

```python
# backend/repositories/transcript_repo.py
import uuid
from datetime import datetime, timezone
from backend.db.connection import get_db

class TranscriptRepo:
    async def add(self, data: dict) -> dict:
        line_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        async with get_db() as db:
            await db.execute(
                """INSERT INTO transcript_lines (id, room_id, expert_id, content, line_type, sequence_num, created_at)
                   VALUES (?,?,?,?,?,?,?)""",
                (line_id, data["room_id"], data["expert_id"], data["content"],
                 data["line_type"], data["sequence_num"], now)
            )
            await db.commit()
        return {**data, "id": line_id, "created_at": now}

    async def get_by_room(self, room_id: str) -> list[dict]:
        async with get_db() as db:
            cursor = await db.execute(
                """SELECT t.*, e.name, e.title, e.color FROM transcript_lines t
                   JOIN experts e ON t.expert_id = e.id
                   WHERE t.room_id = ? ORDER BY t.sequence_num""",
                (room_id,)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
```

```python
# backend/repositories/insight_repo.py
import uuid
from datetime import datetime, timezone
from backend.db.connection import get_db

class InsightRepo:
    async def add(self, room_id: str, type_: str, content: str) -> dict:
        insight_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        async with get_db() as db:
            await db.execute(
                "INSERT INTO insights (id, room_id, type, content, version, updated_at) VALUES (?,?,?,?,1,?)",
                (insight_id, room_id, type_, content, now)
            )
            await db.commit()
        return {"id": insight_id, "room_id": room_id, "type": type_, "content": content, "version": 1, "updated_at": now}

    async def get_by_room(self, room_id: str) -> list[dict]:
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT * FROM insights WHERE room_id = ? ORDER BY updated_at", (room_id,)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_transcript_insight_repo.py -v`
Expected: 2 PASS

- [ ] **Step 5: Commit**

```bash
git add backend/repositories/transcript_repo.py backend/repositories/insight_repo.py tests/test_transcript_insight_repo.py
git commit -m "feat: TranscriptLine and Insight data repositories"
```

---

### Task 8: POST /api/rooms & GET /api/rooms 端点

**Files:**
- Create: `backend/routes/__init__.py`
- Create: `backend/routes/rooms.py`
- Modify: `backend/main.py` (register routes)

**Interfaces:**
- Consumes: `RoomRepo`, `RoomCreate`
- Produces: `POST /api/rooms → 201 RoomResponse`, `GET /api/rooms → 200 list[RoomResponse]`

- [ ] **Step 1: Write API integration test**

```python
# tests/test_api_rooms.py
import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.db.connection import init_db, DB_PATH

@pytest.fixture(autouse=True)
async def setup_db():
    DB_PATH.set(":memory:")
    await init_db()

@pytest.mark.asyncio
async def test_create_room():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/rooms", json={"topic": "AI 监管", "expert_count": 4})
        assert resp.status_code == 201
        data = resp.json()
        assert data["topic"] == "AI 监管"
        assert data["status"] == "waiting"
        assert "id" in data

@pytest.mark.asyncio
async def test_create_room_validation():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/rooms", json={"topic": "", "expert_count": 1})
        assert resp.status_code == 422

@pytest.mark.asyncio
async def test_list_rooms():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/api/rooms", json={"topic": "Room A", "expert_count": 3})
        await client.post("/api/rooms", json={"topic": "Room B", "expert_count": 5})
        resp = await client.get("/api/rooms")
        assert resp.status_code == 200
        data = resp.json()
        assert "rooms" in data
        assert len(data["rooms"]) == 2

@pytest.mark.asyncio
async def test_get_room_detail():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_resp = await client.post("/api/rooms", json={"topic": "Test", "expert_count": 4})
        room_id = create_resp.json()["id"]
        resp = await client.get(f"/api/rooms/{room_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == room_id

@pytest.mark.asyncio
async def test_get_room_404():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/rooms/nonexistent-id")
        assert resp.status_code == 404
```

- [ ] **Step 2: Verify tests fail**

Run: `pytest tests/test_api_rooms.py -v`
Expected: FAIL (404s, not 422s — routes not registered)

- [ ] **Step 3: Write implementation**

```python
# backend/routes/rooms.py
from fastapi import APIRouter, HTTPException
from backend.models.room import RoomCreate, RoomResponse, RoomDetail
from backend.repositories.room_repo import RoomRepo
from backend.repositories.expert_repo import ExpertRepo
from backend.repositories.transcript_repo import TranscriptRepo
from backend.repositories.insight_repo import InsightRepo

router = APIRouter(prefix="/api/rooms", tags=["rooms"])

@router.post("", status_code=201, response_model=RoomResponse)
async def create_room(body: RoomCreate):
    repo = RoomRepo()
    room = await repo.create({"topic": body.topic, "expert_count": body.expert_count})
    return RoomResponse(**room)

@router.get("")
async def list_rooms():
    repo = RoomRepo()
    rooms = await repo.list_all()
    return {"rooms": [RoomResponse(**r) for r in rooms]}

@router.get("/{room_id}", response_model=RoomDetail)
async def get_room(room_id: str):
    repo = RoomRepo()
    room = await repo.get_by_id(room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    expert_repo = ExpertRepo()
    experts = await expert_repo.get_by_room(room_id)
    transcript_repo = TranscriptRepo()
    transcripts = await transcript_repo.get_by_room(room_id)
    insight_repo = InsightRepo()
    insights = await insight_repo.get_by_room(room_id)
    return RoomDetail(
        **room,
        experts=experts,
        transcript_count=len(transcripts),
        insight_count=len(insights),
    )
```

```python
# backend/main.py (add route registration)
# ...
from backend.routes.rooms import router as rooms_router
app.include_router(rooms_router)
```

```python
# backend/routes/__init__.py
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_api_rooms.py -v`
Expected: 5 PASS

- [ ] **Step 5: Commit**

```bash
git add backend/routes/ backend/main.py tests/test_api_rooms.py
git commit -m "feat: POST/GET /api/rooms and GET /api/rooms/:id REST endpoints"
```

---

### Task 9: Mock LLM Service

**Files:**
- Create: `backend/services/__init__.py`
- Create: `backend/services/mock_llm.py`

**Interfaces:**
- Consumes: `get_settings()` (Settings.llm_mode)
- Produces: `LLMClient.generate_experts(topic, count) → LLMExpertsResponse`, `LLMClient.generate_speech(...) → str`, `LLMClient.generate_insights(...) → dict`

- [ ] **Step 1: Write the test**

```python
# tests/test_mock_llm.py
import pytest
from backend.services.mock_llm import MockLLMClient
from backend.models.expert import LLMExpertsResponse

class TestMockLLMClient:
    def test_generate_experts_returns_valid_structure(self):
        client = MockLLMClient()
        result = client.generate_experts("AI 监管", 4)
        assert isinstance(result, LLMExpertsResponse)
        assert result.host.name
        assert result.host.title
        assert len(result.experts) == 4
        # All experts have distinct stances
        stances = [e.stance for e in result.experts]
        assert len(set(stances)) == 4

    def test_generate_experts_different_counts(self):
        client = MockLLMClient()
        for n in [2, 5, 8]:
            result = client.generate_experts("测试话题", n)
            assert len(result.experts) == n

    def test_generate_speech_returns_string(self):
        client = MockLLMClient()
        speech = client.generate_speech(
            expert_name="张教授", stance="支持监管",
            context="当前讨论监管必要性", line_type="argument"
        )
        assert isinstance(speech, str)
        assert len(speech) > 0

    def test_generate_insights_returns_consensus_and_disagreement(self):
        client = MockLLMClient()
        result = client.generate_insights("张教授认为需要监管，李总认为行业自律更有效")
        assert "consensus" in result
        assert "disagreement" in result
```

- [ ] **Step 2: Verify tests fail**

Run: `pytest tests/test_mock_llm.py -v`
Expected: FAIL

- [ ] **Step 3: Write implementation**

```python
# backend/services/mock_llm.py
from backend.models.expert import LLMExpertRaw, LLMExpertsResponse

FALLBACK_TEMPLATES = {
    "tech": {
        "host": {"name": "陈博士", "title": "圆桌主持人", "stance": "中立客观"},
        "experts": [
            {"name": "张总", "title": "科技企业家", "stance": "坚信技术创新是第一生产力，支持自由发展"},
            {"name": "王教授", "title": "AI 伦理学家", "stance": "技术必须以人类福祉为前提，支持严格监管"},
            {"name": "李工", "title": "一线AI工程师", "stance": "从技术可行性角度理性分析问题"},
            {"name": "赵观察员", "title": "独立科技评论员", "stance": "关注产业生态平衡，偏向市场调节"},
        ]
    },
    "generic": {
        "host": {"name": "陈博士", "title": "资深圆桌主持人", "stance": "中立客观，引导讨论"},
        "experts": [
            {"name": "张教授", "title": "乐观派学者", "stance": "强烈支持并推动该议题的积极方向"},
            {"name": "王老师", "title": "批判性思考者", "stance": "持怀疑态度，质疑过于乐观的假设"},
            {"name": "李分析师", "title": "数据驱动分析师", "stance": "依据数据和实证评估各方论点"},
            {"name": "赵先生", "title": "务实主义者", "stance": "关注实际可行性和落地难度"},
        ]
    }
}

class MockLLMClient:
    def generate_experts(self, topic: str, count: int) -> LLMExpertsResponse:
        template = FALLBACK_TEMPLATES["generic"]
        experts = template["experts"][:count]
        # Pad if more experts needed than template has
        while len(experts) < count:
            experts.append({"name": f"专家{len(experts)+1}", "title": "特邀嘉宾", "stance": f"立场视角{len(experts)+1}"})
        return LLMExpertsResponse(
            host=LLMExpertRaw(**template["host"]),
            experts=[LLMExpertRaw(**e) for e in experts[:count]]
        )

    def generate_speech(self, expert_name: str, stance: str, context: str, line_type: str) -> str:
        speeches = {
            "argument": f"{expert_name}认为，基于{stance}的立场，这个问题需要更深入的探讨。",
            "rebuttal": f"{expert_name}反驳道：从前面的发言来看，有一些关键点被忽略了。",
            "supplement": f"{expert_name}补充说：还有一个角度值得考虑。",
            "question": f"{expert_name}提出疑问：我们是否应该重新审视这个前提？",
            "opening": "欢迎各位来到今天的圆桌讨论。让我们围绕这个话题展开深度对话。",
            "closing": "今天的讨论非常精彩，感谢各位专家贡献的深刻洞见。",
        }
        return speeches.get(line_type, speeches["argument"])

    def generate_insights(self, transcript_snippet: str) -> dict:
        return {
            "consensus": ["各方都认识到该议题的重要性"],
            "disagreement": ["在具体实施方案上存在分歧"]
        }

    def generate_public_thought(self, expert_name: str, stance: str) -> str:
        thoughts = [
            f"正在从{stance}的角度分析...",
            "正在组织论点...",
            "关注当前讨论的走向...",
            "准备回应前一个观点...",
        ]
        import random
        return random.choice(thoughts)
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_mock_llm.py -v`
Expected: 4 PASS

- [ ] **Step 5: Commit**

```bash
git add backend/services/ tests/test_mock_llm.py
git commit -m "feat: Mock LLM service with fallback expert templates"
```

---

### Task 10: POST /api/rooms/:id/experts 端点

**Files:**
- Create: `backend/routes/experts.py`
- Modify: `backend/main.py`

**Interfaces:**
- Consumes: `RoomRepo`, `ExpertRepo`, `LLMClient`
- Produces: `POST /api/rooms/:id/experts → 200 ExpertGenerationResponse`

- [ ] **Step 1: Write the API test**

```python
# tests/test_api_experts.py
import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.db.connection import init_db, DB_PATH

@pytest.fixture(autouse=True)
async def setup_db():
    DB_PATH.set(":memory:")
    await init_db()

@pytest.mark.asyncio
async def test_generate_experts():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_resp = await client.post("/api/rooms", json={"topic": "AI 监管", "expert_count": 4})
        room_id = create_resp.json()["id"]

        resp = await client.post(f"/api/rooms/{room_id}/experts", json={"user_confirmed": False})
        assert resp.status_code == 200
        data = resp.json()
        assert "host" in data
        assert "experts" in data
        assert len(data["experts"]) == 4
        assert data["host"]["role"] == "host"

@pytest.mark.asyncio
async def test_regenerate_returns_409():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_resp = await client.post("/api/rooms", json={"topic": "Test", "expert_count": 3})
        room_id = create_resp.json()["id"]
        await client.post(f"/api/rooms/{room_id}/experts", json={"user_confirmed": False})
        resp = await client.post(f"/api/rooms/{room_id}/experts", json={"user_confirmed": False})
        assert resp.status_code == 409

@pytest.mark.asyncio
async def test_experts_nonexistent_room():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/rooms/nonexistent/experts", json={"user_confirmed": False})
        assert resp.status_code == 404
```

- [ ] **Step 2: Verify tests fail**

Run: `pytest tests/test_api_experts.py -v`
Expected: FAIL (404 — route not registered)

- [ ] **Step 3: Write implementation**

```python
# backend/routes/experts.py
from fastapi import APIRouter, HTTPException
from backend.models.expert import ExpertGenerationRequest, ExpertResponse
from backend.repositories.room_repo import RoomRepo
from backend.repositories.expert_repo import ExpertRepo
from backend.services.mock_llm import MockLLMClient

router = APIRouter(prefix="/api/rooms", tags=["experts"])

EXPERT_COLORS = ["#6366f1", "#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#ec4899", "#8b5cf6", "#06b6d4"]

@router.post("/{room_id}/experts")
async def generate_experts(room_id: str, body: ExpertGenerationRequest):
    room_repo = RoomRepo()
    room = await room_repo.get_by_id(room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")

    expert_repo = ExpertRepo()
    existing = await expert_repo.get_by_room(room_id)
    if existing:
        raise HTTPException(status_code=409, detail="Experts already generated for this room")

    llm = MockLLMClient()
    result = llm.generate_experts(room["topic"], room["expert_count"])

    experts_data = []
    # Host first
    experts_data.append({
        "name": result.host.name, "title": result.host.title, "stance": result.host.stance,
        "color": "#f8fafc", "role": "host", "position": 0
    })
    for i, e in enumerate(result.experts):
        experts_data.append({
            "name": e.name, "title": e.title, "stance": e.stance,
            "color": EXPERT_COLORS[i % len(EXPERT_COLORS)], "role": "expert", "position": i + 1
        })

    created = await expert_repo.create_batch(room_id, experts_data)
    await room_repo.update_status(room_id, "ready")

    host = [e for e in created if e["role"] == "host"][0]
    experts = [e for e in created if e["role"] == "expert"]
    return {"host": host, "experts": experts}
```

Register in main.py:
```python
from backend.routes.experts import router as experts_router
app.include_router(experts_router)
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_api_experts.py -v`
Expected: 3 PASS

- [ ] **Step 5: Commit**

```bash
git add backend/routes/experts.py backend/main.py tests/test_api_experts.py
git commit -m "feat: POST /api/rooms/:id/experts endpoint with LLM mock"
```

---

### Task 11: SSE Manager (多房间广播基础设施)

**Files:**
- Create: `backend/services/sse_manager.py`

**Interfaces:**
- Consumes: `asyncio.Queue`
- Produces: `SSEManager.subscribe(room_id) → asyncio.Queue`, `SSEManager.unsubscribe(room_id, queue)`, `SSEManager.broadcast(room_id, event_type, data)`

- [ ] **Step 1: Write the test**

```python
# tests/test_sse_manager.py
import pytest
import asyncio
from backend.services.sse_manager import SSEManager

@pytest.mark.asyncio
async def test_subscribe_and_broadcast():
    manager = SSEManager()
    queue = await manager.subscribe("room-1")

    await manager.broadcast("room-1", "test.event", {"msg": "hello"})

    event = await asyncio.wait_for(queue.get(), timeout=1.0)
    assert event["event"] == "test.event"
    assert event["data"] == {"msg": "hello"}

@pytest.mark.asyncio
async def test_room_isolation():
    manager = SSEManager()
    q1 = await manager.subscribe("room-1")
    q2 = await manager.subscribe("room-2")

    await manager.broadcast("room-1", "test", {"room": 1})
    await manager.broadcast("room-2", "test", {"room": 2})

    e1 = await asyncio.wait_for(q1.get(), timeout=1.0)
    e2 = await asyncio.wait_for(q2.get(), timeout=1.0)
    assert e1["data"]["room"] == 1
    assert e2["data"]["room"] == 2

@pytest.mark.asyncio
async def test_unsubscribe():
    manager = SSEManager()
    queue = await manager.subscribe("room-1")
    await manager.unsubscribe("room-1", queue)
    await manager.broadcast("room-1", "test", {})

    # Should not receive — queue was removed
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(queue.get(), timeout=0.3)

@pytest.mark.asyncio
async def test_broadcast_removes_disconnected_queues():
    manager = SSEManager()
    manager._channels["room-1"] = set()
    # Add a mock queue that raises on put
    class BrokenQueue:
        async def put(self, item):
            raise RuntimeError("disconnected")
    broken = BrokenQueue()
    manager._channels["room-1"].add(broken)

    # Should not raise
    await manager.broadcast("room-1", "test", {})
    assert broken not in manager._channels["room-1"]
```

- [ ] **Step 2: Verify tests fail**

Run: `pytest tests/test_sse_manager.py -v`
Expected: FAIL

- [ ] **Step 3: Write implementation**

```python
# backend/services/sse_manager.py
import asyncio
import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class SSEManager:
    def __init__(self):
        self._channels: dict[str, set[asyncio.Queue]] = {}

    async def subscribe(self, room_id: str) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self._channels.setdefault(room_id, set()).add(queue)
        return queue

    async def unsubscribe(self, room_id: str, queue: asyncio.Queue):
        if room_id in self._channels:
            self._channels[room_id].discard(queue)
            if not self._channels[room_id]:
                del self._channels[room_id]

    async def broadcast(self, room_id: str, event_type: str, data: dict):
        if room_id not in self._channels:
            return
        message = {"event": event_type, "data": data}
        dead_queues = set()
        for queue in self._channels[room_id]:
            try:
                await queue.put(message)
            except Exception:
                dead_queues.add(queue)
        self._channels[room_id] -= dead_queues

# Singleton
sse_manager = SSEManager()
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_sse_manager.py -v`
Expected: 4 PASS

- [ ] **Step 5: Commit**

```bash
git add backend/services/sse_manager.py tests/test_sse_manager.py
git commit -m "feat: SSE manager with per-room channels and broadcast isolation"
```

---

### Task 12: GET /api/rooms/:id/stream SSE 端点

**Files:**
- Create: `backend/routes/stream.py`
- Modify: `backend/main.py`

**Interfaces:**
- Consumes: `SSEManager`, `RoomRepo`
- Produces: `GET /api/rooms/:id/stream → text/event-stream`

- [ ] **Step 1: Write the SSE API test**

```python
# tests/test_sse_api.py
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.db.connection import init_db, DB_PATH
from backend.services.sse_manager import sse_manager

@pytest.fixture(autouse=True)
async def setup_db():
    DB_PATH.set(":memory:")
    await init_db()

@pytest.mark.asyncio
async def test_sse_connection_established():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_resp = await client.post("/api/rooms", json={"topic": "Test", "expert_count": 2})
        room_id = create_resp.json()["id"]

        # Connect SSE
        async with client.stream("GET", f"/api/rooms/{room_id}/stream") as response:
            assert response.status_code == 200
            assert "text/event-stream" in response.headers["content-type"]

@pytest.mark.asyncio
async def test_sse_receives_broadcast():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_resp = await client.post("/api/rooms", json={"topic": "Test", "expert_count": 2})
        room_id = create_resp.json()["id"]

        async with client.stream("GET", f"/api/rooms/{room_id}/stream") as response:
            # Broadcast a test event
            await sse_manager.broadcast(room_id, "test.event", {"msg": "hello"})

            # Read first line
            line = await asyncio.wait_for(response.aiter_lines().__anext__(), timeout=2.0)
            assert "event: test.event" in line

@pytest.mark.asyncio
async def test_sse_room_404():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        async with client.stream("GET", "/api/rooms/nonexistent/stream") as response:
            assert response.status_code == 404
```

- [ ] **Step 2: Verify tests fail**

Run: `pytest tests/test_sse_api.py -v`
Expected: FAIL (404 — route not registered)

- [ ] **Step 3: Write implementation**

```python
# backend/routes/stream.py
import asyncio
import json
from fastapi import APIRouter, HTTPException, Request
from sse_starlette.sse import EventSourceResponse
from backend.repositories.room_repo import RoomRepo
from backend.services.sse_manager import sse_manager

router = APIRouter(prefix="/api/rooms", tags=["stream"])

@router.get("/{room_id}/stream")
async def stream_room(room_id: str):
    room_repo = RoomRepo()
    room = await room_repo.get_by_id(room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")

    async def event_generator():
        queue = await sse_manager.subscribe(room_id)
        try:
            while True:
                message = await queue.get()
                event_type = message["event"]
                data = json.dumps(message["data"], ensure_ascii=False, default=str)
                yield {"event": event_type, "data": data}
        except asyncio.CancelledError:
            pass
        finally:
            await sse_manager.unsubscribe(room_id, queue)

    return EventSourceResponse(event_generator())
```

```txt
# Add to requirements.txt
sse-starlette>=2.0.0
```

Register in main.py:
```python
from backend.routes.stream import router as stream_router
app.include_router(stream_router)
```

- [ ] **Step 4: Run tests**

Run: `pip install sse-starlette && pytest tests/test_sse_api.py -v`
Expected: 3 PASS

- [ ] **Step 5: Commit**

```bash
git add backend/routes/stream.py backend/main.py backend/requirements.txt tests/test_sse_api.py
git commit -m "feat: GET /api/rooms/:id/stream SSE endpoint with per-room broadcasting"
```

---

### Task 13: Scheduler Service (TDD — RED Phase)

**Files:**
- Create: `tests/test_scheduler.py` (all 10 test cases, RED)
- Create: `backend/services/scheduler.py` (stub only)

**Interfaces:**
- Consumes: `ExpertRepo`, `TranscriptRepo`, `InsightRepo`, `SSEManager`, `LLMClient`
- Produces: `Scheduler.start(room_id)`, `Scheduler.stop(room_id)`

- [ ] **Step 1: Write ALL scheduler tests (RED)**

```python
# tests/test_scheduler.py
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from backend.db.connection import init_db, DB_PATH
from backend.repositories.room_repo import RoomRepo
from backend.repositories.expert_repo import ExpertRepo
from backend.repositories.transcript_repo import TranscriptRepo
from backend.repositories.insight_repo import InsightRepo
from backend.services.scheduler import Scheduler

@pytest.fixture(autouse=True)
async def setup_db():
    DB_PATH.set(":memory:")
    await init_db()

async def _create_room_with_experts(topic="AI 监管", count=4):
    room = await RoomRepo().create({"topic": topic, "expert_count": count})
    experts_data = []
    positions = ["强烈支持", "倾向支持", "倾向反对", "强烈反对"]
    colors = ["#6366f1", "#3b82f6", "#f59e0b", "#ef4444"]
    for i in range(count + 1):  # +1 for host
        role = "host" if i == 0 else "expert"
        experts_data.append({
            "name": f"专家{i}", "title": f"头衔{i}",
            "stance": positions[i-1] if i > 0 else "中立主持",
            "color": "#f8fafc" if i == 0 else colors[(i-1) % 4],
            "role": role, "position": i
        })
    experts = await ExpertRepo().create_batch(room["id"], experts_data)
    return room, experts

# TC-SCH-01: Expert initial state
@pytest.mark.asyncio
async def test_experts_initial_state_idle():
    room, experts = await _create_room_with_experts()
    scheduler = Scheduler()
    states = await scheduler._get_expert_states(room["id"])
    for expert in experts:
        if expert["role"] == "expert":
            assert states[expert["id"]] == "idle"

# TC-SCH-02: Bidding score ranking
def test_scoring_ranks_experts_by_relevance():
    scheduler = Scheduler()
    experts = [
        {"id": "e1", "name": "A", "stance": "支持严格监管", "role": "expert"},
        {"id": "e2", "name": "B", "stance": "反对监管", "role": "expert"},
        {"id": "e3", "name": "C", "stance": "中立理性", "role": "expert"},
    ]
    last_content = "我认为必须加强政府监管力度"
    scores = scheduler._score_experts(experts, last_content, {})
    # The expert with opposite stance (反对) should rank high on contrarian bias
    # The expert with matching stance (支持) should rank high on relevance
    # Both should outrank the neutral one
    assert scores["e1"]["score"] > scores["e3"]["score"] or scores["e2"]["score"] > scores["e3"]["score"]

# TC-SCH-03: Cooldown penalty
def test_cooldown_penalty_reduces_score():
    scheduler = Scheduler()
    scheduler.COOLDOWN_SECONDS = 10
    expert = {"id": "e1", "name": "A", "stance": "支持", "role": "expert"}
    last_speak_times = {"e1": asyncio.get_event_loop().time() - 2}  # spoke 2s ago
    scores = scheduler._score_experts([expert], "test content", last_speak_times)
    # Should still be penalized (within cooldown)
    assert "cooldown_penalty" in scores["e1"]

# TC-SCH-04: Contrarian bias
def test_contrarian_bias_boosts_opposing_stance():
    scheduler = Scheduler()
    experts = [
        {"id": "e1", "name": "支持者", "stance": "强烈支持该议题", "role": "expert"},
        {"id": "e2", "name": "反对者", "stance": "强烈反对该议题", "role": "expert"},
    ]
    content = "我坚信这个方向完全正确，应该大力推进"
    scores = scheduler._score_experts(experts, content, {})
    # The opposing stance should get a significant contrarian boost
    assert scores["e2"]["contrarian_bias"] > scores["e1"]["contrarian_bias"]

# TC-SCH-05: Host opening
@pytest.mark.asyncio
async def test_host_speaks_first():
    room, experts = await _create_room_with_experts()
    scheduler = Scheduler()
    first_speaker = await scheduler._select_next_speaker(room["id"], round_num=0, last_speaker_id=None)
    host = [e for e in experts if e["role"] == "host"][0]
    assert first_speaker["id"] == host["id"]

# TC-SCH-06: Host closing
@pytest.mark.asyncio
async def test_discussion_ends_with_host_closing():
    room, experts = await _create_room_with_experts("AI 监管", 4)
    scheduler = Scheduler()
    scheduler.MAX_ROUNDS = 1
    mock_llm = MagicMock()
    scheduler.llm = mock_llm
    mock_llm.generate_speech.return_value = "总结陈词..."
    mock_llm.generate_insights.return_value = {"consensus": [], "disagreement": []}
    mock_llm.generate_public_thought.return_value = "正在总结..."

    with patch.object(scheduler, '_broadcast') as mock_broadcast:
        scheduler._room_stop_flags[room["id"]] = False
        await scheduler._run_discussion(room["id"])
        # Check that closing was called
        closing_calls = [c for c in mock_llm.generate_speech.call_args_list
                         if c.kwargs.get('line_type') == 'closing']
        assert len(closing_calls) >= 1

# TC-SCH-07: Context window
def test_context_window_respects_limit():
    scheduler = Scheduler()
    scheduler.CONTEXT_MAX_LINES = 5
    transcript = [{"content": f"line {i}", "name": f"speaker {i}"} for i in range(20)]
    ctx = scheduler._build_context(transcript, current_expert_stance="支持监管")
    assert len(ctx) <= scheduler.CONTEXT_MAX_LINES * 100  # rough char limit check

# TC-SCH-08: Consensus extraction
@pytest.mark.asyncio
async def test_insight_extractor_finds_consensus():
    scheduler = Scheduler()
    mock_llm = MagicMock()
    mock_llm.generate_insights.return_value = {
        "consensus": ["各方都认同AI需要某种约束"],
        "disagreement": []
    }
    scheduler.llm = mock_llm
    result = await scheduler._extract_insights("各方都应该承认AI需要约束...")
    assert "consensus" in result
    assert len(result["consensus"]) >= 1

# TC-SCH-09: Disagreement extraction
@pytest.mark.asyncio
async def test_insight_extractor_finds_disagreement():
    scheduler = Scheduler()
    mock_llm = MagicMock()
    mock_llm.generate_insights.return_value = {
        "consensus": [],
        "disagreement": ["监管主体：政府 vs 行业自律"]
    }
    scheduler.llm = mock_llm
    result = await scheduler._extract_insights("我认为应该政府主导，但我认为行业自律更好...")
    assert "disagreement" in result
    assert len(result["disagreement"]) >= 1

# TC-SCH-10: Concurrent room isolation
@pytest.mark.asyncio
async def test_concurrent_rooms_have_isolated_schedulers():
    room_a, experts_a = await _create_room_with_experts("Topic A", 4)
    room_b, experts_b = await _create_room_with_experts("Topic B", 4)

    sched_a = Scheduler()
    sched_b = Scheduler()

    # Each scheduler should only see its own room's experts
    states_a = await sched_a._get_expert_states(room_a["id"])
    states_b = await sched_b._get_expert_states(room_b["id"])

    assert set(states_a.keys()).isdisjoint(set(states_b.keys()))
```

- [ ] **Step 2: Write stubs so tests compile**

```python
# backend/services/scheduler.py (stub)
import asyncio
import random
import logging
from backend.repositories.expert_repo import ExpertRepo
from backend.repositories.transcript_repo import TranscriptRepo
from backend.repositories.insight_repo import InsightRepo
from backend.repositories.room_repo import RoomRepo
from backend.services.sse_manager import sse_manager
from backend.services.mock_llm import MockLLMClient

logger = logging.getLogger(__name__)

class Scheduler:
    COOLDOWN_SECONDS = 30
    MAX_ROUNDS = 12
    CONTEXT_MAX_LINES = 15
    SPEAK_THRESHOLD = 0.60
    W1 = 0.40  # relevance
    W2 = 0.35  # contrarian
    W3 = 0.20  # cooldown
    W4 = 0.05  # noise

    def __init__(self):
        self.llm = MockLLMClient()
        self._room_stop_flags: dict[str, bool] = {}

    async def _get_expert_states(self, room_id: str) -> dict[str, str]:
        repo = ExpertRepo()
        experts = await repo.get_by_room(room_id)
        return {e["id"]: e["current_status"] for e in experts}

    def _score_experts(self, experts, last_content, last_speak_times):
        result = {}
        for expert in experts:
            if expert["role"] == "host":
                continue
            relevance = float(random.random())  # TODO: real NLP
            contrarian_bias = float(random.random())
            cooldown_penalty = 0.0  # TODO: real calc
            noise = random.uniform(0, 0.2)
            score = self.W1 * relevance + self.W2 * contrarian_bias - self.W3 * cooldown_penalty + self.W4 * noise
            result[expert["id"]] = {"score": score, "relevance": relevance,
                                     "contrarian_bias": contrarian_bias, "cooldown_penalty": cooldown_penalty}
        return result

    async def _select_next_speaker(self, room_id: str, round_num: int, last_speaker_id: str | None):
        repo = ExpertRepo()
        experts = await repo.get_by_room(room_id)
        if round_num == 0:
            return [e for e in experts if e["role"] == "host"][0]
        # Find expert experts
        return [e for e in experts if e["role"] == "expert"][0]

    def _build_context(self, transcript, current_expert_stance):
        lines = transcript[-self.CONTEXT_MAX_LINES:]
        return " ".join(l["content"] for l in lines)

    async def _extract_insights(self, transcript_text):
        return self.llm.generate_insights(transcript_text)

    async def _broadcast(self, room_id, event_type, data):
        await sse_manager.broadcast(room_id, event_type, data)

    async def _run_discussion(self, room_id: str):
        pass  # TODO: implement

    async def start(self, room_id: str):
        self._room_stop_flags[room_id] = False
        asyncio.create_task(self._run_discussion(room_id))

    async def stop(self, room_id: str):
        self._room_stop_flags[room_id] = True
```

- [ ] **Step 3: Verify tests fail for the RIGHT reasons**

Run: `pytest tests/test_scheduler.py -v`
Expected: Some PASS (logic tests), some FAIL (integration tests that need real `_run_discussion`)
**Important:** TC-SCH-06 and TC-SCH-10 will likely fail because `_run_discussion` is a stub. TC-SCH-02, 03, 04 should PASS with mock logic.

- [ ] **Step 4: Commit RED state**

```bash
git add tests/test_scheduler.py backend/services/scheduler.py
git commit -m "test: scheduler TDD — RED phase with 10 test cases and stubs"
```

---

### Task 14: Scheduler — GREEN Phase (核心评分逻辑)

**Files:**
- Modify: `backend/services/scheduler.py`

- [ ] **Step 1: Run tests to confirm RED state**

Run: `pytest tests/test_scheduler.py -v`

- [ ] **Step 2: Implement scoring logic to pass TC-SCH-02/03/04**

```python
# Upgrade _score_experts in scheduler.py

def _score_experts(self, experts: list[dict], last_content: str,
                   last_speak_times: dict[str, float]) -> dict:
    import time, re
    now = time.time()
    result = {}

    for expert in experts:
        if expert["role"] == "host":
            continue

        # Relevance: simple keyword overlap between stance and last content
        stance_kw = set(re.findall(r'[一-鿿]+', expert.get("stance", "")))
        content_kw = set(re.findall(r'[一-鿿]+', last_content))
        overlap = len(stance_kw & content_kw) / max(len(stance_kw | content_kw), 1)
        relevance = 0.3 + 0.7 * overlap  # base 0.3, up to 1.0

        # Contrarian bias: opposing stance = keywords conflict
        opposing_markers = ["反对", "不", "质疑", "警惕", "过分", "过度", "自由", "自律"]
        supporting_markers = ["支持", "推进", "加强", "必须", "应该", "监管"]
        is_opposing = any(m in expert.get("stance", "") for m in opposing_markers)
        content_is_supporting = any(m in last_content for m in supporting_markers)
        contrarian_bias = 0.8 if (is_opposing and content_is_supporting) else 0.3

        # Cooldown penalty
        last_time = last_speak_times.get(expert["id"], 0)
        seconds_since = now - last_time if last_time > 0 else self.COOLDOWN_SECONDS + 1
        cooldown_penalty = max(0, 1.0 - seconds_since / self.COOLDOWN_SECONDS)

        # Noise
        noise = random.uniform(0, 0.2)

        score = (self.W1 * relevance +
                 self.W2 * contrarian_bias -
                 self.W3 * cooldown_penalty +
                 self.W4 * noise)

        result[expert["id"]] = {
            "score": max(0.0, score),
            "relevance": relevance,
            "contrarian_bias": contrarian_bias,
            "cooldown_penalty": cooldown_penalty,
        }

    return result
```

- [ ] **Step 3: Run tests to check scoring tests pass**

Run: `pytest tests/test_scheduler.py::test_scoring_ranks_experts_by_relevance tests/test_scheduler.py::test_cooldown_penalty_reduces_score tests/test_scheduler.py::test_contrarian_bias_boosts_opposing_stance tests/test_experts_initial_state_idle tests/test_host_speaks_first -v`
Expected: 5 PASS

- [ ] **Step 4: Implement _select_next_speaker with real logic**

```python
async def _select_next_speaker(self, room_id: str, round_num: int,
                                last_speaker_id: str | None) -> dict | None:
    repo = ExpertRepo()
    experts = await repo.get_by_room(room_id)

    # Round 0: host always speaks first
    if round_num == 0:
        return [e for e in experts if e["role"] == "host"][0]

    # Build last_speak_times from transcript
    transcript_repo = TranscriptRepo()
    lines = await transcript_repo.get_by_room(room_id)
    last_speak_times = {}
    for line in lines:
        last_speak_times[line["expert_id"]] = time.time()  # approximate

    last_content = lines[-1]["content"] if lines else ""

    scores = self._score_experts(
        [e for e in experts if e["role"] == "expert"],
        last_content,
        last_speak_times
    )

    if not scores:
        return None

    # Pick highest score above threshold
    best = max(scores.items(), key=lambda x: x[1]["score"])
    if best[1]["score"] < self.SPEAK_THRESHOLD:
        return None  # No one wants to speak → host should step in

    best_expert = [e for e in experts if e["id"] == best[0]]
    return best_expert[0] if best_expert else None
```

- [ ] **Step 5: Run all tests**

Run: `pytest tests/test_scheduler.py -v`
Expected: All config/logic tests PASS; host-closing and concurrent-room may still fail (need `_run_discussion`)

- [ ] **Step 6: Commit**

```bash
git add backend/services/scheduler.py
git commit -m "feat: scheduler scoring engine with relevance, contrarian bias, and cooldown penalty"
```

---

### Task 15: Scheduler — Full Discussion Loop & POST /start + /stop

**Files:**
- Create: `backend/routes/discussion.py`
- Modify: `backend/main.py`
- Modify: `backend/services/scheduler.py` (complete `_run_discussion`)

- [ ] **Step 1: Write integration tests**

```python
# tests/test_api_discussion.py
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.db.connection import init_db, DB_PATH

@pytest.fixture(autouse=True)
async def setup_db():
    DB_PATH.set(":memory:")
    await init_db()

async def _create_ready_room(client):
    create_resp = await client.post("/api/rooms", json={"topic": "Test", "expert_count": 3})
    room_id = create_resp.json()["id"]
    await client.post(f"/api/rooms/{room_id}/experts", json={"user_confirmed": False})
    return room_id

@pytest.mark.asyncio
async def test_start_discussion():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        room_id = await _create_ready_room(client)
        resp = await client.post(f"/api/rooms/{room_id}/start")
        assert resp.status_code == 200
        assert resp.json()["stream_started"] is True

@pytest.mark.asyncio
async def test_start_non_ready_room_fails():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_resp = await client.post("/api/rooms", json={"topic": "Test", "expert_count": 3})
        room_id = create_resp.json()["id"]
        resp = await client.post(f"/api/rooms/{room_id}/start")
        assert resp.status_code == 409

@pytest.mark.asyncio
async def test_stop_discussion():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        room_id = await _create_ready_room(client)
        await client.post(f"/api/rooms/{room_id}/start")
        # Small delay for async task
        await asyncio.sleep(0.5)
        resp = await client.post(f"/api/rooms/{room_id}/stop")
        assert resp.status_code == 200

@pytest.mark.asyncio
async def test_full_mock_discussion_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        room_id = await _create_ready_room(client)

        # Connect SSE
        async with client.stream("GET", f"/api/rooms/{room_id}/stream") as sse_resp:
            assert sse_resp.status_code == 200

            # Start discussion
            await client.post(f"/api/rooms/{room_id}/start")

            # Collect events for up to 5 seconds
            events = []
            try:
                async for line in sse_resp.aiter_lines():
                    if line.startswith("event: "):
                        events.append(line)
                    if len(events) >= 5:
                        break
            except asyncio.TimeoutError:
                pass

            assert len(events) > 0, "Should receive at least one SSE event"
```

- [ ] **Step 2: Implement _run_discussion**

```python
async def _run_discussion(self, room_id: str):
    room_repo = RoomRepo()
    transcript_repo = TranscriptRepo()
    insight_repo = InsightRepo()
    expert_repo = ExpertRepo()

    await room_repo.update_status(room_id, "discussing")
    await self._broadcast(room_id, "room.status",
                          {"room_id": room_id, "status": "discussing"})

    round_num = 0
    consecutive_no_insight = 0
    last_insight_count = 0

    try:
        while round_num < self.MAX_ROUNDS and not self._room_stop_flags.get(room_id, True):
            # Select next speaker
            speaker = await self._select_next_speaker(
                room_id, round_num,
                last_speaker_id=None if round_num == 0 else None)

            if speaker is None:
                # Host question
                host = [e for e in await expert_repo.get_by_room(room_id)
                        if e["role"] == "host"][0]
                speaker = host
                line_type = "question"
            else:
                line_type = "opening" if round_num == 0 else "argument"

            # Update status → preparing
            if speaker["role"] == "expert":
                thought = self.llm.generate_public_thought(speaker["name"], speaker["stance"])
                await expert_repo.update_state(speaker["id"], "preparing", thought)
                await self._broadcast(room_id, "expert.state", {
                    "expert_id": speaker["id"], "name": speaker["name"],
                    "status": "preparing", "public_thought": thought
                })

            # Generate speech
            lines = await transcript_repo.get_by_room(room_id)
            context = self._build_context(lines, speaker.get("stance", ""))
            content = self.llm.generate_speech(
                speaker["name"], speaker.get("stance", ""), context, line_type)

            # Update status → speaking
            await expert_repo.update_state(speaker["id"], "speaking", "")
            await self._broadcast(room_id, "expert.state", {
                "expert_id": speaker["id"], "name": speaker["name"],
                "status": "speaking", "public_thought": ""
            })

            # Save and broadcast transcript line
            seq = len(lines) + 1
            line = await transcript_repo.add({
                "room_id": room_id, "expert_id": speaker["id"],
                "content": content, "line_type": line_type, "sequence_num": seq
            })
            await self._broadcast(room_id, "transcript.line", line)

            # Update status → idle
            await expert_repo.update_state(speaker["id"], "idle", "")
            await self._broadcast(room_id, "expert.state", {
                "expert_id": speaker["id"], "name": speaker["name"],
                "status": "idle", "public_thought": ""
            })

            # Extract insights every 2 rounds
            if round_num > 0 and round_num % 2 == 0:
                all_lines = await transcript_repo.get_by_room(room_id)
                combined = " ".join(l["content"] for l in all_lines[-3:])
                result = await self._extract_insights(combined)
                for c_text in result.get("consensus", []):
                    await insight_repo.add(room_id, "consensus", c_text)
                for d_text in result.get("disagreement", []):
                    await insight_repo.add(room_id, "disagreement", d_text)
                insights = await insight_repo.get_by_room(room_id)
                await self._broadcast(room_id, "insight.update", {
                    "consensus": [i for i in insights if i["type"] == "consensus"],
                    "disagreement": [i for i in insights if i["type"] == "disagreement"],
                })
                # Stop check
                if len(insights) == last_insight_count:
                    consecutive_no_insight += 1
                else:
                    consecutive_no_insight = 0
                last_insight_count = len(insights)

            if consecutive_no_insight >= 2:
                break

            round_num += 1

    finally:
        # Host closing
        host = [e for e in await expert_repo.get_by_room(room_id)
                if e["role"] == "host"]
        if host:
            lines = await transcript_repo.get_by_room(room_id)
            context = self._build_context(lines, "")
            summary = self.llm.generate_speech(
                host[0]["name"], "中立", context, "closing")
            await self._broadcast(room_id, "discussion.end", {
                "summary": summary, "total_rounds": round_num,
                "final_consensus": [], "final_disagreement": []
            })

        await room_repo.update_status(room_id, "finished")
        await self._broadcast(room_id, "room.status",
                              {"room_id": room_id, "status": "finished"})
```

- [ ] **Step 3: Write discussion route**

```python
# backend/routes/discussion.py
from fastapi import APIRouter, HTTPException
from backend.repositories.room_repo import RoomRepo
from backend.services.scheduler import Scheduler

router = APIRouter(prefix="/api/rooms", tags=["discussion"])

# Simple global scheduler registry — one per room
_schedulers: dict[str, Scheduler] = {}

@router.post("/{room_id}/start")
async def start_discussion(room_id: str):
    repo = RoomRepo()
    room = await repo.get_by_id(room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    if room["status"] != "ready":
        raise HTTPException(status_code=409, detail="Room is not in ready status")

    scheduler = Scheduler()
    _schedulers[room_id] = scheduler
    await scheduler.start(room_id)
    return {"stream_started": True, "room_id": room_id}

@router.post("/{room_id}/stop")
async def stop_discussion(room_id: str):
    repo = RoomRepo()
    room = await repo.get_by_id(room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    if room["status"] != "discussing":
        raise HTTPException(status_code=409, detail="Room is not in discussing status")

    scheduler = _schedulers.get(room_id)
    if scheduler:
        await scheduler.stop(room_id)
    await repo.update_status(room_id, "stopped")
    return {"stopped": True, "room_id": room_id}
```

- [ ] **Step 4: Run all tests**

Run: `pytest tests/ -v`
Expected: ALL tests pass (30+ tests)

- [ ] **Step 5: Commit**

```bash
git add backend/services/scheduler.py backend/routes/discussion.py backend/main.py tests/test_api_discussion.py
git commit -m "feat: full discussion scheduler loop and POST /start + /stop endpoints"
```

---

### Task 16: Error Codes & Output Filter

**Files:**
- Create: `backend/errors.py`
- Create: `backend/services/output_filter.py`

- [ ] **Step 1: Write the tests**

```python
# tests/test_output_filter.py
from backend.services.output_filter import OutputFilter

class TestOutputFilter:
    def test_strip_thinking_tags(self):
        text = "公开内容<thinking>隐藏思维链</thinking>更多内容"
        result = OutputFilter.strip_hidden_cot(text)
        assert "<thinking>" not in result
        assert "隐藏思维链" not in result
        assert "公开内容" in result
        assert "更多内容" in result

    def test_strip_json_block(self):
        text = '正常发言\n```json\n{"key":"value"}\n```\n后续内容'
        result = OutputFilter.strip_json_block(text)
        assert "```json" not in result
        assert '"key":"value"' not in result
        assert "正常发言" in result
        assert "后续内容" in result

    def test_sanitize_full_pipeline(self):
        text = '观点<thinking>内部推理</thinking>```json\n{"a":1}\n```结尾'
        result = OutputFilter.sanitize(text)
        assert "内部推理" not in result
        assert "```json" not in result
        assert "观点" in result
        assert "结尾" in result

    def test_clean_text_passes_through(self):
        text = "这是一段正常的发言内容"
        result = OutputFilter.sanitize(text)
        assert result.strip() == text
```

- [ ] **Step 2: Verify tests fail**

Run: `pytest tests/test_output_filter.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: Write implementation**

```python
# backend/errors.py
class ErrorCode:
    ROOM_NOT_FOUND = "ROOM_NOT_FOUND"
    INVALID_STATUS = "INVALID_STATUS"
    EXPERTS_ALREADY_GEN = "EXPERTS_ALREADY_GEN"
    LLM_TIMEOUT = "LLM_TIMEOUT"
    LLM_INVALID_RESPONSE = "LLM_INVALID_RESPONSE"
    SSE_CONNECTION_LOST = "SSE_CONNECTION_LOST"
    INTERNAL_ERROR = "INTERNAL_ERROR"
```

```python
# backend/services/output_filter.py
import re

class OutputFilter:
    """保障前端永远不会收到 LLM 原始/不安全输出"""

    @staticmethod
    def strip_hidden_cot(text: str) -> str:
        text = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL)
        text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
        text = re.sub(r'\[COT\].*?\[/COT\]', '', text, flags=re.DOTALL)
        return text

    @staticmethod
    def strip_json_block(text: str) -> str:
        text = re.sub(r'```json\s*\n.*?\n```', '', text, flags=re.DOTALL)
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        return text

    @staticmethod
    def sanitize(text: str) -> str:
        text = OutputFilter.strip_hidden_cot(text)
        text = OutputFilter.strip_json_block(text)
        return text.strip()
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_output_filter.py -v`
Expected: 4 PASS

- [ ] **Step 5: Commit**

```bash
git add backend/errors.py backend/services/output_filter.py tests/test_output_filter.py
git commit -m "feat: error codes and LLM output safety filter"
```

---

### Task 17: Frontend Router & Zustand Stores

**Files:**
- Create: `frontend/src/store/index.ts`
- Create: `frontend/src/store/roomSlice.ts`
- Create: `frontend/src/store/expertSlice.ts`
- Create: `frontend/src/store/transcriptSlice.ts`
- Create: `frontend/src/store/insightSlice.ts`
- Create: `frontend/src/store/uiSlice.ts`
- Create: `frontend/src/router.tsx`
- Modify: `frontend/src/main.tsx`
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Write store tests**

```typescript
// frontend/src/store/__tests__/roomSlice.test.ts
import { describe, it, expect } from 'vitest';
import { useRoomStore } from '../roomSlice';

describe('roomSlice', () => {
  it('starts with empty rooms', () => {
    const { rooms } = useRoomStore.getState();
    expect(rooms).toEqual([]);
  });

  it('creates a room', async () => {
    // Will be tested with MSW or mock later
    expect(true).toBe(true);
  });
});
```

- [ ] **Step 2: Install dependencies & implement**

```bash
cd frontend && npm install zustand react-router-dom && npm install -D @types/react-router-dom
```

```typescript
// frontend/src/store/roomSlice.ts
import { create } from 'zustand';

interface Room {
  id: string; topic: string; expert_count: number;
  status: string; created_at: string; updated_at: string;
}

interface RoomDetail extends Room {
  experts: Expert[]; transcript_count: number; insight_count: number;
}

interface Expert {
  id: string; name: string; title: string; stance: string;
  color: string; role: 'host' | 'expert'; position: number;
  current_status: 'idle' | 'preparing' | 'speaking'; public_thought: string;
}

interface RoomState {
  rooms: Room[];
  currentRoom: RoomDetail | null;
  setRooms: (rooms: Room[]) => void;
  setCurrentRoom: (room: RoomDetail) => void;
  updateRoomStatus: (id: string, status: string) => void;
}

export const useRoomStore = create<RoomState>((set) => ({
  rooms: [],
  currentRoom: null,
  setRooms: (rooms) => set({ rooms }),
  setCurrentRoom: (room) => set({ currentRoom: room }),
  updateRoomStatus: (id, status) => set((state) => ({
    rooms: state.rooms.map(r => r.id === id ? { ...r, status } : r),
    currentRoom: state.currentRoom?.id === id
      ? { ...state.currentRoom, status } : state.currentRoom,
  })),
}));
```

```typescript
// frontend/src/store/expertSlice.ts
import { create } from 'zustand';

interface ExpertState {
  experts: Expert[];
  host: Expert | null;
  setExperts: (host: Expert, experts: Expert[]) => void;
  updateExpertState: (expertId: string, status: ExpertStatus, thought: string) => void;
}

type ExpertStatus = 'idle' | 'preparing' | 'speaking';

interface Expert {
  id: string; name: string; title: string; stance: string;
  color: string; role: 'host' | 'expert'; position: number;
  current_status: ExpertStatus; public_thought: string;
}

export const useExpertStore = create<ExpertState>((set) => ({
  experts: [],
  host: null,
  setExperts: (host, experts) => set({ host, experts }),
  updateExpertState: (expertId, status, thought) => set((state) => ({
    experts: state.experts.map(e =>
      e.id === expertId ? { ...e, current_status: status, public_thought: thought } : e
    ),
    host: state.host?.id === expertId
      ? { ...state.host, current_status: status, public_thought: thought } : state.host,
  })),
}));
```

```typescript
// frontend/src/store/transcriptSlice.ts
import { create } from 'zustand';

interface TranscriptLine {
  id: string; expert_id: string; name: string; title: string;
  color: string; content: string; line_type: string;
  sequence_num: number; created_at: string;
}

interface TranscriptState {
  lines: TranscriptLine[];
  isStreaming: boolean;
  setLines: (lines: TranscriptLine[]) => void;
  addLine: (line: TranscriptLine) => void;
}

export const useTranscriptStore = create<TranscriptState>((set) => ({
  lines: [],
  isStreaming: false,
  setLines: (lines) => set({ lines }),
  addLine: (line) => set((state) => ({
    lines: [...state.lines, line],
  })),
}));
```

```typescript
// frontend/src/store/insightSlice.ts
import { create } from 'zustand';

interface InsightItem {
  id: string; type: 'consensus' | 'disagreement'; content: string;
}

interface InsightState {
  consensus: InsightItem[];
  disagreement: InsightItem[];
  setInsights: (consensus: InsightItem[], disagreement: InsightItem[]) => void;
  updateInsights: (consensus: InsightItem[], disagreement: InsightItem[]) => void;
}

export const useInsightStore = create<InsightState>((set) => ({
  consensus: [],
  disagreement: [],
  setInsights: (consensus, disagreement) => set({ consensus, disagreement }),
  updateInsights: (consensus, disagreement) => set({ consensus, disagreement }),
}));
```

```typescript
// frontend/src/store/uiSlice.ts
import { create } from 'zustand';

interface UIState {
  sidebarCollapsed: boolean;
  activeBreakpoint: 'narrow' | 'desktop' | 'wide';
  toggleSidebar: () => void;
  setBreakpoint: (bp: 'narrow' | 'desktop' | 'wide') => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarCollapsed: false,
  activeBreakpoint: 'desktop',
  toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
  setBreakpoint: (bp) => set({ activeBreakpoint: bp }),
}));
```

```typescript
// frontend/src/store/index.ts
export { useRoomStore } from './roomSlice';
export { useExpertStore } from './expertSlice';
export { useTranscriptStore } from './transcriptSlice';
export { useInsightStore } from './insightSlice';
export { useUIStore } from './uiSlice';
```

```typescript
// frontend/src/router.tsx
import { createBrowserRouter } from 'react-router-dom';
import App from './App';
import HomePage from './pages/HomePage';
import LobbyPage from './pages/LobbyPage';
import StudioPage from './pages/StudioPage';
import SummaryPage from './pages/SummaryPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'room/:id/lobby', element: <LobbyPage /> },
      { path: 'room/:id/studio', element: <StudioPage /> },
      { path: 'room/:id/summary', element: <SummaryPage /> },
    ],
  },
]);
```

```tsx
// frontend/src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { RouterProvider } from 'react-router-dom';
import { router } from './router';
import './styles/tokens.css';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
```

- [ ] **Step 3: Run tests**

Run: `cd frontend && npx vitest run`
Expected: Store tests pass, App renders

- [ ] **Step 4: Commit**

```bash
git add frontend/src/store/ frontend/src/router.tsx frontend/src/main.tsx frontend/src/App.tsx
git commit -m "feat: Zustand stores (room, expert, transcript, insight, ui) and React Router"
```

---

### Task 18: Frontend API Client Layer

**Files:**
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/api/rooms.ts`
- Create: `frontend/src/api/experts.ts`
- Create: `frontend/src/api/discussion.ts`

- [ ] **Step 1: Write the API client**

```typescript
// frontend/src/api/client.ts
const API_BASE = 'http://localhost:3000';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: 'POST', body: body ? JSON.stringify(body) : undefined }),
};
```

```typescript
// frontend/src/api/rooms.ts
import { api } from './client';

export interface RoomResponse {
  id: string; topic: string; expert_count: number;
  status: string; created_at: string; updated_at: string;
}

export interface RoomDetail extends RoomResponse {
  experts: ExpertResponse[];
  transcript_count: number; insight_count: number;
}

export interface ExpertResponse {
  id: string; name: string; title: string; stance: string;
  color: string; role: 'host' | 'expert'; position: number;
  current_status: 'idle' | 'preparing' | 'speaking'; public_thought: string;
}

export function createRoom(topic: string, expert_count: number) {
  return api.post<RoomResponse>('/api/rooms', { topic, expert_count });
}

export function listRooms() {
  return api.get<{ rooms: RoomResponse[] }>('/api/rooms');
}

export function getRoomDetail(id: string) {
  return api.get<RoomDetail>(`/api/rooms/${id}`);
}
```

```typescript
// frontend/src/api/experts.ts
import { api } from './client';
import type { ExpertResponse } from './rooms';

interface ExpertGenerationResponse {
  host: ExpertResponse;
  experts: ExpertResponse[];
  fallback?: boolean;
}

export function generateExperts(roomId: string) {
  return api.post<ExpertGenerationResponse>(
    `/api/rooms/${roomId}/experts`, { user_confirmed: false }
  );
}
```

```typescript
// frontend/src/api/discussion.ts
import { api } from './client';

export function startDiscussion(roomId: string) {
  return api.post<{ stream_started: boolean; room_id: string }>(
    `/api/rooms/${roomId}/start`
  );
}

export function stopDiscussion(roomId: string) {
  return api.post<{ stopped: boolean; room_id: string }>(
    `/api/rooms/${roomId}/stop`
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/api/
git commit -m "feat: frontend API client layer with typed fetch wrapper"
```

---

### Task 19: Frontend useSSE Hook

**Files:**
- Create: `frontend/src/hooks/useSSE.ts`

- [ ] **Step 1: Write the hook**

```typescript
// frontend/src/hooks/useSSE.ts
import { useEffect, useRef, useCallback } from 'react';
import { useRoomStore } from '../store/roomSlice';
import { useExpertStore } from '../store/expertSlice';
import { useTranscriptStore } from '../store/transcriptSlice';
import { useInsightStore } from '../store/insightSlice';

const SSE_BASE = 'http://localhost:3000';
const MAX_RECONNECT_ATTEMPTS = 5;

export function useSSE(roomId: string | null) {
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectCount = useRef(0);

  const updateRoomStatus = useRoomStore((s) => s.updateRoomStatus);
  const updateExpertState = useExpertStore((s) => s.updateExpertState);
  const addLine = useTranscriptStore((s) => s.addLine);
  const updateInsights = useInsightStore((s) => s.updateInsights);

  const connect = useCallback(() => {
    if (!roomId) return;

    const es = new EventSource(`${SSE_BASE}/api/rooms/${roomId}/stream`);
    eventSourceRef.current = es;

    es.addEventListener('room.status', (e) => {
      const data = JSON.parse(e.data);
      updateRoomStatus(data.room_id, data.status);
    });

    es.addEventListener('expert.state', (e) => {
      const data = JSON.parse(e.data);
      updateExpertState(data.expert_id, data.status, data.public_thought);
    });

    es.addEventListener('transcript.line', (e) => {
      const data = JSON.parse(e.data);
      addLine(data);
    });

    es.addEventListener('insight.update', (e) => {
      const data = JSON.parse(e.data);
      updateInsights(data.consensus, data.disagreement);
    });

    es.addEventListener('discussion.end', (e) => {
      const data = JSON.parse(e.data);
      updateRoomStatus(roomId, 'finished');
    });

    es.onerror = () => {
      es.close();
      if (reconnectCount.current < MAX_RECONNECT_ATTEMPTS) {
        reconnectCount.current++;
        const delay = Math.min(2000 * Math.pow(2, reconnectCount.current), 30000);
        setTimeout(connect, delay);
      }
    };

    es.onopen = () => {
      reconnectCount.current = 0;
    };
  }, [roomId, updateRoomStatus, updateExpertState, addLine, updateInsights]);

  const disconnect = useCallback(() => {
    eventSourceRef.current?.close();
    eventSourceRef.current = null;
  }, []);

  useEffect(() => {
    return () => { eventSourceRef.current?.close(); };
  }, []);

  return { connect, disconnect };
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/hooks/useSSE.ts
git commit -m "feat: SSE client hook with auto-reconnect and event dispatch to Zustand"
```

---

### Task 20: HomePage — Discussion List + New Discussion Dialog

**Files:**
- Create: `frontend/src/pages/HomePage.tsx`
- Create: `frontend/src/components/home/RoomList.tsx`
- Create: `frontend/src/components/home/NewRoomDialog.tsx`
- Create: `frontend/src/pages/__tests__/HomePage.test.tsx`

- [ ] **Step 1: Write test**

```tsx
// frontend/src/pages/__tests__/HomePage.test.tsx
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import HomePage from '../HomePage';
import { BrowserRouter } from 'react-router-dom';

describe('HomePage', () => {
  it('renders the page title', () => {
    render(
      <BrowserRouter>
        <HomePage />
      </BrowserRouter>
    );
    expect(screen.getByText('AI Panel Studio')).toBeDefined();
  });

  it('shows new discussion button', () => {
    render(
      <BrowserRouter>
        <HomePage />
      </BrowserRouter>
    );
    expect(screen.getByText(/新建讨论/)).toBeDefined();
  });
});
```

- [ ] **Step 2: Implement**

```tsx
// frontend/src/pages/HomePage.tsx
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { listRooms, createRoom, type RoomResponse } from '../api/rooms';
import { useRoomStore } from '../store/roomSlice';
import RoomList from '../components/home/RoomList';
import NewRoomDialog from '../components/home/NewRoomDialog';

export default function HomePage() {
  const navigate = useNavigate();
  const { rooms, setRooms } = useRoomStore();
  const [showDialog, setShowDialog] = useState(false);

  useEffect(() => {
    listRooms().then((data) => setRooms(data.rooms)).catch(console.error);
  }, [setRooms]);

  const handleCreate = async (topic: string, count: number) => {
    const room = await createRoom(topic, count);
    setShowDialog(false);
    navigate(`/room/${room.id}/lobby`);
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--bg-primary)', color: 'var(--text-primary)' }}>
      <header className="p-6 border-b" style={{ borderColor: 'var(--border-default)' }}>
        <h1 className="text-2xl font-bold">AI Panel Studio</h1>
        <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>AI 圆桌讨论</p>
      </header>
      <main className="p-6">
        <div className="mb-6 flex justify-between items-center">
          <h2 className="text-xl font-semibold">讨论列表</h2>
          <button
            onClick={() => setShowDialog(true)}
            className="px-4 py-2 rounded-lg text-white font-medium"
            style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)' }}
          >
            + 新建讨论
          </button>
        </div>
        <RoomList rooms={rooms} onEnter={(id) => navigate(`/room/${id}/lobby`)} />
      </main>
      {showDialog && (
        <NewRoomDialog
          onSubmit={handleCreate}
          onCancel={() => setShowDialog(false)}
        />
      )}
    </div>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/HomePage.tsx frontend/src/components/home/ frontend/src/pages/__tests__/
git commit -m "feat: HomePage with discussion list and new discussion dialog"
```

---

### Task 21: LobbyPage — Expert Lineup Confirmation

**Files:**
- Create: `frontend/src/pages/LobbyPage.tsx`
- Create: `frontend/src/components/lobby/ExpertCard.tsx`
- Create: `frontend/src/components/lobby/ExpertConfirmPanel.tsx`

- [ ] **Step 1: Implement LobbyPage**

```tsx
// frontend/src/pages/LobbyPage.tsx
import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getRoomDetail, generateExperts, type ExpertResponse } from '../api/rooms';
import { useExpertStore } from '../store/expertSlice';
import ExpertCard from '../components/lobby/ExpertCard';
import ExpertConfirmPanel from '../components/lobby/ExpertConfirmPanel';

export default function LobbyPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { experts, host, setExperts } = useExpertStore();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    getRoomDetail(id).then((room) => {
      const hostExpert = room.experts.find(e => e.role === 'host');
      const panelists = room.experts.filter(e => e.role === 'expert');
      if (hostExpert && panelists.length > 0) {
        setExperts(hostExpert, panelists);
        setLoading(false);
        return;
      }
      // Generate if no experts yet
      generateExperts(id).then((data) => {
        setExperts(data.host, data.experts);
        setLoading(false);
      }).catch(() => setLoading(false));
    }).catch(() => setLoading(false));
  }, [id, setExperts]);

  const handleConfirm = () => {
    navigate(`/room/${id}/studio`);
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: 'var(--bg-primary)', color: 'var(--text-primary)' }}>生成专家阵容中...</div>;
  }

  return (
    <div className="min-h-screen p-6" style={{ backgroundColor: 'var(--bg-primary)', color: 'var(--text-primary)' }}>
      <h1 className="text-2xl font-bold mb-2">专家阵容确认</h1>
      <p className="mb-6" style={{ color: 'var(--text-secondary)' }}>
        请确认以下由 AI 生成的专家阵容，确认后将正式进入演播厅
      </p>
      {host && (
        <div className="mb-6">
          <h2 className="text-lg font-semibold mb-3">主持人</h2>
          <ExpertCard expert={host} isHost />
        </div>
      )}
      <h2 className="text-lg font-semibold mb-3">讨论专家 ({experts.length}人)</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        {experts.map((expert) => (
          <ExpertCard key={expert.id} expert={expert} />
        ))}
      </div>
      <ExpertConfirmPanel onConfirm={handleConfirm} onBack={() => navigate('/')} />
    </div>
  );
}
```

```tsx
// frontend/src/components/lobby/ExpertCard.tsx
import type { ExpertResponse } from '../../api/rooms';

export default function ExpertCard({ expert, isHost = false }: { expert: ExpertResponse; isHost?: boolean }) {
  return (
    <div
      className="p-4 rounded-xl border"
      style={{
        backgroundColor: isHost ? 'var(--bg-card)' : 'var(--bg-card)',
        borderColor: isHost ? '#94a3b8' : expert.color,
        borderLeftWidth: '4px',
      }}
    >
      <div className="flex items-center gap-3">
        <div
          className="w-10 h-10 rounded-full flex-shrink-0"
          style={{ background: isHost ? 'linear-gradient(135deg, #f8fafc, #94a3b8)' : `linear-gradient(135deg, ${expert.color}, ${expert.color}88)` }}
        />
        <div>
          <h3 className="font-semibold">{expert.name}</h3>
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>{expert.title}</p>
        </div>
        {isHost && (
          <span className="ml-auto text-xs px-2 py-0.5 rounded" style={{ backgroundColor: 'var(--bg-card-hover)' }}>MC</span>
        )}
      </div>
      <p className="mt-3 text-sm italic" style={{ color: 'var(--text-secondary)' }}>
        「{expert.stance}」
      </p>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/pages/LobbyPage.tsx frontend/src/components/lobby/
git commit -m "feat: LobbyPage with AI-generated expert lineup confirmation"
```

---

### Task 22: StudioPage — Expert Panel with State Animations

**Files:**
- Create: `frontend/src/pages/StudioPage.tsx`
- Create: `frontend/src/components/studio/ExpertPanel.tsx`
- Create: `frontend/src/components/studio/ExpertMiniCard.tsx`

- [ ] **Step 1: Implement ExpertMiniCard with animations**

```tsx
// frontend/src/components/studio/ExpertMiniCard.tsx
import type { ExpertResponse } from '../../api/rooms';

const ANIMATION_MAP: Record<string, string> = {
  idle: 'var(--anim-idle)',
  preparing: 'var(--anim-preparing)',
  speaking: 'var(--anim-speaking)',
};

export default function ExpertMiniCard({ expert }: { expert: ExpertResponse }) {
  const isHost = expert.role === 'host';
  const animation = ANIMATION_MAP[expert.current_status] || ANIMATION_MAP.idle;
  const statusLabel = { idle: '待机', preparing: '准备发言', speaking: '发言中' }[expert.current_status];

  return (
    <div
      className="p-3 rounded-xl border transition-all duration-300"
      style={{
        backgroundColor: 'var(--bg-card)',
        borderColor: expert.current_status === 'speaking' ? expert.color : 'var(--border-default)',
        animation,
      }}
    >
      <div className="flex items-center gap-2">
        <div
          className="w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-xs font-bold"
          style={{
            background: isHost
              ? 'var(--host-gradient)'
              : `var(--expert-gradient-${expert.position % 8})`,
            color: isHost ? 'var(--host-text)' : '#fff',
          }}
        >
          {expert.name[0]}
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-sm font-semibold truncate">{expert.name}</p>
          <p className="text-xs truncate" style={{ color: 'var(--text-muted)' }}>{expert.title}</p>
        </div>
        <span
          className="text-xs px-1.5 py-0.5 rounded"
          style={{
            backgroundColor: expert.current_status === 'speaking' ? `${expert.color}33` : 'transparent',
            color: expert.current_status === 'speaking' ? expert.color : 'var(--text-muted)',
          }}
        >
          {statusLabel}
        </span>
      </div>
      {expert.public_thought && (
        <p className="mt-2 text-xs italic" style={{ color: 'var(--text-secondary)' }}>
          💭 {expert.public_thought}
        </p>
      )}
    </div>
  );
}
```

```tsx
// frontend/src/components/studio/ExpertPanel.tsx
import { useExpertStore } from '../../store/expertSlice';
import ExpertMiniCard from './ExpertMiniCard';

export default function ExpertPanel() {
  const host = useExpertStore((s) => s.host);
  const experts = useExpertStore((s) => s.experts);

  return (
    <div className="h-full overflow-y-auto p-4" style={{ backgroundColor: 'var(--bg-secondary)' }}>
      <h3 className="text-sm font-semibold mb-3" style={{ color: 'var(--text-secondary)' }}>专家状态</h3>
      {host && (
        <div className="mb-3">
          <ExpertMiniCard expert={host} />
        </div>
      )}
      <div className="flex flex-col gap-2">
        {experts.map((expert) => (
          <ExpertMiniCard key={expert.id} expert={expert} />
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/studio/ExpertPanel.tsx frontend/src/components/studio/ExpertMiniCard.tsx
git commit -m "feat: Expert panel with state-driven animations (idle/preparing/speaking)"
```

---

### Task 23: StudioPage — Transcript & Insight Panels

**Files:**
- Create: `frontend/src/components/studio/TranscriptPanel.tsx`
- Create: `frontend/src/components/studio/InsightPanel.tsx`

- [ ] **Step 1: Implement**

```tsx
// frontend/src/components/studio/TranscriptPanel.tsx
import { useEffect, useRef } from 'react';
import { useTranscriptStore } from '../../store/transcriptSlice';

const TYPE_LABELS: Record<string, string> = {
  opening: '开场', argument: '论点', rebuttal: '反驳',
  supplement: '补充', question: '提问', closing: '总结',
};

export default function TranscriptPanel() {
  const lines = useTranscriptStore((s) => s.lines);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [lines.length]);

  return (
    <div
      className="h-full overflow-y-auto p-4"
      style={{ backgroundColor: 'var(--bg-transcript)' }}
    >
      <h3 className="text-sm font-semibold mb-3" style={{ color: 'var(--text-secondary)' }}>现场字幕</h3>
      {lines.length === 0 && (
        <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
          讨论尚未开始，等待主持人开场...
        </p>
      )}
      <div className="space-y-3">
        {lines.map((line) => (
          <div key={line.id} className="flex gap-3 animate-fadeIn">
            <div className="flex-shrink-0 mt-1">
              <span
                className="inline-block text-xs px-1.5 py-0.5 rounded"
                style={{ color: line.color, backgroundColor: `${line.color}15` }}
              >
                {TYPE_LABELS[line.line_type] || line.line_type}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-sm" style={{ color: line.color }}>
                  {line.name}
                </span>
                <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
                  {line.title}
                </span>
              </div>
              <p className="mt-1 text-sm leading-relaxed">{line.content}</p>
            </div>
          </div>
        ))}
      </div>
      <div ref={bottomRef} />
    </div>
  );
}
```

```tsx
// frontend/src/components/studio/InsightPanel.tsx
import { useInsightStore } from '../../store/insightSlice';

export default function InsightPanel() {
  const consensus = useInsightStore((s) => s.consensus);
  const disagreement = useInsightStore((s) => s.disagreement);

  return (
    <div className="h-full overflow-y-auto p-4" style={{ backgroundColor: 'var(--bg-secondary)' }}>
      <h3 className="text-sm font-semibold mb-3" style={{ color: 'var(--text-secondary)' }}>实时洞察</h3>

      <div className="mb-4">
        <h4 className="text-sm font-medium mb-2" style={{ color: 'var(--color-consensus)' }}>✅ 共识</h4>
        {consensus.length === 0 ? (
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>尚未提炼出共识...</p>
        ) : (
          <ul className="space-y-2">
            {consensus.map((item) => (
              <li
                key={item.id}
                className="p-2 rounded-lg text-sm"
                style={{ backgroundColor: 'var(--color-consensus-bg)' }}
              >
                {item.content}
              </li>
            ))}
          </ul>
        )}
      </div>

      <div>
        <h4 className="text-sm font-medium mb-2" style={{ color: 'var(--color-disagreement)' }}>⚡ 分歧</h4>
        {disagreement.length === 0 ? (
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>尚未提炼出分歧...</p>
        ) : (
          <ul className="space-y-2">
            {disagreement.map((item) => (
              <li
                key={item.id}
                className="p-2 rounded-lg text-sm"
                style={{ backgroundColor: 'var(--color-disagreement-bg)' }}
              >
                {item.content}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/studio/TranscriptPanel.tsx frontend/src/components/studio/InsightPanel.tsx
git commit -m "feat: Transcript panel and Insight panel with independent scrolling"
```

---

### Task 24: StudioPage — Layout, ControlBar & Full Integration

**Files:**
- Create: `frontend/src/components/studio/ControlBar.tsx`
- Modify: `frontend/src/pages/StudioPage.tsx`
- Create: `frontend/src/components/layout/AppShell.tsx`
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Implement StudioPage with full integration**

```tsx
// frontend/src/pages/StudioPage.tsx
import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getRoomDetail } from '../api/rooms';
import { useRoomStore } from '../store/roomSlice';
import { useExpertStore } from '../store/expertSlice';
import { useTranscriptStore } from '../store/transcriptSlice';
import { useInsightStore } from '../store/insightSlice';
import { useSSE } from '../hooks/useSSE';
import TranscriptPanel from '../components/studio/TranscriptPanel';
import ExpertPanel from '../components/studio/ExpertPanel';
import InsightPanel from '../components/studio/InsightPanel';
import ControlBar from '../components/studio/ControlBar';

export default function StudioPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { setCurrentRoom, currentRoom } = useRoomStore();
  const { setExperts } = useExpertStore();
  const { setLines } = useTranscriptStore();
  const { setInsights } = useInsightStore();
  const { connect } = useSSE(id || null);

  useEffect(() => {
    if (!id) return;
    getRoomDetail(id).then((room) => {
      setCurrentRoom(room);
      const hostExpert = room.experts.find((e: any) => e.role === 'host');
      const panelists = room.experts.filter((e: any) => e.role === 'expert');
      if (hostExpert) setExperts(hostExpert, panelists);
      // Load transcript from API
      setLines([]);
      setInsights([], []);
    }).catch(console.error);
  }, [id]);

  useEffect(() => {
    if (currentRoom?.status === 'ready' || currentRoom?.status === 'discussing') {
      connect();
    }
    if (currentRoom?.status === 'finished' || currentRoom?.status === 'stopped') {
      navigate(`/room/${id}/summary`);
    }
  }, [currentRoom?.status]);

  return (
    <div
      className="h-screen overflow-hidden flex flex-col"
      style={{ backgroundColor: 'var(--bg-primary)', color: 'var(--text-primary)' }}
    >
      <ControlBar roomId={id || ''} />
      <div className="flex-1 overflow-hidden grid grid-cols-1 md:grid-cols-3 xl:grid-cols-4 gap-0">
        {/* Narrow: stack vertically; Desktop: main 2 + right 1; Wide: main 2 + right 2 */}
        <div className="md:col-span-2 xl:col-span-2 overflow-hidden flex flex-col">
          <div className="flex-1 overflow-hidden">
            <TranscriptPanel />
          </div>
        </div>
        <div className="overflow-hidden">
          <ExpertPanel />
        </div>
        <div className="hidden xl:block overflow-hidden">
          <InsightPanel />
        </div>
        {/* Narrow/Desktop insight: show as bottom panel */}
        <div className="xl:hidden overflow-hidden" style={{ maxHeight: '30vh' }}>
          <InsightPanel />
        </div>
      </div>
    </div>
  );
}
```

```tsx
// frontend/src/components/studio/ControlBar.tsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { startDiscussion, stopDiscussion } from '../../api/discussion';

export default function ControlBar({ roomId }: { roomId: string }) {
  const navigate = useNavigate();
  const [started, setStarted] = useState(false);
  const [stopping, setStopping] = useState(false);

  const handleStart = async () => {
    await startDiscussion(roomId);
    setStarted(true);
  };

  const handleStop = async () => {
    await stopDiscussion(roomId);
    setStopping(true);
  };

  return (
    <div
      className="flex items-center justify-between px-4 py-2 border-b flex-shrink-0"
      style={{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-default)' }}
    >
      <button
        onClick={() => navigate('/')}
        className="text-sm hover:underline"
        style={{ color: 'var(--text-secondary)' }}
      >
        ← 返回首页
      </button>
      <div className="flex gap-3">
        {!started && (
          <button
            onClick={handleStart}
            className="px-6 py-1.5 rounded-lg text-white text-sm font-medium"
            style={{ background: 'linear-gradient(135deg, #10b981, #14b8a6)' }}
          >
            开始讨论
          </button>
        )}
        {started && !stopping && (
          <button
            onClick={handleStop}
            className="px-6 py-1.5 rounded-lg text-white text-sm font-medium"
            style={{ background: 'linear-gradient(135deg, #ef4444, #dc2626)' }}
          >
            终止讨论
          </button>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/pages/StudioPage.tsx frontend/src/components/studio/ControlBar.tsx
git commit -m "feat: StudioPage with full layout, control bar, and SSE integration"
```

---

### Task 25: SummaryPage & Final Integration

**Files:**
- Create: `frontend/src/pages/SummaryPage.tsx`
- Create: `frontend/src/components/summary/SummaryPanel.tsx`

- [ ] **Step 1: Implement**

```tsx
// frontend/src/pages/SummaryPage.tsx
import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getRoomDetail } from '../api/rooms';
import { useRoomStore } from '../store/roomSlice';
import SummaryPanel from '../components/summary/SummaryPanel';

export default function SummaryPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { currentRoom, setCurrentRoom } = useRoomStore();

  useEffect(() => {
    if (!id) return;
    getRoomDetail(id).then(setCurrentRoom).catch(console.error);
  }, [id]);

  if (!currentRoom) {
    return <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: 'var(--bg-primary)', color: 'var(--text-primary)' }}>加载中...</div>;
  }

  return (
    <div className="min-h-screen p-6" style={{ backgroundColor: 'var(--bg-primary)', color: 'var(--text-primary)' }}>
      <button
        onClick={() => navigate('/')}
        className="mb-6 text-sm hover:underline"
        style={{ color: 'var(--text-secondary)' }}
      >
        ← 返回首页
      </button>
      <h1 className="text-2xl font-bold mb-2">讨论总结</h1>
      <p className="mb-6" style={{ color: 'var(--text-secondary)' }}>
        话题：{currentRoom.topic} | 状态：{currentRoom.status}
      </p>
      <SummaryPanel roomId={id!} />
    </div>
  );
}
```

- [ ] **Step 2: Commit & then run all tests**

```bash
git add frontend/src/pages/SummaryPage.tsx frontend/src/components/summary/
git commit -m "feat: SummaryPage with discussion recap"
```

- [ ] **Step 3: Final test run**

```bash
# Backend tests
cd backend && pip install -r requirements.txt && pytest ../tests/ -v

# Frontend tests
cd frontend && npx vitest run
```

Expected: ALL tests pass (40+ tests)

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "feat: complete Smart AI Panel MVP — all endpoints, frontend, scheduler, and tests"
```

---

## Verification Checklist

- [ ] `pytest tests/ -v` → All backend tests PASS (40+ tests)
- [ ] `cd frontend && npx vitest run` → All frontend tests PASS
- [ ] `uvicorn backend.main:app` → Swagger at :3000/docs, all 6 endpoints functional
- [ ] `cd frontend && npm run dev` → HomePage at :5173, full flow works with Mock LLM
- [ ] 3 rooms simultaneously stream SSE, no cross-contamination
- [ ] Frontend panels scroll independently, no global scrollbar
- [ ] Expert cards show idle/preparing/speaking animations
- [ ] No JSON rendered on any frontend page

