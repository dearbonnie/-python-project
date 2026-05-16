import random


def tarot_card_game() -> None:
    """執行簡單塔羅牌翻牌遊戲。"""
    cards = [
        ("愚者", "新的開始、自由、冒險、信任直覺"),
        ("魔術師", "創造力、行動、實現目標、資源整合"),
        ("女祭司", "直覺、潛意識、內在智慧、沉穩"),
        ("皇后", "滋養、豐盛、母性、支持"),
        ("皇帝", "穩定、權威、結構、責任"),
        ("教皇", "傳統、學習、指導、信念"),
        ("戀人", "關係、選擇、協調、愛"),
        ("戰車", "意志、力量、勝利、前進"),
        ("力量", "勇氣、耐心、自信、內在力量"),
        ("隱者", "反省、尋找真理、內觀、孤獨"),
        ("命運之輪", "循環、機會、變化、命運"),
        ("正義", "公平、因果、平衡、決斷"),
        ("倒吊人", "等待、犧牲、換個角度、放手"),
        ("死神", "結束、新開始、轉變、蛻變"),
        ("節制", "平衡、和諧、節制、整合"),
        ("惡魔", "束縛、誘惑、執迷、面對陰暗面"),
        ("塔", "突變、解構、意外覺醒、重建"),
        ("星星", "希望、療癒、靈感、祝福"),
        ("月亮", "幻象、潛意識、不確定、夢境"),
        ("太陽", "快樂、成功、活力、清晰"),
        ("審判", "覺醒、回顧、釋放、決定"),
        ("世界", "圓滿、完成、成就、新旅程"),
    ]

    print("歡迎來到塔羅牌翻牌遊戲！")
    print("我有 22 張大阿爾克那牌，請從 1 到 22 選一張牌來翻開。")

    while True:
        user_input = input("請輸入你要翻的牌號（1-22），或輸入 q 離開：").strip()

        if not user_input:
            print("請輸入一個數字或 q。")
            continue

        if user_input.lower() == "q":
            print("感謝遊玩，期待下次再見！")
            break

        try:
            index = int(user_input)
        except ValueError:
            print("輸入錯誤，請輸入 1 到 22 的數字，或 q 離開。")
            continue

        if index < 1 or index > len(cards):
            print("牌號必須介於 1 到 22。")
            continue

        card_name, card_meaning = cards[index - 1]
        orientation = random.choice(["正位", "逆位"])

        print(f"你翻開的是第 {index} 張：{card_name} ({orientation})")
        print(f"牌意：{card_meaning}")
        print("如果想再翻一張，就繼續輸入牌號；輸入 q 結束遊戲。\n")


def main() -> None:
    tarot_card_game()


if __name__ == "__main__":
    main()
