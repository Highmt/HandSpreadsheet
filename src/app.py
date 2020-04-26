import sys
from PyQt5.QtWidgets import QApplication
from src.SpreadSheet.HandSpreadSheet import HandSpreadSheet

if __name__ == '__main__':
    app = QApplication(sys.argv)
    sheet = HandSpreadSheet(50, 50)
    # sheet.resize(1000, 1000)
    sheet.showFullScreen()
    sys.exit(app.exec_())