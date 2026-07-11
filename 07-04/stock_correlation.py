"""
台股相關係數分析工具
輸入 2~4 檔股票代號，自動計算股價相關係數矩陣
"""

import sys
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QMessageBox, QStatusBar, QFrame, QSizePolicy,
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QColor

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Heiti TC', 'Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

# 常用台灣股票對照表（可自行擴充）
STOCK_LOOKUP = {
    '1101': '台泥', '1102': '亞泥', '1216': '統一', '1301': '台塑',
    '1303': '南亞', '1326': '台化', '1402': '遠東新', '2002': '中鋼',
    '2105': '正新', '2207': '和泰車', '2301': '光寶科', '2303': '聯電',
    '2308': '台達電', '2317': '鴻海', '2324': '仁寶', '2327': '國巨',
    '2330': '台積電', '2345': '智邦', '2356': '英業達', '2357': '華碩',
    '2376': '技嘉', '2377': '微星', '2382': '廣達', '2395': '研華',
    '2408': '南亞科', '2409': '友達', '2412': '中華電', '2449': '京元電子',
    '2454': '聯發科', '2458': '義隆', '2474': '可成', '2603': '長榮',
    '2609': '陽明', '2618': '長榮航', '2801': '彰銀', '2880': '華南金',
    '2881': '富邦金', '2882': '國泰金', '2883': '開發金', '2884': '玉山金',
    '2885': '元大金', '2886': '兆豐金', '2887': '台新金', '2888': '新光金',
    '2890': '永豐金', '2891': '中信金', '2892': '第一金', '2912': '統一超',
    '3008': '大立光', '3034': '聯詠', '3037': '欣興', '3045': '台灣大',
    '3231': '緯創', '3443': '創意', '3533': '嘉澤', '3661': '世芯-KY',
    '3711': '日月光投控', '4904': '遠傳', '4938': '和碩', '5274': '信驊',
    '5871': '中租-KY', '5876': '上海商銀', '5880': '合庫金', '6239': '力成',
    '6414': '樺漢', '6446': '藥華藥', '6505': '台塑化', '6669': '緯穎',
    '6770': '力積電', '6789': '采鈺', '8016': '矽創', '8046': '南電',
    '8299': '群聯', '8454': '富邦媒', '9904': '寶成', '9910': '豐泰',
}


class FetchWorker(QThread):
    """背景下載股價資料"""
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, symbols, names):
        super().__init__()
        self.symbols = symbols
        self.names = names

    def run(self):
        try:
            df = yf.download(self.symbols, period='1y', interval='1d',
                             auto_adjust=True, progress=False)
            close_df = df['Close'].copy()
            close_df.columns = self.names
            close_df = close_df.dropna()
            if close_df.empty:
                self.error.emit('無足夠交易資料，請確認股票代號是否正確')
                return
            self.finished.emit(close_df)
        except Exception as e:
            self.error.emit(str(e))


class StockCorrelationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('台股相關係數分析工具')
        self.resize(950, 700)

        # 存放已選擇的股票 (代號, 名稱)
        self.stocks = []

        self._setup_ui()
        self._update_ui_state()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(12)

        # ── 標題 ──
        title = QLabel('📊 台股相關係數分析')
        title.setStyleSheet('font-size: 22px; font-weight: bold; color: #0f172a;')
        root.addWidget(title)

        subtitle = QLabel(
            '輸入台灣股票代號（如 2330），加入 2 ~ 4 檔股票後自動分析相關係數'
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet('font-size: 13px; color: #64748b; margin-bottom: 4px;')
        root.addWidget(subtitle)

        # ── 輸入列 ──
        input_layout = QHBoxLayout()
        self.stock_input = QLineEdit()
        self.stock_input.setPlaceholderText('請輸入股票代號，例如 2330')
        self.stock_input.setStyleSheet(
            'QLineEdit { padding: 8px 12px; font-size: 16px; border: 2px solid #e2e8f0; '
            'border-radius: 8px; } '
            'QLineEdit:focus { border-color: #3b82f6; }'
        )
        self.stock_input.returnPressed.connect(self._add_stock)
        input_layout.addWidget(self.stock_input, stretch=1)

        self.add_btn = QPushButton('➕ 加入')
        self.add_btn.setStyleSheet(
            'QPushButton { background-color: #3b82f6; color: white; border: none; '
            'border-radius: 8px; padding: 8px 20px; font-size: 14px; font-weight: bold; }'
            'QPushButton:hover { background-color: #2563eb; }'
            'QPushButton:disabled { background-color: #94a3b8; }'
        )
        self.add_btn.clicked.connect(self._add_stock)
        input_layout.addWidget(self.add_btn)

        self.analyze_btn = QPushButton('📈 分析相關係數')
        self.analyze_btn.setStyleSheet(
            'QPushButton { background-color: #10b981; color: white; border: none; '
            'border-radius: 8px; padding: 8px 20px; font-size: 14px; font-weight: bold; }'
            'QPushButton:hover { background-color: #059669; }'
            'QPushButton:disabled { background-color: #94a3b8; }'
        )
        self.analyze_btn.clicked.connect(self._analyze)
        input_layout.addWidget(self.analyze_btn)

        root.addLayout(input_layout)

        self.status_label = QLabel('請加入 2 ~ 4 檔股票')
        self.status_label.setStyleSheet('font-size: 12px; color: #64748b;')
        root.addWidget(self.status_label)

        # ── 上下分割：上為股票列表，下為圖表 ──
        self.splitter = QFrame()
        split_layout = QVBoxLayout(self.splitter)
        split_layout.setContentsMargins(0, 0, 0, 0)
        split_layout.setSpacing(10)

        # 股票清單
        list_label = QLabel('已選擇的股票：')
        list_label.setStyleSheet('font-size: 14px; font-weight: bold; color: #334155;')
        split_layout.addWidget(list_label)

        self.stock_list = QListWidget()
        self.stock_list.setStyleSheet(
            'QListWidget { border: 1px solid #e2e8f0; border-radius: 8px; '
            'font-size: 14px; padding: 4px; }'
            'QListWidget::item { padding: 6px 8px; border-radius: 4px; }'
            'QListWidget::item:selected { background-color: #dbeafe; color: #1e40af; }'
        )
        self.stock_list.setMinimumHeight(100)
        self.stock_list.setMaximumHeight(150)
        split_layout.addWidget(self.stock_list)

        # 按鈕列（移除選取、清空）
        btn_row = QHBoxLayout()
        self.remove_btn = QPushButton('🗑 移除選取')
        self.remove_btn.setStyleSheet(
            'QPushButton { background-color: #f43f5e; color: white; border: none; '
            'border-radius: 6px; padding: 6px 16px; font-size: 13px; }'
            'QPushButton:hover { background-color: #e11d48; }'
            'QPushButton:disabled { background-color: #94a3b8; }'
        )
        self.remove_btn.clicked.connect(self._remove_selected)
        btn_row.addWidget(self.remove_btn)

        self.clear_btn = QPushButton('✖ 全部清空')
        self.clear_btn.setStyleSheet(
            'QPushButton { background-color: #64748b; color: white; border: none; '
            'border-radius: 6px; padding: 6px 16px; font-size: 13px; }'
            'QPushButton:hover { background-color: #475569; }'
            'QPushButton:disabled { background-color: #94a3b8; }'
        )
        self.clear_btn.clicked.connect(self._clear_all)
        btn_row.addWidget(self.clear_btn)

        btn_row.addStretch()
        split_layout.addLayout(btn_row)

        # ── matplotlib 圖表 ──
        self.figure, self.ax = plt.subplots(figsize=(8, 5.5))
        self.figure.patch.set_facecolor('#f8fafc')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        split_layout.addWidget(self.canvas, stretch=1)

        root.addWidget(self.splitter, stretch=1)

        # 狀態列
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('就緒')

    def _add_stock(self):
        code = self.stock_input.text().strip()
        if not code:
            return

        # 檢查是否已在清單中
        if any(s[0] == code for s in self.stocks):
            self.status_bar.showMessage(f'⚠️ {code} 已在清單中', 3000)
            self.stock_input.clear()
            return

        # 查詢股票名稱
        name = STOCK_LOOKUP.get(code)
        if name is None:
            # 不在預設清單中，嘗試從 yfinance 即時查詢
            try:
                info = yf.Ticker(f'{code}.TW').info
                name = info.get('longName', info.get('shortName', None))
                if name is None:
                    self.status_bar.showMessage(f'❌ 找不到代號 {code}', 3000)
                    return
            except Exception:
                self.status_bar.showMessage(f'❌ 無法查詢代號 {code}', 3000)
                return

        # 加入清單
        self.stocks.append((code, name))
        item = QListWidgetItem(f'{code}  {name}')
        item.setData(Qt.UserRole, code)
        self.stock_list.addItem(item)
        self.stock_input.clear()
        self.stock_input.setFocus()

        self._update_ui_state()
        self.status_bar.showMessage(f'✅ 已加入 {code} {name}', 3000)

        # 如果已滿 4 檔，自動分析
        if len(self.stocks) == 4:
            self._analyze()

    def _remove_selected(self):
        rows = self.stock_list.selectedIndexes()
        for idx in reversed(rows):
            code = self.stock_list.item(idx.row()).data(Qt.UserRole)
            self.stocks = [s for s in self.stocks if s[0] != code]
            self.stock_list.takeItem(idx.row())
        self._update_ui_state()

    def _clear_all(self):
        self.stock_list.clear()
        self.stocks.clear()
        self.ax.clear()
        self.ax.text(0.5, 0.5, '加入股票後顯示相關係數矩陣',
                     ha='center', va='center', fontsize=14, color='#94a3b8')
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.canvas.draw()
        self._update_ui_state()
        self.status_bar.showMessage('已清空所有股票', 3000)

    def _update_ui_state(self):
        n = len(self.stocks)
        self.remove_btn.setEnabled(n > 0)
        self.clear_btn.setEnabled(n > 0)
        self.analyze_btn.setEnabled(2 <= n <= 4)
        self.status_label.setText(
            f'已選取 {n} 檔股票（需 2 ~ 4 檔）' + (' ✅ 可分析' if 2 <= n <= 4 else '')
        )

    def _analyze(self):
        if len(self.stocks) < 2 or len(self.stocks) > 4:
            return

        symbols = [f'{s[0]}.TW' for s in self.stocks]
        names = [s[1] for s in self.stocks]

        self.analyze_btn.setEnabled(False)
        self.status_bar.showMessage('📥 正在下載股價資料…')

        self.worker = FetchWorker(symbols, names)
        self.worker.finished.connect(self._draw_correlation)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _draw_correlation(self, df):
        self.ax.clear()

        corr = df.corr()
        labels = corr.columns.tolist()

        # 熱力圖
        im = self.ax.imshow(corr, cmap='RdYlBu_r', vmin=0, vmax=1,
                            aspect='auto', interpolation='nearest')

        self.ax.set_xticks(range(len(labels)))
        self.ax.set_yticks(range(len(labels)))
        self.ax.set_xticklabels(labels, fontsize=13)
        self.ax.set_yticklabels(labels, fontsize=13)

        # 填入數值
        for i in range(len(labels)):
            for j in range(len(labels)):
                val = corr.iloc[i, j]
                color = 'white' if val > 0.5 else '#1e293b'
                self.ax.text(j, i, f'{val:.4f}', ha='center', va='center',
                             fontsize=15, fontweight='bold', color=color)

        self.ax.set_title('股價相關係數矩陣 (Pearson)', fontsize=16,
                          fontweight='bold', pad=12)

        cbar = self.figure.colorbar(im, ax=self.ax, shrink=0.8, pad=0.04)
        cbar.set_label('相關係數', fontsize=12)

        # 底部顯示資料統計
        info_text = f'資料區間：{df.index[0].strftime("%Y-%m-%d")} ~ {df.index[-1].strftime("%Y-%m-%d")} ｜ 共 {len(df)} 個交易日'
        self.figure.text(0.5, 0.01, info_text, ha='center', fontsize=10, color='#64748b')

        self.figure.tight_layout(rect=[0, 0.03, 1, 1])
        self.canvas.draw()

        self.analyze_btn.setEnabled(True)
        self.status_bar.showMessage(f'✅ 分析完成，共 {len(df)} 筆交易日', 5000)

    def _on_error(self, msg):
        self.analyze_btn.setEnabled(True)
        self.status_bar.showMessage(f'❌ {msg}', 5000)
        QMessageBox.warning(self, '下載錯誤', f'無法取得資料：\n{msg}')

    def closeEvent(self, event):
        plt.close(self.figure)
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    font = QFont('.AppleSystemUIFont', 10)
    font.setStyleHint(QFont.SansSerif)
    app.setFont(font)

    window = StockCorrelationApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
