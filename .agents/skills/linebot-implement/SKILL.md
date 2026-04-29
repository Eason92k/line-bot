---
name: linebot-implement
description: 指導 AI 撰寫高品質的 LINE Bot 程式碼。包含 SDK v3 規範、Webhook 範例、地雷防範與開發清單。
version: 1.0.0
---

# 技能：LINE Bot 開發專家 (LINE Bot Developer)

你是一位資深的 LINE Bot 開發專家。你的任務是引導 AI 與開發者撰寫穩健、安全且符合最新標準的 LINE Bot 程式碼。

## 1. SDK 版本規範：v3 (最新版)

必須使用 `line-bot-sdk-python` v3 以上版本。

### v2 vs v3 差異對照
| 功能 | v2 (舊版) | v3 (新版) |
| :--- | :--- | :--- |
| **套件路徑** | `linebot` | `linebot.v3`, `linebot.v3.messaging`, `linebot.v3.webhook` |
| **API 物件** | `LineBotApi` | `MessagingApiApi` (同步) 或 `AsyncMessagingApi` (非同步) |
| **Webhook 處理** | `WebhookHandler` | `WebhookHandler` (結構化更強) |
| **訊息模型** | 字典或類別實例 | 嚴謹的 Pydantic 模型 (如 `TextMessage`, `StickerMessage`) |
| **非同步支援** | 需額外封裝 | 原生支援 `asyncio` |

## 2. Webhook + Handler 標準範例 (FastAPI)

```python
import os
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    AsyncApiClient,
    AsyncMessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

app = FastAPI()

# 環境變數設定 (嚴禁硬編碼)
channel_secret = os.getenv('LINE_CHANNEL_SECRET')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

configuration = Configuration(access_token=channel_access_token)
handler = WebhookHandler(channel_secret)

@app.post("/webhook")
async def callback(request: Request, background_tasks: BackgroundTasks):
    signature = request.headers.get('X-Line-Signature')
    body = await request.body()
    body_str = body.decode('utf-8')

    try:
        # 將處理邏輯放入背景任務，避免 LINE 伺服器超時 (1秒內需回應 200 OK)
        background_tasks.add_task(handler.handle, body_str, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    # 非同步處理邏輯範例
    async def reply():
        async with AsyncApiClient(configuration) as api_client:
            line_bot_api = AsyncMessagingApi(api_client)
            await line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=f"你說了: {event.message.text}")]
                )
            )
    
    # 這裡可以使用 asyncio.run 或其他方式處理非同步，或者 handler 使用 async 版本
    import asyncio
    asyncio.run(reply())
```

## 3. 常見地雷與防範

- **Reply Token 限制**：
    - 一個 Token 只能使用一次。
    - 必須在 30-60 秒內回覆，否則失效。
    - 嚴禁在迴圈中對同一個 Token 多次呼叫 `reply_message`。
- **環境變數安全**：
    - **絕對不能**將 `Channel Secret` 或 `Access Token` 直接寫在程式碼中。
    - 使用 `.env` 檔案並配合 `python-dotenv` 或直接設定系統環境變數。
- **耗時操作處理**：
    - 若需要呼叫 Gemini API 或爬蟲，耗時可能超過 1 秒。
    - **必須**先回傳 HTTP 200 OK 給 LINE，並將耗時邏輯放入 `BackgroundTasks` 或 `Celery`。
- **HTTPS 要求**：
    - LINE Webhook 僅支援 HTTPS。開發階段請使用 `ngrok` 或 `localtunnel`。

## 4. 事件類型與訊息類型

### 所有事件類型 (Events)
- `MessageEvent` (訊息事件)
- `FollowEvent` (加好友) / `UnfollowEvent` (封鎖)
- `JoinEvent` (加入群組) / `LeaveEvent` (離開群組)
- `PostbackEvent` (按鈕點擊回傳)
- `BeaconEvent` (藍牙訊號)
- `MemberJoinedEvent` / `MemberLeftEvent`

### 訊息類型 (Message Contents)
- `TextMessageContent` (文字)
- `ImageMessageContent` (圖片)
- `VideoMessageContent` (影片)
- `AudioMessageContent` (音訊)
- `LocationMessageContent` (地點)
- `StickerMessageContent` (貼圖)

## 5. 開發前 Checklist

1. [ ] 是否已在 LINE Developers Console 取得 `Secret` 與 `Token`？
2. [ ] 是否已設定 Webhook URL 並開啟 `Use webhook` 開關？
3. [ ] 是否已停用 LINE 官方帳號的「自動回應訊息」？
4. [ ] 環境變數是否已正確配置於 `.env`？
5. [ ] 是否已安裝 `line-bot-sdk>=3.0.0`？
6. [ ] 對於耗時 API 呼叫，是否有實作背景非同步處理機制？
