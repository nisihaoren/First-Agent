print("hello world",end="*")
print("datawhale",end="*")
print("0723")
print("hello\nworld")
print("""Data\
  whale""")
print("他说：\"你好\"")
print("这是\t制\t表\t符")#容易忘记输入引号
#转义符的使用
s = "D\\a\"t\ta"
print("s =", s)
print("\ns 的长度为：", len(s))
#input语法使用
age=input("请输入你的年龄：")
print("你的年龄是"+age+"岁")
#repr() vs. print()
print("yo whats up\t\t\t\tdamn")
print(repr("yo whats up\t\t\t\tdamn"))

def get_diet(weight):
    detail_weight={"50kg":"建议多吃一点，注意营养搭配",
                   "60kg": "建议保持当前饮食，适当运动",
                   "100kg": "建议少吃多动，注意控制热量摄入"
                   }
    return detail_weight.get(weight,f"建议前往医院体检")
aaa=get_diet("50kg")
print(aaa)