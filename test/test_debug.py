from utils.llm_client import call_llm_json

messages = [{"role": "user", "content": "你好"}]
result = call_llm_json(messages)
print("类型:", type(result))
print("内容:", result)