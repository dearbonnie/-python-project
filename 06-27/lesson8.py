"""
台灣各鄉鎮市區人口密度查詢系統
使用 pandas 處理資料，tkinter / ttk 建立桌面 GUI
"""

import pandas as pd
import tkinter as tk
from tkinter import ttk


def load_and_process_data():
    """讀取 CSV 並進行資料清理與整理"""

    # 讀取 CSV（不將第一列作為欄位名稱）
    df = pd.read_csv('各鄉鎮市區人口密度.csv', header=None)

    # 將第二列（中文標題）作為欄位名稱
    df.columns = df.iloc[1].values
    # 移除前三列（原欄位名稱、中文標題、以及多餘的第一筆資料列）
    df = df.iloc[2:].reset_index(drop=True)

    # 移除最後 5 筆非資料內容（尾部說明資訊）
    df = df.iloc[:-5].reset_index(drop=True)

    # 僅保留需要的欄位，並重新命名
    df = df[['區域別', '年底人口數', '土地面積']].copy()
    df.rename(columns={'年底人口數': '人口數'}, inplace=True)

    # 將人口數與土地面積轉換為數值型態（"…" 會被轉成 NaN）
    df['人口數'] = pd.to_numeric(df['人口數'], errors='coerce')
    df['土地面積'] = pd.to_numeric(df['土地面積'], errors='coerce')

    # 移除含有空值的列
    df.dropna(inplace=True)

    # 新增人口密度欄位
    df['人口密度'] = (df['人口數'] / df['土地面積']).round(2)

    # 人口數顯示為整數
    df['人口數'] = df['人口數'].astype(int)

    return df


def filter_data(df, keyword):
    """根據關鍵字篩選區域別"""
    if keyword.strip() == '':
        return df
    return df[df['區域別'].str.contains(keyword, na=False)]


def update_table(tree, df):
    """清空並重新填入 Treeview 表格"""
    # 清除現有資料
    for row in tree.get_children():
        tree.delete(row)

    # 逐筆插入資料
    for _, row in df.iterrows():
        tree.insert('', 'end', values=(
            row['區域別'],
            row['人口數'],
            row['土地面積'],
            row['人口密度'],
        ))


def on_search(tree, df, entry):
    """查詢按鈕的回呼函數"""
    keyword = entry.get()
    filtered = filter_data(df, keyword)
    update_table(tree, filtered)


def main():
    # 載入資料
    df = load_and_process_data()

    # 建立主視窗
    root = tk.Tk()
    root.title('台灣鄉鎮市區人口密度查詢系統')
    root.geometry('900x600')

    # ======== 上方控制區 ========
    control_frame = ttk.Frame(root, padding=10)
    control_frame.pack(fill=tk.X)

    ttk.Label(control_frame, text='輸入區域名稱：').pack(side=tk.LEFT, padx=(0, 5))

    entry = ttk.Entry(control_frame, width=30)
    entry.pack(side=tk.LEFT, padx=(0, 5))

    search_btn = ttk.Button(
        control_frame,
        text='查詢',
        command=lambda: on_search(tree, df, entry),
    )
    search_btn.pack(side=tk.LEFT)

    # ======== 下方表格區 ========
    table_frame = ttk.Frame(root, padding=(10, 0, 10, 10))
    table_frame.pack(fill=tk.BOTH, expand=True)

    # 定義欄位
    columns = ('區域別', '人口數', '土地面積', '人口密度')
    tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)

    # 設定每一個欄位
    for col in columns:
        tree.heading(col, text=col, anchor=tk.CENTER)
        tree.column(col, width=180, anchor=tk.CENTER)

    # 加上垂直與水平捲軸
    v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
    h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=tree.xview)
    tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

    tree.grid(row=0, column=0, sticky='nsew')
    v_scrollbar.grid(row=0, column=1, sticky='ns')
    h_scrollbar.grid(row=1, column=0, sticky='ew')

    table_frame.grid_rowconfigure(0, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)

    # 預設顯示全部資料
    update_table(tree, df)

    # 啟動主迴圈
    root.mainloop()


if __name__ == '__main__':
    main()
