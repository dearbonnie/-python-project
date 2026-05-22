import random
import sys


def choose_difficulty():
	print("選擇難度：")
	print("  1) 簡單（1-20，10 次）")
	print("  2) 中等（1-100，8 次）")
	print("  3) 困難（1-1000，10 次）")
	while True:
		choice = input("輸入 1/2/3（或直接輸入最大數字）：").strip()
		if choice in ("1", "2", "3"):
			if choice == "1":
				return 20, 10
			if choice == "2":
				return 100, 8
			return 1000, 10
		# 允許直接輸入最大數字，例如輸入 50
		try:
			max_num = int(choice)
			if max_num >= 2:
				return max_num, max(5, int(max_num.bit_length() * 2))
		except ValueError:
			pass
		print("輸入錯誤，請輸入 1、2、3 或一個大於等於 2 的整數。")


def play_round(max_num, max_attempts):
	secret = random.randint(1, max_num)
	attempts = 0
	print(f"我已經想好一個 1 到 {max_num} 的數字，你有 {max_attempts} 次機會。祝好運！")
	while attempts < max_attempts:
		remaining = max_attempts - attempts
		try:
			guess = input(f"第 {attempts+1} 次 - 請猜一個數字（剩 {remaining} 次）：").strip()
			guess_int = int(guess)
		except ValueError:
			print("請輸入有效的整數。")
			continue

		attempts += 1
		if guess_int == secret:
			print(f"恭喜！你在 {attempts} 次內猜中答案 {secret}。")
			return True
		if guess_int < secret:
			print("太小了。")
		else:
			print("太大了。")

		# 額外提示：若只剩 1 次，給出更具體提示
		if max_attempts - attempts == 1:
			diff = abs(secret - guess_int)
			if diff <= 5:
				print("提示：你已非常接近！")
			elif diff <= 15:
				print("提示：還算接近。")

	print(f"挑戰結束，答案是 {secret}。加油下次再試！")
	return False


def main():
	print("=== 猜數字遊戲 ===")
	while True:
		max_num, max_attempts = choose_difficulty()
		play_round(max_num, max_attempts)
		again = input("要再玩一次嗎？(y/n)：").strip().lower()
		if again not in ("y", "yes", "yep", "是"):
			print("感謝遊玩！再見。")
			break


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("\n遊戲中止，掰掰。")
		sys.exit(0)

