#!/usr/bin/env python3
from PyQt5 import QtWidgets
import sys

from main_window import MainWindow


def main():
    app: QtWidgets.QApplication = QtWidgets.QApplication(sys.argv)
    main_window: MainWindow = MainWindow()
    app.exec_()

if __name__ == "__main__":
    main()
