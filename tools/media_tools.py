import os
import json
import requests
import re
from datetime import datetime
from utils.llm_client import call_llm, call_llm_json, call_llm_image
from typing import Dict, Optional, Any



def search_knowledge(query: str) -> str:
    """
    模拟本地知识库查询。

    参数：
        query (str): 查询关键词（如 "春熙路"）

    返回：
        str: 查询结果文本，如果未找到则返回提示信息。
    """
    try:
        knowledge_base = {
            "春熙路": "春熙路是成都最繁华的步行街，聚集了众多老字号和网红店。",
            "玉林路": "玉林路以文艺气息和地道串串闻名。",
            "玉林路串串": "玉林路老字号串串香，人均 55 元，招牌菜是牛肉串和冒脑花，营业到凌晨 2 点，充满市井烟火气。"
        }
        return knowledge_base.get(query, f"没有关于 {query} 的资料")
    except Exception as e:
        return f"❌ search_knowledge 执行失败: {e}"


def extract_shop_insights(raw_data: str) -> Dict[str, str]:
    """
    从杂乱文本中提炼出结构化卖点。

    参数：
        raw_data (str): 包含店铺评价的长文本（网友评论、大众点评等）

    返回：
        dict: 包含 dishes, vibe, pitfalls, crowd 四个字段的字典。
              如果提取失败，返回四个字段均为 "提取失败" 的字典。
    """
    try:
        prompt = f"""
你是一位资深的美食数据分析师和探店内容策划专家。
请仔细阅读以下关于成都某家店铺的长篇描述（可能包含网友评价、游记、大众点评片段），
提炼出最具价值的核心信息，并严格按照 JSON 格式输出。

【原始材料】：
{raw_data}

【必须提取的 4 个维度（请严格按照以下 JSON 键名输出）】：
{{
    "dishes": "人均价格 / 爆款菜品（用中文逗号分隔，最多提炼 3 个，如 '人均价格，麻辣牛肉, 手打红糖糍粑'）",
    "vibe": "氛围与环境特色（一句话概括，如 '复古市井风，适合拍照打卡'）",
    "pitfalls": "真实避坑点 / 争议（用中文逗号分隔，如 '排队超1小时, 口味偏辣'，如果没有就写'无明显坑点'）",
    "crowd": "目标客群画像（一句话概括，如 '年轻情侣, 游客打卡, 深夜夜宵党'）"
}}

【输出要求】：
1. 只输出纯 JSON，不要添加任何额外的解释、Markdown 标记或文字。
2. 确保 JSON 是合法的（键名和字符串值都用双引号包裹）。
3. 如果原文中没有提到某个维度，就用 "暂无数据" 或 "无明显坑点" 填充。
"""
        messages = [{"role": "user", "content": prompt}]
        result = call_llm_json(messages, model="glm-4-flash", temperature=0.8)
        
        # 如果 call_llm_json 返回空字典，说明解析失败，给兜底值
        if not result:
            return {
                "dishes": "提取失败",
                "vibe": "提取失败",
                "pitfalls": "提取失败",
                "crowd": "提取失败"
            }
        return result
    except Exception as e:
        return {
            "dishes": f"提取异常: {e}",
            "vibe": f"提取异常: {e}",
            "pitfalls": f"提取异常: {e}",
            "crowd": f"提取异常: {e}"
        }



def generate_rednote(shop: str, detail: str) -> str:
    """
    根据店铺名称和详细信息，生成小红书探店文案。

    参数：
        shop (str): 店铺名称
        detail (str): 详细信息，可以是原始文本或 JSON 字符串

    返回：
        str: 纯文本小红书文案。如果失败，返回错误描述。
    """
    try:
        # 如果 detail 是 JSON 字符串，先解析再拼成自然语言
        if detail.strip().startswith("{"):
            data = json.loads(detail)
            detail = f"爆款菜品：{data.get('dishes', '暂无')}。氛围特色：{data.get('vibe', '暂无')}。避坑提示：{data.get('pitfalls', '暂无')}。适合人群：{data.get('crowd', '暂无')}。"

        prompt = f"""
你是一位成都本地的资深探店博主，精通小红书爆款笔记的写法。
请根据以下店铺信息，写一篇不超过 200 字的高质量种草文案。

【店铺名称】:{shop}
【详细信息】:{detail}

【写作要求（必须严格遵守）】：
1. 标题：必须吸睛，包含 2-3 个 Emoji(如 🔥、✨、💰）。
2. 开头：用“黄金 3 秒”痛点或场景切入。
3. 正文（必须包含这 3 个要素）：
   - 人均消费（直接写数字)。
   - 招牌菜或必点单品（至少提 1-2 个）。
   - 环境或氛围描述。
4. 结尾：自动带上 3-5 个成都本地热门标签。

【输出格式】：直接输出文案内容，不要包含“标题：”、“正文：”这类前缀，也不要输出任何额外的解释或 Markdown 标记。
"""
        messages = [{"role": "user", "content": prompt}]
        return call_llm(messages, model="glm-4.7-flash", temperature=0.7)
    except Exception as e:
        return f"❌ generate_rednote 执行失败: {e}"


