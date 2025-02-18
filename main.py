from PyQt5.QtWidgets import QApplication
from ui import TabularApp
import sys

def main():
    app = QApplication(sys.argv)
    window = TabularApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
