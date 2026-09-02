#数据类型
a=1
b=1.0
c="1.0"
d=5>4
print("a的数据类型是",type(a))
print("b的数据类型是",type(b))
print("c的数据类型是",type(c))
print("d的数据类型是",type(d))
#运算符
import math
print(5==5)
print(5!=5)
print(-1//3)
#运算符与数据类型
a1=5
a2="个苹果"
print(str(a1)+a2)
print(f"{a1}{a2}")
print(f"{a1*a2}")
#短路
#type() vs isinstance()
x=1
print(type(x)==int or type(x)==bool)
print(isinstance(x,(int,bool)))