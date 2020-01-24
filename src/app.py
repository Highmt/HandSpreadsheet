import sys
from PyQt5.QtWidgets import QApplication
from src.HandSpreadSheet import HandSpreadSheet

if __name__ == '__main__':
    app = QApplication(sys.argv)
    sheet = HandSpreadSheet(50, 50)
    sheet.resize(1000, 600)
    sheet.show()
    sys.exit(app.exec_())