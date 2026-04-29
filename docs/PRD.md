# PRD: LINE 股票 AI 助手 (LINE Stock AI Bot)

## 1. 產品定義 (Product Definition)
- **一句話描述**：結合 Gemini 強大語言能力與實時股票數據的 LINE 智慧投資助手。
- **目標用戶**：一般投資大眾、需要快速獲取股票資訊與分析的 LINE 使用者。
- **核心痛點**：
    - 查股價需要切換多個 App，不夠直覺。
    - 複雜的技術指標與新聞難以快速消化。
    - 缺乏個人化的對話式投資助手。

## 2. 功能清單 (Feature List)
- **基礎對話**：串接 LINE Messaging API，支援文字訊息接收與回覆。
- **股票分析**：整合 Gemini API (預計使用 `gemini-2.5-flash`)，提供對話式的股票分析。
- **歷史管理**：
    - 使用 SQLite 儲存 `userId` 與對話紀錄 (Conversation History)。
    - 支援上下文理解（Context Awareness），讓對話與上下文更連貫。
- **記憶機制**：記錄使用者查詢過的股票代碼，提供更精準的推薦。
- **追蹤清單 (Watchlist)**：允許使用者將股票加入自選清單，並儲存於 SQLite 中。
- **資訊獲取 (工具整合)**：透過 Function Calling 串接股票 API（如 Yahoo Finance 或相關財經 API）獲取即時行情。

## 3. AI 互動與指令設計 (AI Interaction & Prompt Design)
- **系統指令 (System Instruction)**：
    - 「你是一位專業、客觀且友好的投資分析助理。你的任務是協助使用者理解股市動態。在提供任何分析時，必須包含『投資有風險，入市需謹慎』的免責聲明。若使用者詢問非股票相關問題，請委婉導回正軌。」
- **工具整合 (Function Calling)**：
    - `get_stock_price(ticker)`: 獲取指定股票的最新價格與漲跌幅。
    - `get_stock_news(ticker)`: 獲取該股票的最新相關新聞摘要。
    - `add_to_watchlist(ticker)`: 將股票加入使用者的追蹤清單。
    - `remove_from_watchlist(ticker)`: 將股票從追蹤清單中移除。
    - `get_watchlist()`: 獲取使用者目前所有的追蹤股票。

## 4. 系統架構概念 (High-level Architecture Concept)
- **前端**：LINE Messaging App (用戶端)。
- **後端**：FastAPI (處理 LINE Webhook、邏輯運算、Gemini API 呼叫)。
- **資料庫**：SQLite (儲存 `users`、`chat_history` 與 `watchlists` 表)。
- **部署環境**：支援 HTTPS 的伺服器 (如 Render, Heroku 或本機使用 ngrok 測試)。

## 5. 異常處理與邊界情況 (Edge Cases & Fallbacks)
- **API 失敗**：當 Gemini 或 股票 API 斷線時，回傳「系統繁忙中，請稍後再試」。
- **無效輸入**：當使用者輸入錯誤的股票代碼時，AI 應能辨識並提示正確格式。
- **敏感內容**：內建過濾機制，不針對特定股票給予強烈的「買入」或「賣出」指令，僅提供數據分析。

## 6. 成功指標 (Success Metrics)
- **回應速度**：Gemini 回應時間控制在 3 秒內。
- **用戶留存**：重複查詢股票的使用者比例。
- **任務完成率**：使用者成功獲取股票資訊的比率。
