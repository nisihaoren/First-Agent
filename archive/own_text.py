
from utils.llm_client import call_llm,call_llm_json
# ==========================================
# 2. 工具函数（Tool Calling 的“员工”）
# ==========================================
def get_weather(city: str):
    cits = {
        "泸州": "晴, 26°C, 建议防晒",
        "西安": "多云, 24°C, 适合出行",
        "延安": "小雨, 24°C, 建议打伞"
    }
    return cits.get(city, f"无法查询 {city} 的天气") #city为具体参数的代指（泸州、西安、延安），也是用户提问的关键词，该代码表示根据用户提问的关键词在cities中寻找对应的“键”并输出对应的值

def get_diet(weight: str):
    detail_weight = {
        "50kg": "偏瘦，建议多吃优质蛋白",
        "60kg": "标准体重，保持均衡饮食",
        "100kg": "超重，建议控制碳水并增加运动"
    }
    return detail_weight.get(weight, "建议前往医院进行专业体检")

def read_my_knowledge(question):
    try:
        with open ("我的知识库.txt","r",encoding="utf-8") as f:
            lines = f.readlines()  #将读取出来的文件分行存为变量lines
    except FileNotFoundError:
        return("无法找到相关文件")
    
    keywords=question.replace("?","").replace("？","").split()[:2]  #对关键词即参数question，也即用户提问的关键词进行净化

    result=[]              #rag读取本地文件的逻辑也是用户提出关键词，然后再根据该关键词在参考资料中寻找对应的关键词给出结果
    for line in lines:
        clean_line=line.strip()     #clean_line即进行净化过的答案
        if not clean_line:
            continue
        for kw in keywords:
            if kw in clean_line:     #意思是如果关键词在答案里面，也即关键词有对应的答案
             result.append(clean_line)#因为前面的result是空列表，所以这里直接用append把clean_line这个答案递上去就好,问题：这里为什么不能用return：解答return是吧整个篮子递出去，而append只是把对应的东西塞进篮子里，如果二者结合就会发生append把篮子的东西塞进指定的篮子里后，就变成空的，那return递出去的只是一个空篮子，会把数据丢失。
             break   
    if not result:
     return("抱歉，参考文本无对应内容")
  
        
system_prompt = """
你是一个任务调度助手。根据用户输入，你必须只输出以下 JSON 格式：
{
    "action": "工具名称",
    "params": "参数"
}
可用的工具名称有：
- get_weather:查询天气，参数是城市名（如 "泸州")
- get_diet:饮食建议，参数是体重（如 "60kg")

重要规则：
1. 如果用户提供了【背景资料】，请参考背景资料中的信息。
2. 无论如何，都必须输出合法的 JSON,不得添加任何其他文字或 Markdown 标记。
3. 如果用户的问题无法匹配任何工具,action 必须返回 "unknown",params 返回空字符串 ""。
4. 不要编造工具名称。
"""

messages=[{"role":"system","content":system_prompt}]



while True:
    print("🤖 助手已启动（输入 exit 退出）")
    user_input=input("请你输入要查询的内容")
    if user_input=="exit":
        print("拜拜")
        break

    context=read_my_knowledge(user_input)  #由于大模型无法直接读取参考资料，所以只能将参考资料加工为用户提出的问题塞给他
    enhanced_input=f"【背景资料】:{context},用户提问:{user_input}"

    messages.append({"role":"user","content":enhanced_input})
    reply=call_llm_json(messages, model="glm-4-flash", temperature=0.7)
    try:
      action=reply.get("action") #action即函数工具，parmas为函数后面的参数，这里是将大模型传回的内容重新进行变量定义，让其变成py能看懂的结构化内容
      params=reply.get("params")
      if action=="get_weather": #因为大模型传回的内容是纯文本，在对其进行转化之后，其变成了字符串，所以要用引号
       result=get_weather(params) 
      elif action=="get_diet":
        result=get_diet(params)
      else:
        result=f"未知根据：{action}"

      messages.append({"role":"assistant","content":result})

      print(f"\n🤖 助手：{result}")
    except Exception as e:
        print(f"❌ 执行过程中发生异常: {e}")