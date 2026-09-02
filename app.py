import streamlit as st
import json
import time  # 可选，用于模拟思考过程
from tools.media_tools import extract_shop_insights, generate_rednote, generate_image,generate_video_script,fetch_web_insight

st.set_page_config(page_title="成都探店 Agent", page_icon="🍲", layout="wide")

# ===== 侧边栏配置 =====
with st.sidebar:
    st.header("⚙️ 运营配置")
    temperature = st.slider("创意温度 (Temperature)", 0.0, 1.0, 0.7, 0.1)
    shop_type = st.selectbox("店铺类型预设", ["火锅", "串串", "咖啡", "茶馆", "网红店"])
    st.divider()
    st.caption("✅ API 状态：连接正常")
    st.caption("📁 知识库：已加载")

# ===== 主界面 =====
st.title("📝 成都本地生活 AI 运营助手")
st.caption("输入店铺名称或粘贴探店笔记，一键生成小红书文案与配图")

# 显示聊天历史（简单版，不加会话状态）
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史消息
with st.expander("📜 查看聊天记录", expanded=False):
     for msg in st.session_state.messages:
      with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 输入框
if prompt := st.chat_input("例如：玉林路社区火锅，排队很长..."):
    if len(prompt.strip())<2:
       with st.chat_message("assistant"):
          st.write("🤔 您输入的内容太短了，请告诉我您想了解的具体店铺或菜品。")
          st.stop()
    else:
     st.session_state.messages.append({"role": "user", "content": prompt})
     with st.chat_message("user"):
        st.write(prompt)
    if prompt.startswith("http://") or prompt.startswith("https://"):
           with st.chat_message("assistant"):
              with st.spinner("正在抓取网页内容"):
                url_content=fetch_web_insight(prompt)
              st.write(url_content)
           st.session_state.messages.append({"role": "assistant", "content": url_content})
           st.stop()
           




       # 2. 开始处理助手回复
    with st.chat_message("assistant"):
        # ① 创建状态容器（动态展示进度）
       
        with st.status("🚀 Agent 已启动，正在思考...", expanded=True) as status:

            # 第一步：提取卖点
            status.update(label="📊 步骤 1/4：正在分析店铺口碑与卖点...", state="running")
            try:
             insights=extract_shop_insights(prompt)
             obs_insights=json.dumps(insights,ensure_ascii=False, indent=2)
            except Exception as e:
                 insights = {}
                 obs_insights = f"提取失败：{e}"
                 st.error("提取卖点失败...")
            
            # 第二步：生成文案
            status.update(label="✍️ 步骤 2/4：正在构思小红书爆款文案...", state="running")
            # 从 insights 中提取店铺名（取 vibe 字段或前几个字）
            shop_name=insights.get("vibe",'成都保障店铺')[:8]if insights else prompt[:8]
            details=f"爆款菜品：{insights.get('dishes','暂无')},氛围：{insights.get('vibe','暂无')}"if insights else prompt
            rednote=generate_rednote(shop_name,details)
            obs_rednote=rednote[:200]if len(rednote)>200 else rednote
            # 第三步：生成配图（视情况，如果不想等太久，可以注释掉生图）
            status.update(label="🎨 步骤 3/4：正在生成高清配图...", state="running")
            img_prompt=f"'美食摄影',{shop_name},{insights.get('vibe')},'高清','不要有错别字'"
            img_result=generate_image(img_prompt)
            if "❌" in img_result:
             img_path = None
             obs_image = f"图片生成失败：{img_result}"
            else:
             img_path = img_result
             obs_image = f"图片已保存至 {img_path}"

            status.update(label="🎬 步骤 4/4：正在生成拍摄脚本...", state="running")
             
            script_content = "⚠️ 脚本生成失败"  # 默认值
            obs_script_preview = "生成失败"
            try:
              script_content=generate_video_script(shop_name,details)
              obs_script_content=script_content[:50] if len(script_content)>50 else script_content
            except Exception as e:
                script_content = f"⚠️ 脚本生成失败：{e}"
                obs_script_preview = "生成失败"
            
            # 标记完成
            status.update(label="✅ 任务全部完成！", state="complete")
            
        
        
        # ---------- ③ 结果渲染（直接在助手气泡里展示） ----------
        # 显示文案（Markdown 渲染）
    with st.expander("📜 查看生成内容", expanded=False):
        st.markdown("#### ✍️小红书文案")
        def stream_text(text):
         words = text.split()
         for i, word in enumerate(words):
              yield word + (" " if i < len(words) - 1 else "")
              time.sleep(0.05)
    
        st.write_stream(stream_text(rednote))
        st.divider()
        st.markdown("### 🎬 拍摄脚本")     # 脚本标题
        st.markdown(script_content)
        # 显示配图（如果有）
        if img_path and "❌" not in str(img_path):
            st.image(img_path, caption="🎨 AI 生成的配图")
        else:
            st.info("🖼️ 本次未生成配图（可能是 API 未配置或网络问题）")
        col1,col2=st.columns(2)
        with col1:
           st.download_button(
              label="📥 下载小红书文案",
              data=obs_rednote,
              file_name=f"{shop_name}_小红书文案.md",
              mime="text/markdown"
           )
        with col2:
           if script_content and "失败" not in script_content:
              st.download_button(
              label="📥 下载拍摄脚本",
              data=script_content,
              file_name=f"{shop_name}_小红书文案.md",
              mime="text/markdown"
           )
           else:
                st.warning("⚠️ 拍摄脚本未生成，无法下载")
        # ---------- ④ 折叠展示思考日志（任务二核心输出） ----------
        with st.expander("📋 查看 Agent 完整思考日志 (Thought & Observation)"):
            st.text("📌 Thought 1 (提取卖点)：")
            st.code(obs_insights,language="json")
            st.divider()
            st.text("📌 Thought 2 (生成文案)：")
            st.write(f"生成预览：{obs_rednote}")
            st.divider()
            st.text("📌 Thought 3 (生成配图)：")
            st.write(obs_image)
            st.divider()
            st.text("📌 Thought 4 (生成拍摄脚本)：")
            st.write(script_content)

        
        # ---------- ⑤ 将助手回复存入 session_state (用于历史展示) ----------
        # 存入纯文本，方便后续在循环中显示（也可以存 Markdown，但这里简化为文本）
        assistant_fully_reply=f"**生成文案:**\n{obs_rednote},**生成拍摄脚本：**\n{obs_script_content}"
        if img_path and "❌" not in str(img_path):
           assistant_fully_reply+=f"**生成配图:**{obs_image}"
        st.session_state.messages.append({"role":"assistant","content":assistant_fully_reply})
