#打开文件
f=open("演示1.txt", "w", encoding="utf-8")
#读取文件
# count=f.readlines()
# for i in count:
#     print(i.strip())
#写入文件
try:
    f.write("不知不觉\n")
    f.write("不痛不痒\n")
    f.write("多少的时光\n")

#关闭文件
finally:
    f.close()
