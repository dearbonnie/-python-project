import random


def guess_number_game() -> None:
    """執行一個簡單的 1 到 100 猜數字遊戲。"""
    secret = random.randint(1, 100)
    attempts = 0

    print("歡迎來到猜數字遊戲！")
    print("我已經想好一個 1 到 100 之間的整數，請你猜猜看。")

    while True:
        user_input = input("請輸入你的猜測：")
        user_input = user_input.strip()

        if not user_input:
            print("請輸入一個數字。")
            continue

        try:
            guess = int(user_input)
        except ValueError:
            print("輸入錯誤，請輸入整數。")
            continue

        attempts += 1

        if guess < 1 or guess > 100:
            print("請輸入介於 1 到 100 的數字。")
            continue

        if guess < secret:
            print("太小了！再試一次。")
        elif guess > secret:
            print("太大了！再試一次。")
        else:
            print(f"恭喜你，猜對了！答案是 {secret}。")
            print(f"你總共猜了 {attempts} 次。")
            break


def main() -> None:
    guess_number_game()


if __name__ == "__main__":
    main()
