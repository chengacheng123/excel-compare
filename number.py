number = 22

guess = int(input("猜一个数字 (20-25):"))
if guess == number:
    print("猜对了")
elif guess > number:
    print("猜大了")
elif guess < number:
    print("猜小了")
else:
    print("猜错了")
