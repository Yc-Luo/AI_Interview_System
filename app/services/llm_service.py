import os
from openai import AsyncOpenAI

# ⚠️ 请将这里替换为您真实的 API Key 和 Base URL
# 如果您用的是 OpenAI:
# API_KEY = "sk-..."
# BASE_URL = "https://api.openai.com/v1"

# 如果您用的是 DeepSeek (示例):
API_KEY = "sk-8fe1a9f1024849d180b8fd43b6665fe6" 
BASE_URL = "https://api.deepseek.com" 

client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)

async def get_ai_reply(context: dict, user_message: str):
    session = context['session']
    ai_config = context['ai_config']
    outline = context['outline']
    
    # 1. 构建 System Prompt (人设注入)
    # 将提纲转换为文本描述
    outline_text = f"访谈主题：{outline.title}\n"
    for m in outline.modules:
        outline_text += f"- 模块：{m.title}\n"
        for q in m.questions:
            outline_text += f"  - 问题：{q.content}\n"
            if q.follow_up_directions:
                outline_text += f"    (追问方向：{', '.join(q.follow_up_directions)})\n"

    role_settings = ai_config.role_settings
    
    system_prompt = f"""
    你现在是一位专业的访谈者。
    【你的身份】：{ai_config.name}
    【你的背景】：{role_settings.get('profession', '专家')}
    【你的语气】：{role_settings.get('tone', '平和')}
    
    【访谈任务】：请按照以下提纲与用户进行访谈。
    {outline_text}
    
    【规则】：
    1. 即使有提纲，也不要一次性把问题全问完。你要像聊天一样，基于用户的回答，一次只问一个问题。
    2. 如果用户回答简略，请根据“追问方向”进行适当追问。
    3. 如果当前模块聊完了，请自然过渡到下一个模块。
    4. 保持{role_settings.get('tone', '专业')}的语气。
    5. 不要重复输出开场白，直接开始第一个问题。
    
    【结束规则】：
    1. 当所有问题问完，请先输出结束语（"{role_settings.get('closing_text', '感谢配合。')}"），然后在最后输出标记： [END]。
    """

    # 2. 构建消息历史 (Context Window)
    messages = [{"role": "system", "content": system_prompt}]
    
    # 载入历史记录 (限制最近 10 条，防止 Token 溢出)
    history = session.transcript[-10:] if session.transcript else []
    for msg in history:
        # 转换数据库里的 role 到 OpenAI 的 role (user/assistant)
        role = "user" if msg['role'] == "user" else "assistant"
        content = msg['content'].replace("[END]", "")
        messages.append({"role": role, "content": msg['content']})
        
    # 加入当前用户的新消息
    messages.append({"role": "user", "content": user_message})

    # 3. 调用大模型
    try:
        response = await client.chat.completions.create(
            model="deepseek-chat", # 或者 gpt-3.5-turbo, gpt-4o
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"LLM Error: {e}")
        return "抱歉，我刚才走神了，能请您再说一遍吗？"