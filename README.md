# W11 作業：股票 LINE Bot

> **繳交方式**：將你的 GitHub repo 網址貼到作業繳交區
> **作業性質**：個人作業

---

## 作業目標

利用上週設計的 Skill，開發一個股票相關的 LINE Bot。
重點不是功能多寡，而是你設計的 **Skill 品質**——Skill 寫得越具體，AI 產出的程式碼就越接近可以直接執行。

---

## 功能要求（擇一實作）

| 功能 | 說明 |
| --- | --- |
| AI 分析股票 | 使用者說股票名稱，Gemini 給出分析 |
| 追蹤清單 | 儲存使用者的自選股清單到 SQLite |
| 查詢即時價格 | 整合 yfinance 或 twstock 取得股價 |

> 以「可以執行、能回覆訊息」為目標，不需要複雜

---

## 繳交項目

你的 GitHub repo 需要包含：

| 項目 | 說明 |
| --- | --- |
| `app.py` | LINE Webhook + Gemini + SQLite 後端 |
| `requirements.txt` | 所有套件 |
| `.env.example` | 環境變數範本（不含真實 token） |
| `.agents/skills/` | 至少包含 `/linebot-implement` Skill |
| `README.md` | 本檔案（含心得報告） |
| `screenshots/chat.png` | LINE Bot 對話截圖（至少一輪完整對話） |

### Skill 要求

`.agents/skills/` 至少需要包含：

- `/linebot-implement`：產出 LINE Bot 主程式（必要）
- `/prd` 或 `/architecture`：延用上週的
- `/commit`：延用上週的

---

## 專案結構

```
your-repo/
├── .agents/
│   └── skills/
│       ├── prd/SKILL.md
│       ├── linebot-implement/SKILL.md
│       └── commit/SKILL.md
├── docs/
│   └── PRD.md
├── screenshots/
│   └── chat.png
├── app.py
├── requirements.txt
├── .env.example
└── README.md
```

> `.env` 和 `users.db` 不要 commit（加入 `.gitignore`）

---

## 啟動方式

```bash
# 1. 建立虛擬環境
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. 安裝套件
pip install -r requirements.txt

# 3. 設定環境變數
cp .env.example .env
# 編輯 .env，填入三個 token

# 4. 啟動 FastAPI
uvicorn app:app --reload

# 5. 另開終端機啟動 ngrok
ngrok http 8000
# 複製 https 網址，填入 LINE Developers Console 的 Webhook URL（加上 /callback）
# 點「Verify」確認連線正常後，掃 QR Code 加好友開始測試
```

---

## 心得報告

**姓名**：
**學號**：

**Q1. 你在 `/linebot-implement` Skill 的「注意事項」寫了哪些規則？為什麼這樣寫？**

在 `linebot-dev` (對應作業要求的 `/linebot-implement`) 的注意事項中，我主要寫了以下規則：
- **SDK v3 規範**：強制使用 `linebot.v3` 模組，確保與最新 API 相容並獲得更好的非同步支援。
- **環境變數安全**：嚴禁硬編碼 Secret/Token，必須透過 `.env` 讀取，避免個資外洩。
- **超時預防機制**：針對耗時的 Gemini API，必須實作非同步背景處理（如 `asyncio.create_task`），以符合 LINE Webhook 1 秒內回傳 200 OK 的規定。
- **HTTPS 要求**：明確標註開發時需配合 `ngrok` 提供安全連線。
**原因**：這些規則是為了防範 LINE Bot 開發最常見的失敗原因（超時、權限、安全性），讓 AI 能一次生成穩健的程式碼。

---

**Q2. 你的 Skill 第一次執行後，AI 產出的程式直接能跑嗎？需要修改哪些地方？修改後有沒有更新 Skill？**

**不能直接跑。** 雖然邏輯正確，但需要進行以下手動調整：
- **填寫 `.env`**：手動填入真實的 LINE Secret、Access Token 與 Gemini API Key。
- **Webhook 驗證**：需要在 LINE Console 手動填入 ngrok 的網址並點擊驗證。
- **依賴套件安裝**：需要執行 `pip install`。
**更新 Skill**：有的。初次嘗試時 AI 漏掉了非同步處理導致 1 秒超時，我隨後在 Skill 範例中加入了 `asyncio.create_task` 的結構，之後產出的版本就解決了超時問題。

---

**Q3. 你遇到什麼問題是 AI 沒辦法自己解決、需要你介入處理的？**

- **LINE 平台設定**：AI 無法進入 LINE Developers Console 開啟 Webhook 開關或停用自動回應。
- **外部服務串接**：AI 無法自動執行 `ngrok` 並取得隨機產生的網域，這需要我手動複製網址貼回設定。
- **實機互動測試**：最終在 LINE App 上的對話流暢度與 Rich Menu 點擊感，仍需我親自用手機操作來確認細節。

---

**Q4. 如果你要把這個 LINE Bot 讓朋友使用，你還需要做什麼？**

- **正式環境部署**：將程式部屬至 Render 或 AWS 等雲端平台，並配置固定 Domain 與 SSL 憑證。
- **使用者管理與擴展**：使用受管理型的資料庫（如 PostgreSQL）取代本地 SQLite，並增加錯誤處理與日誌監控。
- **功能引導**：設計圖文選單（Rich Menu）與歡迎訊息，引導朋友如何查詢股價或設定清單。
- **隱私聲明**：告知使用者其對話歷史與自選股清單的儲存方式，符合基本個資保護。
