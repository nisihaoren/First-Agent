import os
from dotenv import load_dotenv
from zai import ZhipuAiClient   # 注意：我猜测你的导入应该是 ZhipuAiClient（看你的报错信息里是 zai）

# 1. 加载 .env 文件中的环境变量
load_dotenv()

# 2. 从环境变量读取 API Key（如果找不到则返回 None，建议检查）
api_key = os.getenv("ZHIPU_API_KEY")
if not api_key:
    raise ValueError("请在 .env 文件中设置 ZHIPU_API_KEY")

# 4. 初始化客户端
client = ZhipuAiClient(api_key=api_key)   # 注意类名是否正确

# 5. 发送请求
response = client.chat.completions.create(
    model="glm-4.7-flash",          # 建议用免费且快速的模型，你写的 "g1m-5.2" 可能拼错了？
    messages=[
        {"role": "system", "content": "您是一个有用的AI助手。"},
        {"role": "user", "content": "您好，请用文言文介绍一下自己。"}
    ],
    temperature=1.0               # 温度参数要放这里
)

# 6. 打印回复
print(response.choices[0].message.content)





    if raw_reply is None:
       print("内容格式错误")

       messages.append({"role":"user",
                        "content":f"错误内容：你上一轮返回的内容不是合法的 JSON 格式,无论你最后输出的内容是什么，你必须按照{{'Thought': ,'Action': ,'Action Input':, 'Final Answer': }}的json格式重新输出内容。"
                        })
       continue

    print("🔍 大模型原始返回:", raw_reply)          # 看整个字典
    print("🔍 Action 字段内容:", raw_reply.get("Action"))
    print("🔍 Thought 字段内容:", raw_reply.get("Thought"))


    action=reply.get("Action")
    action_input=reply.get("Action Input")
    thought=reply.get("Thought")

    if action=="Finish":
        final_answer = reply.get("Final Answer", thought)
        print(f"任务已完成")
        print(f"输出结果为{final_answer}")
        break
    if not action_input:
     observation = "错误：工具参数为空，请重新提供有效的参数。"
    else:
     if action in ["generate_rednote","generate_video_script"]:
        param1,param2=parse_tool_params(action_input)
        if param1 and param2:
           if action=="generate_rednote":
              observation=generate_rednote(param1,param2)
           else:
              script_content=generate_video_script(param1,param2)
              os.makedirs("output",exist_ok=True)
              safe_name=param1,param2.replace("\\","_").replace("/","_")
              flie_name=f"output/{safe_name}_分镜头脚本.md"
              with open (flie_name,"w",encoding="utf-8") as f:
               f.write(script_content)
              observation=f"脚本已生成保存至{flie_name}\n\n{script_content}" 
        else:
          observation=f"参数格式错误，请用 '店铺名|详细信息' 格式"

     elif action=="search_knowledge":
        observation=search_knowledge(action_input)
     elif action=="extract_shop_insights":
        raw_result=extract_shop_insights(action_input)
        import json
        observation = json.dumps(raw_result, ensure_ascii=False, indent=2)
     elif action=="generate_image":
        observation=generate_image(action_input)
     else:
        observation=f"工具错误:{action},请输入正确的工具名称"

    print(f"📖 观察结果: {observation}")

    messages.append({"role":"assistant",
                     "content":f"思考:{thought},\nAction:{action},\ninput={action_input}"})
    messages.append({"role":"user",
                     "content":f"Observation:{observation},\n请根据观察结果继续思考,如果任务已完成,Action 返回 Finish。如果还需要更多信息,请继续调用工具。"})
    
    if step>=max_steps:
        print(f"已达到最大循环次数")