import os
import logging
import asyncio
import datetime
from typing import List, Optional

import yfinance as yf
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from dotenv import load_dotenv

# LINE SDK v3
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

# Google Gemini
import google.generativeai as genai

# Database
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# 加載環境變數
load_dotenv()

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 設定區 ---
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./line_bot.db")

# 初始化 Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# 初始化 LINE SDK
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# --- 資料庫模型 ---
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    line_user_id = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    history = relationship("ChatHistory", back_populates="user")
    watchlist = relationship("Watchlist", back_populates="user")

class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("User", back_populates="history")

class Watchlist(Base):
    __tablename__ = "watchlists"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ticker = Column(String)
    added_at = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("User", back_populates="watchlist")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# --- 工具函式 ---
def get_stock_price(ticker: str) -> str:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        current_price = info.get("regularMarketPrice") or info.get("currentPrice")
        if current_price:
            return f"{ticker} 當前價格: {current_price}"
        return f"無法獲取 {ticker} 價格。"
    except:
        return f"查詢 {ticker} 出錯。"

def get_stock_news(ticker: str) -> str:
    try:
        stock = yf.Ticker(ticker)
        news = stock.news[:2]
        return "\n".join([n['title'] for n in news]) if news else "無新聞。"
    except:
        return "查詢新聞出錯。"

# --- 核心邏輯 ---
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "LINE Stock Bot is running!"}

@app.post("/callback")
async def callback(request: Request, background_tasks: BackgroundTasks):
    body = await request.body()
    body_str = body.decode("utf-8")
    
    print("\n" + "="*50)
    print(f"【收到訊息】時間: {datetime.datetime.now()}")
    print(f"內容: {body_str}")
    print("="*50 + "\n")

    signature = request.headers.get("X-Line-Signature")
    try:
        handler.handle(body_str, signature)
    except Exception as e:
        print(f"【處理失敗】: {str(e)}")
    
    return "OK"

@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event: MessageEvent):
    user_id = event.source.user_id
    text = event.message.text
    reply_token = event.reply_token
    # 建立新 Task 處理 Gemini 邏輯
    asyncio.create_task(process_gemini_chat(user_id, text, reply_token))

async def process_gemini_chat(line_user_id: str, text: str, reply_token: str):
    logger.info(f"開始處理訊息: {text}")
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.line_user_id == line_user_id).first()
        if not user:
            user = User(line_user_id=line_user_id)
            db.add(user); db.commit(); db.refresh(user)

        # Gemini 工具
        def add_to_watchlist(ticker: str):
            db.add(Watchlist(user_id=user.id, ticker=ticker))
            db.commit(); return f"已加入 {ticker}"
        
        def get_watchlist():
            ws = db.query(Watchlist).filter(Watchlist.user_id == user.id).all()
            return "清單: " + ", ".join([w.ticker for w in ws]) if ws else "清單為空"

        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            tools=[get_stock_price, get_stock_news, add_to_watchlist, get_watchlist],
            system_instruction="你是一位專業股票助理。請協助查詢股價或清單，並附上投資風險警語。"
        )

        # 5. 發送至 Gemini (開啟自動工具呼叫)
        chat = model.start_chat(history=[], enable_automatic_function_calling=True)
        loop = asyncio.get_event_loop()
        logger.info("呼叫 Gemini API (包含工具執行)...")
        response = await loop.run_in_executor(None, chat.send_message, text)
        
        reply_text = response.text
        logger.info(f"Gemini 回應: {reply_text}")

        async with AsyncApiClient(configuration) as api_client:
            api = AsyncMessagingApi(api_client)
            await api.reply_message(ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=reply_text)]
            ))
        logger.info("已成功回傳 LINE")
    except Exception as e:
        logger.error(f"錯誤: {str(e)}", exc_info=True)
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
