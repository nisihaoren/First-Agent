import os
import chromadb
from chromadb.utils import embedding_functions

# 初始化 Embedding 函数（使用轻量级开源模型）
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"  # 英文模型，适合中文+英文混合，较小
)

# 初始化 ChromaDB 客户端（持久化到 ./chroma_db 目录）
client = chromadb.PersistentClient(path="./chroma_db")

# 创建或获取 collection（类似“表”）
collection_name = "shop_knowledge"
try:
    collection = client.get_collection(name=collection_name)
    # 如果已存在，清空旧数据（可选）
    client.delete_collection(collection_name)
except:
    pass
collection = client.create_collection(name=collection_name, embedding_function=embedding_fn)

# 读取 data/我的知识库.txt
knowledge_path = "data/我的知识库.txt"
if not os.path.exists(knowledge_path):
    print(f"❌ 文件 {knowledge_path} 不存在，请先准备数据。")
    exit(1)

with open(knowledge_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

ids = []
documents = []
metadatas = []

for idx, line in enumerate(lines):
    line = line.strip()
    if not line:
        continue

    parts = line.split("|")
    if len(parts) < 4:
        print(f"⚠️ 第 {idx+1} 行字段数不足，使用整行作为文档。")
        doc = line
        metadata = {
            "name": "未知店铺",
            "dish": "未知",
            "price": "未知",
            "comment": line[:30]
        }
    else:
        doc = f"店名：{parts[0]}，招牌菜：{parts[1]}，人均：{parts[2]}，评价：{parts[3]}"
        metadata = {
            "name": parts[0].replace("店名：", ""),
            "dish": parts[1].replace("招牌菜：", ""),
            "price": parts[2].replace("人均：", ""),
            "comment": parts[3].replace("评价：", "")
        }

    documents.append(doc)
    metadatas.append(metadata)
    ids.append(str(idx))

print(f"✅ 成功解析 {len(ids)} 条记录，准备入库...")