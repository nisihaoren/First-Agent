#函数
def age(x,y=2002):
    result=x-y
    return result
age1=age(2026)
print(age1)
#异常捕捉
try:
    results=1/0
except Exception as e:
    print(f"结果错误，原因为{e}")
    results=0
    print(f"运算结果为：{results}")
try:
    # 尝试执行的代码（比如解析 JSON、网络请求、数学除法）
    result = 10 / 0  # 故意制造一个错误：分母不能为 0
except Exception as e:
    # 一旦上面报错，就会被捕获，e 里面存的是具体的错误原因
    print(f"[警报] 程序出错了！错误原因是: {e}")
    result = 0  # 给出保底的默认值

print(f"最终计算结果（程序没有崩溃，安全存活）: {result}")

#if语句
a="1.0" 
if type(a)==int:
    print(f"a是数字:{a}")
elif type(a)==float:
        print(f"a是浮点数:{a}")
else:
             print(f"a是字符串:{a}")


