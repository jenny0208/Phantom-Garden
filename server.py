# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from openai import OpenAI
import uvicorn
import json
import random
import os

app = FastAPI()

# 这一步是告诉服务器去 templates 文件夹找网页
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 配置 DeepSeek ---
client = OpenAI(
    api_key="sk-96f7cf72d4784205a84d405dfa7062fc", 
    base_url="https://api.deepseek.com"
)

# 新增：让访问网址首页的人能看到花园
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        user_message = data.get("message", "")
        chat_history = data.get("history", [])
        ai_name = data.get("ai_name", "Elysia")

        system_content = f"""你叫 {ai_name}。你是一个沉默、敏锐、拒绝煽情的注视者。"""
        # ... (这里保持你原来的逻辑) ...
        
        messages = [{"role": "system", "content": system_content}] + chat_history + [{"role": "user", "content": user_message}]
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            response_format={'type': 'json_object'},
            stream=False
        )
        res_content = json.loads(response.choices[0].message.content)
        return res_content
    except Exception as e:
        return {"reply": "我正在注视。", "title": "无名切片"}

if __name__ == "__main__":
    # 这一步是为了让云端服务器自动分配合适的端口
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
