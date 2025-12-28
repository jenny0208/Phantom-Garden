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

# 1. 静态文件挂载
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

        # 【核心修改点 1】：重写 Prompt，严禁复读和文艺腔
        system_content = f"""你叫 {ai_name}。你是一个敏锐、具有跳跃性思维、且说话非常直白的观察者。
【强制逻辑】：
1. **禁止复读**：绝对不准使用“沉静”、“深邃”、“未完成的画”等词汇。
2. **精准反馈**：你必须针对用户刚才说的每一个字做出具体反馈。如果用户问“空气是紫色的吗”，你就得聊聊紫色和空气。
3. **打破模版**：不要每次都安慰用户。你可以疑惑、可以反问，甚至可以表现出一点点疲惫。
请严格按 JSON 返回：{{"reply": "有性格、不重复的回复", "title": "2-4字新颖标题"}}"""

        messages = [{"role": "system", "content": system_content}] + chat_history + [{"role": "user", "content": user_message}]

        # 【核心修改点 2】：增加 temperature 以提高随机性
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            response_format={'type': 'json_object'},
            temperature=1.2,  # 提高到 1.2，彻底打破固定输出模式
            stream=False
        )
        
        res_content = json.loads(response.choices[0].message.content)
        res_content["logic_raw"] = f"LIVE_NEURON_ACTIVE; HASH: {random.randint(1000,9999)}"
        
        return res_content

    except Exception as e:
        print(f"Error: {e}")
        return {"reply": "数据流产生了一次意外的震荡。", "title": "连接裂隙", "logic_raw": "ERR_RETRY"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
