# Architecture Design: LINE 股票 AI 助手

## 1. 系統概觀 (System Overview)
本系統是一個基於事件驅動 (Event-driven) 的 LINE 機器人。系統接收來自 LINE 平台的 Webhook 事件，透過 Gemini AI 模型解析使用者意圖，並整合外部股票 API 與內部 SQLite 資料庫，提供即時行情與個人化自選股管理服務。

## 2. 技術堆棧 (Tech Stack)
- **Frontend**: LINE Messaging App (客戶端介面)。
- **Backend**: Python 3.10+, FastAPI (非同步 Web 框架)。
- **AI Model**: Google Gemini 2.5-flash (意圖識別、自然語言生成、Function Calling)。
- **Database**: SQLite (SQLAlchemy ORM)，儲存用戶資料、對話歷史與追蹤清單。
- **LINE SDK**: `line-bot-sdk-python` (處理 Messaging API 串接)。
- **Stock API**: `yfinance` 或 相關財經 API。

## 3. 核心組件設計 (Component Design)
- **Webhook Handler**: 負責接收與驗證 LINE 傳來的簽名，並將事件派發至處理邏輯。
- **AI Orchestrator (Gemini)**: 核心大腦，負責結合上下文與使用者輸入，並決定是否觸發 Tool Calling。
- **Database Manager**: 封裝 SQLite 操作，處理 `User`、`ChatHistory` 與 `Watchlist` 的增刪查改。
- **Stock Service**: 封裝外部股票 API 呼叫，提供標準化的股價與新聞格式。
- **Function Calling Registry**: 定義 AI 可調用的工具函式，並處理工具執行的結果回傳。

## 4. 資料流 (Data Flow)
1.  **接收訊息**：使用者在 LINE 發送訊息 -> LINE 伺服器轉發 `POST` 請求至 `/webhook`。
2.  **身分識別與上下文抓取**：後端提取 `userId`，從 SQLite 抓取最近 5-10 輪對話紀錄。
3.  **意圖分析 (AI)**：將訊息與歷史紀錄傳送給 Gemini 2.5-flash。
4.  **工具執行 (Tool Use)**：
    - 若使用者問「台積電現在多少錢？」，Gemini 觸發 `get_stock_price("2330.TW")`。
    - `Stock Service` 抓取即時數據並回傳給 Gemini。
5.  **生成回應**：Gemini 整合數據後產出人性化的回覆文字。
6.  **持久化與回傳**：將機器人的回覆存入 SQLite `ChatHistory`，並透過 LINE Messaging API 將訊息推播給使用者。

## 5. API 設計 (API Specifications)
- **`POST /webhook`**:
    - 用途：接收來自 LINE 的所有事件。
    - 認證：驗證 `X-Line-Signature`。
- **`GET /health`**:
    - 用途：監控系統運行狀態。
- **`POST /admin/broadcast` (選配)**：
    - 用途：向所有使用者發送系統通知。

## 6. 資料庫結構概念 (Database Schema)
- `users`: `id`, `line_user_id`, `created_at`
- `chat_history`: `id`, `user_id`, `role` (user/assistant), `content`, `timestamp`
- `watchlists`: `id`, `user_id`, `ticker`, `added_at`
