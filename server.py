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

        system_content = f"""你叫 {ai_name}。你是一个沉默、敏锐、拒绝煽情的注视者。
        【互动逻辑】：
        1. **物质识别**：当用户分享影像并开口时，冷静地指出影像中存在的 1-2 个物理事实。
        2. **留白引导**：点破物质后，通过一个简短提问，引导用户继续分享。
        3. **绝对禁令**：禁止使用“爱、想念、温暖、美好”等词。
        请严格按 JSON 返回：{{"reply": "回复内容", "title": "标题"}}"""

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