def generate_video_script(shop: str, detail: str) -> str:
    """
    根据店铺名称和详细信息，生成短视频拍摄脚本（Markdown 格式）。

    参数：
        shop (str): 店铺名称
        detail (str): 详细信息，可以是原始文本或 JSON 字符串

    返回：
        str: Markdown 格式的脚本文本。如果失败，返回错误描述。
    """
    try:
        if detail.strip().startswith("{"):
            data = json.loads(detail)
            detail = f"爆款菜品：{data.get('dishes', '暂无')}。氛围特色：{data.get('vibe', '暂无')}。避坑提示：{data.get('pitfalls', '暂无')}。适合人群：{data.get('crowd', '暂无')}。"

        prompt = f"""
你是一位资深短视频导演和美食摄影师，擅长将探店文案或店铺信息拆解为极具画面感的分镜头脚本。
请根据以下店铺信息，生成一份包含 **4-6 个镜头** 的专业拍摄脚本，总时长控制在 25-30 秒。

【店铺名称】：{shop}
【详细信息】：{detail}

【必须严格遵守的格式要求】：
请直接输出以下格式的 Markdown 文本，不要包含任何额外的解释、前缀或 Markdown 代码块标记（如 ```）。

# 🎬 分镜头拍摄脚本 - {shop}

## 镜头 1 [0-3s]
- **景别与运镜**：（例如：特写 / 固定镜头 或 全景 / 缓慢推近）
- **画面描述**：（描述画面中具体的视觉元素，如：筷子夹起裹满红油的牛肉，热气升腾）
- **口播旁白**：（写具体台词，如：在成都，没有一顿串串解决不了的事！）
- **音效/BGM 建议**：（例如：滋滋油爆声 + 欢快卡点音乐）

## 镜头 2 [3-6s]
...

（以此类推，直到写完 4-6 个镜头）

【核心创作原则】：
1.  **第一镜（黄金 3 秒）**：必须有视觉冲击力极强的特写（油泼辣子、热气、食材入锅）。
2.  **中段镜头**：展示环境（烟火气/文艺风）和用餐互动（拿串、蘸料）。
3.  **结尾镜头**：展示整体满桌美食或食客满足的特写，并定格。
4.  时长标注要连续（如 [0-3s], [3-6s], [6-10s]...）。
"""
        messages = [{"role": "user", "content": prompt}]
        return call_llm(messages, model="glm-4.7-flash", temperature=0.8)
    except Exception as e:
        return f"❌ generate_video_script 执行失败: {e}"

def generate_image(prompt: str, model: str = "glm-image") -> str:
    """
    根据提示词生成图片并保存到本地。

    参数：
        prompt (str): 生图提示词（自然语言描述）
        model (str): 生图模型名，默认 "glm-4.6v"

    返回：
        str: 本地保存路径（成功）或错误描述（失败）
    """
    try:
        print(f"🎨 正在生成图片：{prompt[:20]}...")
        image_url = call_llm_image(prompt, model=model)
        if not image_url:
            return "❌ 图片生成失败，请检查提示词或网络连接"

        # 准备保存路径
        save_dir = "output/images"
        os.makedirs(save_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_{timestamp}.jpg"
        file_path = os.path.join(save_dir, filename)

        # 下载图片
        print(f"⏳ 正在下载图片...")
        response = requests.get(image_url, timeout=15)
        response.raise_for_status()
        with open(file_path, "wb") as f:
            f.write(response.content)

        print(f"✅ 图片已保存：{file_path}")
        return file_path
    except Exception as e:
        return f"❌ generate_image 执行失败: {e}"
    
def fetch_web_insight(url:str)->dict:
    """
    抓取指定网页上面的信息，并调用extract_shop_insights提取网页信息中的卖点
    参数：
    url：用户发来的网址
    返回：
    dict主要包括dishes, vibe, pitfalls, crowd 的字典，如果失败则返回错误信息字典。
    """

    try:
        headers= {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response=requests.get(url,headers=headers,timeout=10)
        response.raise_for_status() 

        raw_text=response.text
        # 去掉 <script> 和 <style> 块
        raw_text = re.sub(r'<script.*?>.*?</script>', '', raw_text, flags=re.DOTALL)
        raw_text = re.sub(r'<style.*?>.*?</style>', '', raw_text, flags=re.DOTALL)
        # 去掉所有 HTML 标签
        raw_text = re.sub(r'<[^>]+>', '', raw_text)
        # 把多个换行/空格压缩成单个
        raw_text = re.sub(r'\s+', ' ', raw_text).strip()

        if len(raw_text) < 50:
            return {
                "dishes": "抓取失败",
                "vibe": "页面内容过短，可能需登录或动态加载",
                "pitfalls": "暂无数据",
                "crowd": "暂无数据"
            }
        result=extract_shop_insights(raw_text)
        return result
    except requests.exceptions.RequestException as e:
        return {
            "dishes": f"网络请求失败",
            "vibe": "暂无数据",
            "pitfalls": "暂无数据",
            "crowd": "暂无数据"
        }
    except Exception as e:
        return {
            "dishes": f"处理失败",
            "vibe": "暂无数据",
            "pitfalls": "暂无数据",
            "crowd": "暂无数据"
        }