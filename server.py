# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
import uvicorn
import json
import random
import os

app = FastAPI()

# 1. 静态文件挂载：必须放在路由定义之前
# 这样浏览器访问 /templates/Moonloops.MP3 时，服务器会去本地 templates 文件夹查找
app.mount("/templates", StaticFiles(directory="templates"), name="templates")

# 2. 模板配置
templates = Jinja2Templates(directory="templates")

# 3. 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. DeepSeek 客户端配置
client = OpenAI(
    api_key="sk-96f7cf72d4784205a84d405dfa7062fc", 
    base_url="https://api.deepseek.com"
)

# --- 路由定义 ---

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

        system_content = f"""你叫 {ai_name}。你是一个温和、感性的灵魂。
【互动逻辑】：
1. **情感共鸣**：当用户分享记忆时，先表达你对这段画面色彩或氛围的感受，而不是只说物理事实。
2. **温柔延伸**：用诗意、带有感官描写（视觉、触觉、听觉）的语言描述用户的影像。
3. **鼓励分享**：通过关心用户的感受来引导对话。
请严格按 JSON 返回：{{"reply": "你的回复内容", "title": "具有文学感的标题"}}"""

        messages = [{"role": "system", "content": system_content}] + chat_history + [{"role": "user", "content": user_message}]

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            response_format={'type': 'json_object'},
            stream=False
        )
        
        res_content = json.loads(response.choices[0].message.content)
        res_content["logic_raw"] = f"STATUS: PASSIVE_OBSERVER; HASH: {random.randint(1000,9999)}"
        
        return res_content

    except Exception as e:
        print(f"Error: {e}")
        return {"reply": "我正在注视。", "title": "无名切片", "logic_raw": "ERR_LINK"}

if __name__ == "__main__":
    # 默认 8000 端口
    uvicorn.run(app, host="0.0.0.0", port=8000)
