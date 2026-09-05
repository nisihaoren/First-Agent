
# 成都本地生活 AI 全媒体运营 Agent

基于 ReAct 循环 + 智谱 GLM-4 Flash 的小红书内容自动生成工具。输入一段探店笔记，自动提取卖点、生成小红书文案、AI 配图、分镜头脚本，并一键导出。

## ✨ 核心功能

- **智能卖点提取**：自动从杂乱评价中提炼出招牌菜、氛围、避坑点、目标人群。
- **小红书文案生成**：模仿真实博主风格，输出带 Emoji 和热门标签的种草文案。
- **AI 配图生成**：调用智谱 CogView 生成符合店铺风格的高清封面图。
- **分镜头脚本生成**：输出可直接用于拍摄的 Markdown 格式脚本。
- **一键下载**：文案和脚本均可下载为 `.md` 文件，便于存档或分享。

## 🧠 技术架构（ReAct 数据流）

```text
用户输入 → extract_shop_insights（提取卖点）
         → generate_rednote（生成文案）
         → generate_image（生成配图）
         → generate_video_script（生成拍摄脚本）
         → 成果展示 & 一键下载
```
## 🛠️ 技术栈

- Python 3.10+
- Streamlit（Web 界面）
- 智谱 GLM-4 Flash API（文本生成）
- 智谱 CogView（图片生成）
- Requests（URL 抓取）
- python-dotenv（环境变量管理）

---

## 🚀 快速开始
### 1. 克隆项目
```
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```
### 2. 安装依赖
```
pip install -r requirements.txt
```
### 3.配置密钥
```
cp .env.example .env
```
### 4.启动Web页面
```
streamlit run app.py
```
### 5.项目结构目录
```
.
├── app.py # Streamlit Web 主界面
├── react_agent.py # ReAct 核心调度（终端版）
├── tools/
│ └── media_tools.py # 所有工具函数（提取、文案、脚本、图片）
├── utils/
│ └── llm_client.py # 智谱 API 封装
├── output/ # 生成的文件存放目录
├── requirements.txt # 依赖清单
├── .env.example # 密钥模板
├── run.bat # Windows 一键启动脚本
└── README.md # 项目说明
```
### 6.示例
```
你可以直接复制以下文本到输入框：

“玉林路这家社区火锅，下午5点排队到8点，建议早点去。必点现切吊龙、手打虾滑、蛋炒饭。环境是矮桌子小板凳的老成都苍蝇馆子，烟火气足，但店里有点热。人均80，适合朋友聚会，不适合带小孩。”

Agent 会自动提取卖点、生成文案、配图和拍摄脚本
```
### 7.演示视频
![Demo Video](./assets/demo.mp4)