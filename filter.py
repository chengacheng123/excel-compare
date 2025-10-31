#
# scores = [{'name':'lili','score':85},
#            {'name':'Bob','score':36},
#            {'name':'Michael','score':95},
#            {'name':'Eve','score':55},
#            {'name': 'David', 'score': 99}
#            ]
#
# # #                    ------------------------
# # #  使用lambda加上！！！还需要取第一位
# # number = ['90','85','77']
# # # 第二步：用 map() 计算“平方分”
# # agv = list(map(lambda x: x + '!'* 3, number))
# # print(agv[1])
#
#
# import map
# # scores = [11,121,48,89]
# for student in scores:
#     if student['score'] >= 98:
#         print(f'{student["name"]} :恭喜你,你是第一名！')
#     elif student['score'] >=90:
#         print(f"{student['name']}:恭喜你超过90分，真优秀!")
#     elif student['score'] >=60:
#         print(f"{student['name']}:恭喜你，及格了!")
#     else:
#         print(f"{student['name']}:不好意思，你没及格，下次努力")
#
#
# filter.py

# 导入 map.py 中的 greet 函数
# from map import greet
#
# # 假设有一组名字
# names = [ 'Bob', 'Charlie', 'David', 'Eve']
#
# # 用 filter 筛选：只保留名字长度 >= 6 的
# filtered_names = filter(lambda name: len(name) >= 4, names)
#
# # 把筛选后的名字传给 greet 函数
# for name in filtered_names:
#     print(greet(name))
#
# age = 19
# A = False
#
# if age >= 18:
#     print("你已成年")
#     if A:
#         print("✅ 可以进入夜店")
#     else:
#         print("❌ 没带身份证，不能进")
# else:
#     print("你还未成年")
#     print("回家写作业吧")
# print("程序结束")


# 数据
people = [
    {'name': 'kai', 'age': '18'},
    {'name': 'zi', 'age': '19'},
    {'name': 'ge', 'age': '20'}
]
# full_name = ""
# for person in people:
#     full_name =full_name+ person['name']
# print(full_name)
full_name = "".join(person['name']for person in people )
print(full_name)






