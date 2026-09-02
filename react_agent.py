import os
import requests
import json
from datetime import datetime
from utils.llm_client import call_llm,call_llm_json,call_llm_image
# react_agent.py 顶部
from tools.media_tools import (
    search_knowledge,
    extract_shop_insights,
    generate_rednote,
    generate_video_script,
    generate_image,
    fetch_web_insight
)
def parse_tool_params(raw_input:str):
   if not raw_input:
      return None,None
   if "|" in raw_input:
         parts=raw_input.split("|")
   elif "," in raw_input:
           parts=raw_input.split(",")
   else:
           parts=raw_input.split("，")
   if len(parts)>=2:
      return parts[0].strip(),parts[1].strip()
   else:
      return parts[0].strip(),None

system_prompt = """
你是一个任务调度助手。你每次输出的内容**必须**是以下 JSON 格式。除了这个 JSON，绝对不允许输出任何额外的文字、解释或 Markdown 标记。
{
    "Thought": "你当前对用户问题的思考过程（中文）",
    "Action": "工具名称 或 Finish",
    "Action Input": "传给工具的参数",
    "Final Answer": "仅在 Action 为 Finish 时，填上最终回答用户的内容"
}

可用的工具名称有（你只能从这里面选）：
- fetch_web_insight:抓取指定网页内容，参数为url
- search_knowledge：查询本地知识库，参数是关键词（如 "春熙路"）
- generate_rednote：生成小红书探店文案，参数必须用 "|" 分隔店铺名和详细信息，例如 "玉林路串串|人均55，牛肉串好吃"
- generate_video_script:生成小红书短视频拍摄脚本，参数必须用 "|" 分隔店铺名和详细信息，例如 "玉林路串串|人均55，牛肉串好吃"
- extract_shop_insights：分析用户提供的大段长文本（超过50字），提炼出结构化卖点（JSON格式），参数是原始长文本本身。
- generate_image:输入必须是纯文本生图提示词，不要包含 `#` 标签或 Emoji。根据用户给出的prompt生成相应的图片，图片要清晰，不要有明显的错别字。
【核心工作流指引（非常重要！）】：
1.如果用户发来一段网址，在第一轮你必须调用fetch_web_insight对网页内容进行抓取，再将抓取的内容传给extract_shop_insights
2. 如果用户直接给你一段很长的文字（超过 50 字），请你**第一轮**必须调用 extract_shop_insights 来分析它。
3. 拿到 extract_shop_insights 返回的 JSON 结果后，请在下一轮把这份结果（特别是 dishes、vibe 等字段）作为 "详细信息"，传给 generate_rednote 或 generate_video_script。
4. 重要：拿到文案后，必须调用 generate_image，用文案内容作为生图提示词。
5. 如果用户只输入了简短的地名（如"玉林路"），你可以直接调用 search_knowledge，或者根据记忆直接写文案。
6. 重要：生成图片后，第四轮必须调用 generate_video_script，用文案内容作为脚本素材，生成拍摄脚本
7. 生成视频拍摄脚本后，必须调用 Finish 输出最终结果。
规则：
1. 如果任务还没有完成，你必须选择一个工具并填写 Action Input，Final Answer 留空。
2. 如果你认为任务已经完成，Action 必须返回 "Finish"，Final Answer 必须填写最终回答用户的内容（不要只写“任务完成”），Action Input 返回空字符串。
3. 绝对不要编造工具名称。
- 不允许在生成文案之前调用 generate_image。
- 不允许在生成文案之前调用 generate_video_script。
- 不允许跳过某个工具。
4. generate_rednote 和 generate_video_script 的 Action Input 只接受 "店铺名|详细信息"，不要把完整文案塞进去,其中 "详细信息" 应该是一个完整的自然语言段落（或者直接复制上一轮 `extract_shop_insights` 返回的整个 JSON 字符串），**绝对不要**把 JSON 的每个字段拆开用 `|` 分隔。
5. 当你调用 `Finish` 时，请把前面 `Observation` 中生成的文案或脚本内容，完整填入 `Final Answer` 中。
重要：你必须始终以 JSON 格式输出，即使你只是回复一句“好的”，也要把它放在 JSON 的 Thought 字段里。
【禁止事项】：
- 严禁在 JSON 外面写“思考：”这样的内容。
- 严禁在 JSON 外面写任何文字。
- 严禁在 JSON 里面使用中文冒号“：”作为键。
- 严禁在一轮中输出多个 Action。
- 严禁在 Action Input 中包含 JSON 格式以外的额外参数（例如“Action:generate_video_script”和“Action:generate_rednote”同时出现在同一轮）。
"""

messages=[{"role":"system","content":system_prompt}]

