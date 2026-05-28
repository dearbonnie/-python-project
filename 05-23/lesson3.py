import random

# 產生 1~100 的隨機數字
answer = random.randint(1, 100)

print("🎮 歡迎來到猜數字遊戲！")
print("請猜一個 1 到 100 的數字")

count = 0

while True:
    guess = input("請輸入你的猜測：")

    # 檢查是否為數字
    if not guess.isdigit():
        print("⚠️ 請輸入有效的數字！")
        continue

    guess = int(guess)
    count += 1

    if guess < answer:
        print("太小了！")
    elif guess > answer:
        print("太大了！")
    else:
        print(f"🎉 恭喜你猜對了！答案就是 {answer}")
        print(f"你總共猜了 {count} 次")
        break