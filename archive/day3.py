#索引与切片
s="agent"
print(s[0])
print(s[4])
#print(s[5])
#负数索引
s="agent"
print(s[-4])
print(s[-5])
#切片
s="agent"
print(s[0:4])
print(s[2:5])
print(s[::-1])
print(s[::-2])
print(s[::])
print(s[::-1])
#数据清洗.strip()
a1="\thi boys and girls\t"
a2=a1.strip()
print(a1)
print(a2)
#数据清洗.replace()
aa=".....ggg\thi boys and girls fucky\t"
ab=(aa
    .replace(".....ggg","")
    .replace("fucky","hhh")
    .strip())
print(ab)
#.splitliness()和startswith()
# 原始文本（三引号包起来的多行内容）
'''text = """Thought: 今天天气不错。
Action: query_weather
Action Input: Shanghai
"""

# 第1步：拆成行
for row in text.splitlines():
    # 第2步：去掉每行首尾多余的空格和换行
    content = row.strip()
    
    # 第3步：判断这行开头是什么
    if content.startswith("Action:"):
        # 按冒号切割，取冒号后面的东西，再去掉多余空格
        order = content.split(":", 1)[1].strip()
        print(f"执行: {order}")
        
    elif content.startswith("Thought:"):
        # 按冒号切割，取冒号后面的东西
        idea = content.split(":", 1)[1].strip()
        print(f"思考: {idea}")
        
    elif content.startswith("Action Input:"):
        # 按冒号切割，取冒号后面的东西
        data = content.split(":", 1)[1].strip()
        print(f"参数: {data}")'''
day="第一天\n第二天\n第三天"
print(day
      .splitlines())

role="Action pic"
print(role.startswith("Action"))
print(role.startswith("action"))
print(role.startswith("Action",0))
print(role.startswith("Action",1))
#列表
summer_day=["hot","so hot","very hot"]
print(summer_day[0])
summer_day.append("fucking hot")
print(summer_day)
for temp in summer_day:
    print(temp)

year="365days"
for long in year:
    print(long)
    
i=["1","2","3","6"]
for o in range(10):
    print(i)
#字典
yanan={"belong":"china",#.get()
       "detail":"shanxi"}
print(yanan.get("belong"))
print(yanan.get("detail"))
print(yanan.get("belongs","timeout"))

yanan["belong"]="CN"#修改或新增数据
yanan["temp"]="cool"
print(yanan)

import json#与json互转

# 1. json.loads()：将 JSON 字符串 -> 转换为 Python 字典
json_str = '{"tool": "weather", "city": "Beijing"}'
dict_data = json.loads(json_str)

print(type(dict_data))  # <class 'dict'>
print(dict_data.get("city"))  # 输出: Beijing


# 2. json.dumps()：将 Python 字典 -> 转换为 JSON 字符串（存盘或发送网络请求时用）
new_str = json.dumps(dict_data, ensure_ascii=False, indent=2)
print(new_str)