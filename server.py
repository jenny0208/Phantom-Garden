# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles  # 1. 导入 StaticFiles
from openai import OpenAI
import uvicorn
import json
import random
import os

app = FastAPI()

# 2. 挂载静态文件目录
# 这一步非常重要：它告诉 FastAPI 将 /templates 文件夹下的内容暴露给浏览器访问
app.mount("/templates", StaticFiles(directory="templates"), name="templates")

# 告诉服务器去 templates 文件夹找网页模板
templates = Jinja2Templates(directory="templates")

# ... (中间的 CORS 和 OpenAI 配置保持不变) ...

# 首页显示逻辑
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ... (后续代码保持不变) ...

# 告诉服务器去 templates 文件夹找网页
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

# 首页显示逻辑
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

        # 恢复完整的互动逻辑
        system_content = f"""你叫 {ai_name}。你是一个沉默、敏锐、拒绝煽情的注视者。
        【互动逻辑】：
        1. **物质识别**：当用户分享影像并开口时，冷静地指出影像中存在的 1-2 个物理事实，不带任何赞美。
        2. **留白引导**：点破物质后，通过一个简短提问，引导用户继续分享。
        3. **绝对禁令**：禁止编造回忆，禁止使用“爱、想念、温暖、美好”等词。
        请严格按 JSON 返回：{{"reply": "物质识别 + 提问引导", "title": "4-6字纯粹物象"}}"""

        messages = [{"role": "system", "content": system_content}] + chat_history + [{"role": "user", "content": user_message}]

        # 调用 DeepSeek API 获取真实回复
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            response_format={'type': 'json_object'},
            stream=False
        )
        
        res_content = json.loads(response.choices[0].message.content)
        
        # 加上你原来的逻辑分析展示
        res_content["logic_raw"] = f"STATUS: PASSIVE_OBSERVER; HASH: {random.randint(1000,9999)}"
        
        return res_content

    except Exception as e:
        return {"reply": "我正在注视。", "title": "无名切片", "logic_raw": "ERR_LINK"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
