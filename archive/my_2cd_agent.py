import os
import json
from zai import  ZhipuAiClient
from dotenv import load_dotenv

load_dotenv()
api_key=os.getenv("ZHIPU_API_KEY")
if not api_key:
    raise ValueError("请在.env文件中创建api_key")
client=ZhipuAiClient(api_key=api_key)

messages=[{"role":"system","content":"你是一个聪明并且耐心的智能助手"}]

while True:
    user_input=input("holle")
    if user_input=="exit":
     print(f"很高兴认识你")
     break

messages.append({"role":"user","content":"你好"})

if len(messages)>10:
   messages=messages[:1]+messages[-6:]

response=client.chat.completions.create(
    model="glm-4.5-air",
    messages=messages,
    temperature=0.7
)

ai_reply=response.choices[0].message.content

messages.append({"role":"assistant","content":"你好,很高兴认识你"})

print(f"{ai_reply}")