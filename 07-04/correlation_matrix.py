"""
台積電、聯發科、鴻海、聯電 — 股價相關係數矩陣圖
使用 PySide6 嵌入 matplotlib 繪製熱力圖
"""

import sys
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QLabel, QPushButton, QHBoxLayout, QMessageBox,
                               QStatusBar, QProgressBar)
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QFont

# 中文字型設定
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Heiti TC', 'Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False


# 台股四大權值股
STOCKS = {
    '2330.TW': '台積電',
    '2454.TW': '聯發科',
    '2317.TW': '鴻海',
    '2303.TW': '聯電',
}


class FetchWorker(QThread):
    """背景執行緒：下載股價資料，避免凍結 UI"""
    finished = Signal(object)
    error = Signal(str)

    def run(self):
        try:
            df = yf.download(
                list(STOCKS.keys()),
                period='1y',
                interval='1d',
                auto_adjust=True,
                progress=False,
            )
            close_df = df['Close'].copy()
            close_df.columns = [STOCKS[t] for t in close_df.columns]
            close_df = close_df.dropna()
            self.finished.emit(close_df)
        except Exception as e:
            self.error.emit(str(e))


class CorrelationMatrixApp(QMainWindow):
    """主視窗"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle('台股權值股相關係數矩陣')
        self.resize(800, 700)

        self.df = None
        self._setup_ui()
        self._fetch_data()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 標題
        title = QLabel('📊 台灣四大權值股 — 股價相關係數矩陣')
        title.setStyleSheet('font-size: 20px; font-weight: bold; color: #1e293b;')
        layout.addWidget(title)

        # 說明
        desc = QLabel('下方熱力圖顯示各公司近一年股價收盤價之間的 Pearson 相關係數。'
                      '數值越接近 1.0（深紅色）表示走勢越同步，越接近 0 表示越無關聯。')
        desc.setWordWrap(True)
        desc.setStyleSheet('font-size: 13px; color: #64748b; margin-bottom: 8px;')
        layout.addWidget(desc)

        # 進度列
        self.progress = QProgressBar()
        self.progress.setMaximum(0)  # 無限跑馬燈模式
        self.progress.setFixedHeight(6)
        self.progress.setTextVisible(False)
        layout.addWidget(self.progress)

        # 按鈕列
        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton('🔄 重新下載資料')
        self.refresh_btn.setStyleSheet(
            'QPushButton { background-color: #3b82f6; color: white; border: none; '
            'border-radius: 6px; padding: 8px 20px; font-size: 14px; }'
            'QPushButton:hover { background-color: #2563eb; }'
        )
        self.refresh_btn.clicked.connect(self._fetch_data)
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # matplotlib 畫布容器
        self.figure, self.ax = plt.subplots(figsize=(7, 6))
        self.figure.patch.set_facecolor('#f8fafc')
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas, stretch=1)

        # 狀態列
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage('正在下載股價資料…')

    def _fetch_data(self):
        self.progress.setVisible(True)
        self.refresh_btn.setEnabled(False)
        self.status.showMessage('正在從 Yahoo Finance 下載資料…')

        self.worker = FetchWorker()
        self.worker.finished.connect(self._on_data_ready)
        self.worker.error.connect(self._on_data_error)
        self.worker.start()

    def _on_data_ready(self, df):
        self.df = df
        self.progress.setVisible(False)
        self.refresh_btn.setEnabled(True)
        self.status.showMessage(f'資料就緒：{len(df)} 筆交易日', 5000)
        self._draw_chart()

    def _on_data_error(self, msg):
        self.progress.setVisible(False)
        self.refresh_btn.setEnabled(True)
        self.status.showMessage('下載失敗，請檢查網路連線', 5000)
        QMessageBox.warning(self, '下載錯誤', f'無法取得股價資料：\n{msg}')

    def _draw_chart(self):
        self.ax.clear()

        # 計算相關係數矩陣
        corr = self.df.corr()

        # 繪製熱力圖
        im = self.ax.imshow(corr, cmap='RdYlBu_r', vmin=0, vmax=1,
                            aspect='auto', interpolation='nearest')

        # 設定標籤
        labels = corr.columns.tolist()
        self.ax.set_xticks(range(len(labels)))
        self.ax.set_yticks(range(len(labels)))
        self.ax.set_xticklabels(labels, fontsize=13)
        self.ax.set_yticklabels(labels, fontsize=13)

        # 在格子中填入數值
        for i in range(len(labels)):
            for j in range(len(labels)):
                val = corr.iloc[i, j]
                color = 'white' if val > 0.5 else '#1e293b'
                self.ax.text(j, i, f'{val:.4f}', ha='center', va='center',
                             fontsize=14, fontweight='bold', color=color)

        self.ax.set_title('股價相關係數矩陣 (Pearson)', fontsize=16, pad=16,
                          fontweight='bold')

        # 顏色條
        cbar = self.figure.colorbar(im, ax=self.ax, shrink=0.8, pad=0.04)
        cbar.set_label('相關係數', fontsize=12)

        self.figure.tight_layout()
        self.canvas.draw()

    def closeEvent(self, event):
        plt.close(self.figure)
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    font = QFont('.AppleSystemUIFont', 10)
    font.setStyleHint(QFont.SansSerif)
    app.setFont(font)

    window = CorrelationMatrixApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
