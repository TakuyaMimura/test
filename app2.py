# app.py

# sysモジュールをインポート（コマンドライン引数などで使う）
import sys

# PyQt5の基本的なウィジェット関連モジュールをインポート
from PyQt5.QtWidgets import QApplication, QLabel, QWidget

# QApplicationオブジェクトを作成
# これがPyQtアプリケーションのメインイベントループを管理する
app = QApplication(sys.argv)

# メインウィンドウを作成（QWidgetは基本的なウィンドウ）
window = QWidget()

# ウィンドウタイトルを設定
window.setWindowTitle("PyQt5 サンプル")

# ウィンドウの位置（x=100, y=100）とサイズ（幅=300, 高さ=200）を設定
window.setGeometry(100, 100, 300, 200)

# ウィンドウにラベル（テキスト）を追加
label = QLabel("Hello, PyQt5!", parent=window)

# ラベルの位置を（x=100, y=80）に設定
label.move(100, 80)

# ウィンドウを表示
window.show()

# アプリケーションのメインイベントループを開始
# イベントループが終了したらアプリケーションを終了（exitコードを返す）
sys.exit(app.exec_())