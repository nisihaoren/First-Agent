import os
import json
from zai import ZhipuAiClient
from dotenv import load_dotenv

load_dotenv()
api_key=os.getenv("ZHIPU_API_KEY")
if not api_key:
    raise ValueError("请在.env文件中配置ZHIPU_API_KEY")
client=ZhipuAiClient(api_key=api_key)
def get_weather(city:str):
    cits={"泸州":"晴,气温26摄氏度,建议防晒",
         "西安":"多云,气温24摄氏度,建议防晒",
         "延安":"小雨,气温24摄氏度,建议打伞"
         }
    return cits.get(city,f"展示无法查询{city}信息")
def get_diet(weight):
    detail_weight={"50kg":"建议多吃一点，注意营养搭配",
                   "60kg": "建议保持当前饮食，适当运动",
                   "100kg": "建议少吃多动，注意控制热量摄入"
                   }
    return detail_weight.get(weight,f"建议前往医院体检")

system_prompt="""
你是一个专门用来进行信息提取和提供建议的工具助手
你必须严格按照以下json格式输出,不得添加其他文字、解释和markdown标记:
{
    "action":"工具名称",
    "params":"参数"
}
以下是可以使用的工具：
get_weather:查询天气,参数是具体的城市,如:泸州,你要提供具体的天气情况并给出建议
get_diet:饮食建议,参数是具体的体重,如:50kg,你要根据具体的体重提供饮食建议
"""
user_input=input("请输入你要查询的信息")

response=client.chat.completions.create(
    model="glm-4.5-air",
    messages=[
        {"role":"system","content":system_prompt},
        {"role":"user","content":user_input}],
    temperature=0.1
)

reply=response.choices[0].message.content

try:
    clean_reply=json.loads(reply)
    action=clean_reply.get("action")
    params=clean_reply.get("params")
    if action=="get_weather":
        result=get_weather(params)
    elif action=="get_diet":
        result=get_diet(params)
    print(f"执行结果为:{result}")
except json.JSONDecodeError as e:
    print(f"\n模型返回错误json类型,错误:{e}")
