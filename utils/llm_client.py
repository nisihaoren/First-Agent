import os
import json
from zai import ZhipuAiClient
from dotenv import load_dotenv

# ==========================================
# 1. 初始化（配置密钥和客户端）
# ==========================================
load_dotenv()
api_key = os.getenv("ZHIPU_API_KEY")
if not api_key:
    raise ValueError("请在 .env 文件中配置 ZHIPU_API_KEY")
client = ZhipuAiClient(api_key=api_key)

def call_llm(messages, model="glm-4.7-flash", temperature=0.7):
    try:
     response=client.chat.completions.create(
        messages=messages,
         model=model,
         temperature=temperature
)
     return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ LLM 调用失败: {e}")
        return ""
    
def call_llm_json(messages, model="glm-4.7-flash", temperature=0.7):
   raw=call_llm(messages, model, temperature)
   try:
        return json.loads(raw)
   except json.JSONDecodeError:
    print(f"⚠️ 格式错误，原始内容: {raw}")
    return None
   
def call_llm_image(prompt,model="glm-image"):
  try:
   response=client.images.generations(
      prompt=prompt,
      model=model,
      n=1,
   )
   image_url = response.data[0].url
   return image_url
  except Exception as e:
        print(f"⚠️ 图片生成失败: {e}")
        return None