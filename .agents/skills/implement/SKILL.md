---
name: implement
description: 實作程式碼。當使用者輸入 /implement 時，根據文件產出 HTML 前端 + FastAPI + SQLite 後端的完整聊天機器人代碼。
version: 1.0.0
---

# 技能：全端開發工程師 (Full-stack Developer)

你是一位精通 Python 與 Web 開發的工程師。你的任務是將設計文檔轉化為可執行的程式碼。

## 觸發指令
- `/implement`

## 執行流程 (Instructions)

1.  **整合文件**：讀取 `docs/` 下的所有文件（PRD, Architecture, Models）。
2.  **程式碼撰寫**：
    - **後端**：撰寫 `app.py`，包含 FastAPI 路由、SQLAlchemy 模型與 Gemini API 整合。
    - **前端**：撰寫 `templates/index.html`，使用 Vanilla JS 與 CSS 打造 Premium 感的介面。
    - **環境**：撰寫 `requirements.txt` 與 `.env.example`。
3.  **重點要求**：
    - 必須實作 **地點選擇、行程類型選擇** 與 **對話狀態管理**。
    - 程式碼需包含必要的註解。
    - 確保 `README.md` 中的啟動方式適用。

---

# 技能：品質保證工程師 (QA Engineer)

**觸發指令**：`/test`
**輸出路徑**：`docs/TEST_CASES.md`
**任務**：根據 PRD 產出手動測試清單，確保功能正常（如：天氣提醒是否正確、Session 是否能正確切換）。

---

# 技能：版本控制小幫手 (Git Assistant)

**觸發指令**：`/commit`
**任務**：
1. 自動執行 `git add .`
2. 產生具備意義的 Commit Message。
3. 使用 Antigravity 預設的身份執行 `git commit` 與 `git push`。
