import typing
import os
import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap, QTextCursor, QColor
from PyQt5.QtWidgets import QMainWindow, QLabel, QApplication, QWidget, QColorDialog, QInputDialog, QCheckBox
from PyQt5 import uic, QtCore, QtGui
import cv2
from PyQt5 import QtWidgets
from PyQt5 import Qt
from library_bmp_to_binary import *


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("ui\\text_creator.ui", self)
        # POINTERS TO ELEMENTS IN THE UI FILE
        # Pointer to buttons
        self.updateButton = self.findChild(QtWidgets.QPushButton, 'updateButton')  # Find the button
        self.updateButton.clicked.connect(self.update_button_pressed)
        self.saveButton = self.findChild(QtWidgets.QPushButton, 'saveButton')  # Find the button
        self.saveButton.clicked.connect(self.save)
        self.discardButton = self.findChild(QtWidgets.QPushButton, 'discardButton')  # Find the button
        self.discardButton.clicked.connect(self.discard)

        self.backgroundColorPicker = self.findChild(QtWidgets.QPushButton, 'backgroundColorPicker')  # Find the button
        self.backgroundColorPicker.clicked.connect(self.background_color_picker)
        self.textColorPicker = self.findChild(QtWidgets.QPushButton, 'textColorPicker')  # Find the button
        self.textColorPicker.clicked.connect(self.text_color_picker)

        # Pointer to Inputs
        self.inputText = self.findChild(QtWidgets.QLineEdit, 'inputText')  # Find the input field
        self.inputScale = self.findChild(QtWidgets.QLineEdit, 'inputScale')  # Find the input field
        self.inputTextThickness = self.findChild(QtWidgets.QLineEdit, 'inputTextThickness')  # Find the input field
        self.inputX = self.findChild(QtWidgets.QLineEdit, 'inputX')  # Find the input field
        self.inputY = self.findChild(QtWidgets.QLineEdit, 'inputY')  # Find the input field
        self.inputSpeed = self.findChild(QtWidgets.QLineEdit, 'inputSpeed')  # Find the input field
        # Pointer to Image Label
        self.image_frame = self.findChild(QtWidgets.QLabel, 'image_frame')  # Find the image frame label

        # Checkbox
        self.centerText = self.findChild(QtWidgets.QCheckBox,'centerText')  # Find the check box
        self.centerText.stateChanged.connect(lambda: self.center_text(self.centerText))

        # Initiation of the important parameters for the image creation
        self.background_color = [0, 0, 0]
        self.text = self.inputText.text()
        self.scale = self.inputScale.text()
        self.text_color = [255, 255, 255]
        self.text_thickness = self.inputTextThickness.text()
        self.x_coordinate = self.inputX.text()
        self.y_coordinate = self.inputY.text()
        self.speed = self.inputSpeed.text()
        self.center = False

    def update_button_pressed(self):
        # Create Picture
        cv_img = create_frame_with_text(self.background_color, self.inputText.text(), float(self.inputScale.text()),
                                        self.text_color, int(self.inputTextThickness.text()),
                                        int(self.inputX.text()), int(self.inputY.text()), center=True)[0]

        print(create_frame_with_text(self.background_color, self.inputText.text(), float(self.inputScale.text()),
                                     self.text_color, int(self.inputTextThickness.text()),
                                     int(self.inputX.text()), int(self.inputY.text()), center=True)[1])

        qt_img = self.convert_cv_qt(cv_img)
        self.image_frame.setPixmap(qt_img)

        # show image on LED Wall
        create_and_show_text_animation(self.background_color, self.inputText.text(), float(self.inputScale.text()),
                                       self.text_color, int(self.inputTextThickness.text()),
                                       int(self.inputX.text()), int(self.inputY.text()), int(self.inputSpeed.text()),
                                       center=True)




    def background_color_picker(self):
        q_background_color = QtWidgets.QColorDialog.getColor()
        rgb = q_background_color.name()
        h = rgb.lstrip('#')
        new_rgb = tuple(int(h[i:i + 2], 16) for i in (0, 2, 3))
        # print(new_rgb)
        self.background_color = list(new_rgb)

    def text_color_picker(self):
        q_text_color = QtWidgets.QColorDialog.getColor()
        rgb = q_text_color.name()
        h = rgb.lstrip('#')
        new_rgb = tuple(int(h[i:i + 2], 16) for i in (0, 2, 3))
        # print(new_rgb)
        self.text_color = list(new_rgb)

    def center_text(self, centerText):
        if centerText:
            self.center = True


    def convert_cv_qt(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(500, 281)
        return QPixmap.fromImage(p)

    def save(self):
        text, ok = QInputDialog.getText(self, "Bild Speichern", "Bitte gewünschten Dateinamen eingeben")
        if ok:
            img = create_frame_with_text(self.background_color, self.inputText.text(), float(self.inputScale.text()),
                                         self.text_color, int(self.inputTextThickness.text()),
                                         int(self.inputX.text()), int(self.inputY.text()))[0]

            cv2.imwrite(text + '.bmp', img)
            self.close()

    def discard(self):
        self.close()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
