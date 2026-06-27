import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path


plt.rcParams["font.sans-serif"] = ["Arial Unicode MS", "Heiti TC", "Microsoft JhengHei"]
plt.rcParams["axes.unicode_minus"] = False


def main() -> None:
    labels = ["Nokia", "Samsung", "Apple", "Lumia"]
    values = [20, 30, 45, 10]
    colors = ["yellow", "green", "red", "blue"]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        values,
        labels=labels,
        colors=colors,
        explode=[0.3, 0, 0, 0],
        shadow=True,
        autopct="%2.1f%%",
        startangle=180,
    )
    ax.set_title("手機品牌占比")

    output_path = Path(__file__).with_suffix(".png")
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"已輸出圖表: {output_path}")


if __name__ == "__main__":
    main()
