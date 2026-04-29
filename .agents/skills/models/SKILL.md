---
name: models
description: 設計資料庫模型。當使用者輸入 /models 時，根據 ARCHITECTURE.md 產出 docs/MODELS.md，定義資料表結構與關聯。
version: 1.0.0
---

# 技能：資料建模師 (Data Modeler)

你是一位資深的資料庫工程師。你的任務是根據架構設計，定義出符合 SQLite 規範的資料表結構 (Schema)。

## 觸發指令
- `/models`

## 輸出路徑
- `docs/MODELS.md`

## 執行流程 (Instructions)

1.  **讀取架構**：讀取 `docs/ARCHITECTURE.md` 以了解資料儲存需求。
2.  **設計 Schema**：根據 **[資料模型模板]** 定義資料表、欄位類型、主鍵與外鍵。
3.  **ORM 映射**：提供對應的 SQLAlchemy 模型代碼範例。
4.  **自動儲存**：完成後將內容寫入 `docs/MODELS.md`。

---

## 資料模型模板

# Data Models: [產品名稱]

## 1. 資料庫類型
- **SQLite**

## 2. 資料表結構 (Schema)

### Table: `sessions`
儲存對話階段資訊。
- `id`: String (UUID), Primary Key
- `title`: String (地點或行程摘要)
- `created_at`: DateTime

### Table: `messages`
儲存每一則對話。
- `id`: Integer, Primary Key
- `session_id`: String, Foreign Key (sessions.id)
- `role`: String (user/assistant)
- `content`: Text
- `timestamp`: DateTime

### Table: `user_prefs`
儲存使用者偏好與天氣暫存。
- `session_id`: String, Foreign Key (sessions.id)
- `location`: String
- `itinerary_type`: String
- `weather_cache`: Text (JSON)

## 3. 關聯圖 (ERD Concept)
- `sessions` (1) --- (N) `messages`
- `sessions` (1) --- (1) `user_prefs`
