secret =7
guess = 0
while guess != secret:
    guess = int(input("猜一个数字，0-7之间："))
    if guess < secret:
        print("猜小了")
    elif guess > secret:
        print("猜大了")
    else:
        print("猜对了")
while True:
    cmd =input("输入‘A’，退出")
    if cmd == "A":
        break
    else:
        print(f"你输入了：{cmd}")