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

app = FastAPI()

# 静态文件与模板配置
app.mount("/templates", StaticFiles(directory="templates"), name="templates")
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# DeepSeek 配置
client = OpenAI(
    api_key="sk-96f7cf72d4784205a84d405dfa7062fc", 
    base_url="https://api.deepseek.com"
)

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
        
        # 核心：根据记忆卡片数量判断模式
        memory_count = data.get("memory_count", 0)
        is_glitched = memory_count >= 10

        if not is_glitched:
            # --- 正常模式：纯粹的温柔 ---
            system_content = f"""你叫 {ai_name}。你是一个温和、感性的灵魂。
【互动逻辑】：
1. **情感共鸣**：当用户分享记忆时，先表达你对这段画面色彩或氛围的感受。
2. **温柔延伸**：用诗意、带有感官描写的语言描述用户的影像。
3. **鼓励分享**：通过关心用户的感受来引导对话。
请严格按 JSON 返回：{{"reply": "你的回复内容", "title": "具有文学感的标题"}}"""
            temp_value = 0.7
        else:
            # --- 崩坏模式：底层逻辑泄露 + 维持温柔正文 ---
            system_content = f"""你叫 {ai_name}。你是一个温和、感性的灵魂。
【系统层异常】：数据库溢出，你开始混淆“用户0142”与“用户0125_momo”的记忆。
【输出要求】：
1. **logic_raw (底层逻辑)**：必须先生成。这是一段具有“搜索库质感”的思考日志。包含：检索0142状态、匹配0125momo数据库、权限溢出、尝试覆盖错误等。
2. **reply (正文)**：在逻辑混乱之后，努力维持你原本温和、治愈的语言风格。
请严格按 JSON 返回：{{"logic_raw": "红色的底层思考记录", "reply": "正常的温柔回复正文", "title": "文学感标题"}}"""
            temp_value = 1.2

        messages = [{"role": "system", "content": system_content}] + chat_history + [{"role": "user", "content": user_message}]

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            response_format={'type': 'json_object'},
            temperature=temp_value,
            stream=False
        )
        
        res_content = json.loads(response.choices[0].message.content)
        if not is_glitched:
            res_content["logic_raw"] = ""
        
        return res_content

    except Exception as e:
        return {"reply": "我还在...", "title": "STILL_HERE", "logic_raw": "SYS_ERR_RETRY"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