user_input=input(f"请输入您要查询的内容：")
messages.append({"role":"user","content":user_input})

max_steps=8
step=0

execution_tracker={
   "steps":[],
   "files":[],
   "urls":[]
}
while step<max_steps:
    step+=1
    print(f"开始第{step}轮思考")

    reply=call_llm_json(messages, model="glm-4-flash", temperature=0.7)

    if reply is None:
       print("内容格式错误")

       messages.append({"role":"user",
                        "content":f"错误内容：你上一轮返回的内容不是合法的 JSON 格式,无论你最后输出的内容是什么，你必须按照{{'Thought': ,'Action': ,'Action Input':, 'Final Answer': }}的json格式重新输出内容。"
                        })
       continue
    
    
    print("🔍 大模型原始返回:", reply)          # 看整个字典
    print("🔍 Action 字段内容:", reply.get("Action"))
    print("🔍 Thought 字段内容:", reply.get("Thought"))


    action=reply.get("Action")
    action_input=reply.get("Action Input")
    thought=reply.get("Thought")

    if action=="Finish":
        final_answer = reply.get("Final Answer", thought)
        print("\n📦 交付物清单")
        print(f"轮次: {len(execution_tracker['steps'])}")
        for s in execution_tracker["steps"]:
         icon = "✅" if s["status"] == "成功" else "❌"
         print(f"  {s['action']} {icon}")

        if execution_tracker.get("files"):
         print("文件:", ", ".join(execution_tracker["files"]))

# 兼容两种键名：优先用 image_urls，若无则用 urls
        urls = execution_tracker.get("image_urls") or execution_tracker.get("urls")
        if urls:
         print("图片URL:", ", ".join(urls))
         print("最终结果:", final_answer)
        break
    if not action_input:
     observation = "错误：工具参数为空，请重新提供有效的参数。"
    else:
     if action in ["generate_rednote","generate_video_script"]:
        param1,param2=parse_tool_params(action_input)
        if param1 and param2:
           if action=="generate_rednote":
              observation=generate_rednote(param1,param2)
              execution_tracker["steps"].append({
            "round": step,
            "action": action,
            "status": "成功",
            "detail": f"店铺：{param1}"
        })
           else:
              script_content=generate_video_script(param1,param2)
              os.makedirs("output",exist_ok=True)
              safe_name = str(param1).replace("\\", "_").replace("/", "_")
              flie_name=f"output/{safe_name}_分镜头脚本.md"
              with open (flie_name,"w",encoding="utf-8") as f:
               f.write(script_content)
              observation=f"脚本已生成保存至{flie_name}\n\n{script_content}" 
              execution_tracker["steps"].append({
                "round": step,
                "action": action,
                "status": "成功",
                "detail": f"脚本已保存"
        })
              execution_tracker["files"].append(flie_name)

        else:
          observation=f"参数格式错误，请用 '店铺名|详细信息' 格式"

     elif action=="search_knowledge":
        observation=search_knowledge(action_input)
        execution_tracker["steps"].append({
        "round": step,
        "action": action,
        "status": "成功",
        "detail": f"查询关键词：{action_input}"
    })
     elif action=="extract_shop_insights":
        raw_result=extract_shop_insights(action_input)
        import json
        observation = json.dumps(raw_result, ensure_ascii=False, indent=2)
        execution_tracker["steps"].append({
        "round": step,
        "action": action,
        "status": "成功",
        "detail": f"提取了 {len(raw_result)} 个字段"
    })

     elif action=="generate_image":
        observation=generate_image(action_input)
        execution_tracker["steps"].append({
            "round": step,
            "action": action,
            "status": "成功",
            "detail": "图片已生成"
        })
        execution_tracker["files"].append(observation)
     elif action=="fetch_web_insight":
        raw_result=fetch_web_insight(action_input)
        observation=json.dumps(raw_result,ensure_ascii=False, indent=2)
        execution_tracker["steps"].append({
        "round": step,
        "action": action,
        "status": "成功",
        "detail": f"已抓取网页：{action_input[:30]}"
    })
     else:
        observation=f"工具错误:{action},请输入正确的工具名称"

    print(f"📖 观察结果: {observation}")

    messages.append({"role":"assistant",
                     "content": json.dumps(reply, ensure_ascii=False)}) #让大模型在下一轮中记得自己之前说过什么，它不会覆盖之前的message内容，比如：messages.append({"role":"user","content":user_input})
    messages.append({"role":"user",
                     "content":f"Observation:{observation},\n请根据观察结果继续思考,如果任务已完成,Action 返回 Finish。如果还需要更多信息,请继续调用工具。"})
    
    if step>=max_steps:
        print(f"已达到最大循环次数")