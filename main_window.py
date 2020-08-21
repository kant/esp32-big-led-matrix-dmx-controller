import typing
import threading as th
import os
import sys
from PyQt5.QtCore import QTimer, QFile, QUrl, QFileInfo, QRunnable, QThreadPool, pyqtSlot
from PyQt5.QtGui import QPixmap, QTextCursor, QColor
from PyQt5.QtWidgets import QMainWindow, QLabel, QApplication, QFileDialog
from PyQt5 import uic, QtCore, QtGui
import cv2
from PyQt5 import QtWidgets
from PyQt5 import Qt
from library_bmp_to_binary import *


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("D:\\Projekte\\led-matrix-qt-gui\\main_gui.ui", self)

        # Creating the Thread pool
        self.threadpool = QThreadPool()
        print("Multitasking with maximum %d threads" % self.threadpool.maxThreadCount())

        # POINTERS TO ELEMENTS IN THE UI FILE
        # Pointer to buttons
        self.openButton = self.findChild(QtWidgets.QPushButton, 'openVideo')  # Find the button
        self.openButton.clicked.connect(self.open_button_pressed)
        self.showButton = self.findChild(QtWidgets.QPushButton, 'showVideo')  # Find the button
        self.showButton.clicked.connect(self.show_button_pressed)
        self.stopButton = self.findChild(QtWidgets.QPushButton, 'stopVideo')  # Find the button
        self.stopButton.clicked.connect(self.stop_button_pressed)

        self.filename_label = self.findChild(QtWidgets.QLabel, 'filename')  # Find the "filename" label

        self.file_path = ""

    def open_button_pressed(self):
        print("Open")
        self.file_path, _ = QFileDialog.getOpenFileName(self, 'Open file', "Files")
        print(self.file_path)
        url = QUrl.fromLocalFile(self.file_path)
        self.filename_label.setText(url.fileName())

    def show_button_pressed(self):
        video_file_name = self.file_path
        th.Thread(target=lt1_video(video_file_name), args=(), name='video', daemon=True).start()



    def stop_button_pressed(self):
        stop_function()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()


