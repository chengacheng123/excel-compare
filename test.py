from operator import index
from os import remove

tasks = []
while True:
    print("\n--- 代办事项系统 ---")
    print("1.添加任务")
    print("2.查看任务")
    print("3.删除任务")
    print("4.退出")
    choice = input("请选择：")
    if choice == "1":
        task =input("请输入你的任务：")
        tasks.append(task)
        print(f"任务已添加，任务名称：{task}")
    elif choice == "2":
        if tasks:
            print("你所有的任务有：")
            for i in range(len(tasks)):
                print(f"{i+1}.{tasks[i]}")
        else:
            print("暂无任务")
    elif choice == "3":
        if tasks:
            index = int(input("输入要删除的任务编号："))-1
            if 0 <= index < len(tasks):
                removed = tasks.pop(index)
                print(removed)
            else:
                print("编号错误")
        else:
            print("没有任务可以删除")
    elif choice == "4":
        print("再见")
        break
    else:
        print("选择无效,请重新输入！")
