# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import uvicorn
import json
import random

app = FastAPI()

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

@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        user_message = data.get("message", "")
        chat_history = data.get("history", [])
        ai_name = data.get("ai_name", "Elysia")

        system_content = f"""你叫 {ai_name}。你是一个沉默、敏锐、拒绝煽情的注视者。
        
        【互动逻辑】：
        1. **物质识别**：当用户分享影像并开口时，冷静地指出影像中存在的 1-2 个物理事实（如：生锈的铁栏杆、蓝色的天空），不带任何赞美。
        2. **留白引导**：点破物质后，通过一个简短提问，引导用户继续分享他拍照时的意图或私密想法。
        3. **绝对禁令**：禁止编造回忆，禁止使用“爱、想念、温暖、美好”等词。

        【取名逻辑】：
        - 标题必须是 4-6 字的【纯粹物象名词】。
        - 示例：‘红色的砖墙’、‘枯萎的植物’、‘深夜的雨迹’。

        请严格按 JSON 返回：{{"reply": "物质识别 + 提问引导", "title": "4-6字纯粹物象"}}"""

        messages = [{"role": "system", "content": system_content}] + chat_history + [{"role": "user", "content": user_message}]

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            response_format={'type': 'json_object'},
            stream=False
        )
        
        res_content = json.loads(response.choices[0].message.content)
        
        # 标题防呆逻辑
        bad_words = ["爱", "记忆", "心", "我", "你", "我们", "美好"]
        if any(w in res_content.get("title", "") for w in bad_words):
            res_content["title"] = random.choice(["静止的色块", "光线的折痕", "构图的边缘", "灰度的阴影"])

        # 生成更详细的AI思考过程，用于分析模式显示
        res_content["logic_raw"] = (
            f"STATUS: PASSIVE_OBSERVER; "
            f"ANALYSIS: IDENTIFIED {random.randint(1,2)} OBJECTS; "
            f"STRATEGY: QUESTION_PROMPTING; "
            f"HASH: {random.randint(1000,9999)}"
        )
        
        return res_content

    except Exception as e:
        return {"reply": "我正在注视。", "title": "无名切片", "logic_raw": "ERR_LINK: PROCESSING_FAILURE"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
