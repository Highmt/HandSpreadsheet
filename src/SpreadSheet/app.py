import sys

from PyQt5.QtWidgets import QApplication
from src.SpreadSheet.HandSpreadSheet import HandSpreadSheet

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("app")
    sheet = HandSpreadSheet(50, 50)
    sys.exit(app.exec_())
