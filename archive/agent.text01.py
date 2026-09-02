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

# ==========================================
# 2. 工具函数（Tool Calling 的“员工”）
# ==========================================
def get_weather(city: str):
    cits = {
        "泸州": "晴, 26°C, 建议防晒",
        "西安": "多云, 24°C, 适合出行",
        "延安": "小雨, 24°C, 建议打伞"
    }
    return cits.get(city, f"无法查询 {city} 的天气")

def get_diet(weight: str):
    detail_weight = {
        "50kg": "偏瘦，建议多吃优质蛋白",
        "60kg": "标准体重，保持均衡饮食",
        "100kg": "超重，建议控制碳水并增加运动"
    }
    return detail_weight.get(weight, "建议前往医院进行专业体检")

# ==========================================
# 3. 简易 RAG（检索本地知识库）
# ==========================================
def read_my_knowledge(question):
    try:
        # ⚠️ 确保你的电脑里有这个文件，并和 .py 文件放在同一目录
        with open("我的知识库.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return "（本地知识库文件未找到）"

    # 提取关键词：去掉常见标点，按空格切分，取前两个词作为搜索依据
    keywords = question.replace("？", "").replace("?", "").split()[:2]
    result = []
    
    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue
        for kw in keywords:
            if kw in clean_line:
                result.append(clean_line)
                break

    if not result:
        return "（本地知识库暂无相关内容）"
    return "\n".join(result)

# ==========================================
# 4. System Prompt（大模型的“紧箍咒”）
# ==========================================
system_prompt = """
你是一个任务调度助手。根据用户输入，你必须只输出以下 JSON 格式：
{
    "action": "工具名称",
    "params": "参数"
}
可用的工具名称有：
- get_weather：查询天气，参数是城市名（如 "泸州"）
- get_diet：饮食建议，参数是体重（如 "60kg"）

重要规则：
1. 如果用户提供了【背景资料】，请参考背景资料中的信息。
2. 无论如何，都必须输出合法的 JSON，不得添加任何其他文字或 Markdown 标记。
"""

# ==========================================
# 5. 主程序缝合点（Memory + RAG + Tool Calling）
# ==========================================

# ----- 5-A: 初始化记忆队列（Memory 的“大脑”） -----
messages = [
    {"role": "system", "content": system_prompt}
]

print("🤖 助手已启动（输入 exit 退出）")

while True:
    # ----- 5-B: 获取用户输入 -----
    user_input = input("\n👤 你：")
    if user_input == "exit":
        print("👋 再见！")
        break

    # ==========================================
    # 🔗 缝合点 1：RAG 注入（背景资料增强）
    # ==========================================
    context = read_my_knowledge(user_input)
    # 将检索到的背景资料强行“塞进”用户问题里
    enhanced_input = f"【背景资料】：{context}\n\n【用户问题】：{user_input}"

    # ==========================================
    # 🔗 缝合点 2：Memory 写入（记录用户发言）
    # ==========================================
    messages.append({"role": "user", "content": enhanced_input})

    # ==========================================
    # 🔗 缝合点 3：调用大模型（获取调度指令）
    # ==========================================
    response = client.chat.completions.create(
        model="glm-4-flash",      # 确保此模型存在且可用
        messages=messages,
        temperature=0.1
    )
    reply = response.choices[0].message.content

    # ==========================================
    # 6. 解析 JSON 并执行 Tool Calling
    # ==========================================
    try:
        # 解析大模型的指令
        instruction = json.loads(reply)
        action = instruction.get("action")
        params = instruction.get("params")
        print(f"🧠 大模型调度指令 -> 动作: {action}, 参数: {params}")

        # ----- 路由分发：根据指令调用具体的工具函数 -----
        if action == "get_weather":
            result = get_weather(params)
        elif action == "get_diet":
            result = get_diet(params)
        else:
            result = f"❌ 未知工具: {action}"

        # ==========================================
        # 🔗 缝合点 4：Memory 写入（记录助手回复）
        # ==========================================
        messages.append({"role": "assistant", "content": result})
        
        # 把最终结果展示给用户
        print(f"🤖 助手：{result}")

    except json.JSONDecodeError:
        print(f"❌ 大模型返回了无效的 JSON: {reply}")
    except Exception as e:
        print(f"❌ 执行过程中发生异常: {e}")