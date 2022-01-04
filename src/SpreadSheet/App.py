import sys

from PyQt5.QtWidgets import QApplication
from src.SpreadSheet.HandSpreadSheet import HandSpreadSheet

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("app")
    sheet = HandSpreadSheet(rows=50, cols=50)
    sheet.showFullScreen()
    sys.exit(app.exec_())
