import typing
import os
from time import sleep

import cv2
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QColorDialog, QMessageBox, QFileDialog
from PyQt5 import uic


from matrix_controller import Matrix
from fading_color_frame_provider import FadingColorFrameProvider
from video_frame_provider import VideoFrameProvider
from run_text_provider import RunTextProvider


class MainWindow(QMainWindow):
    LAYOUT = 1
    VIDEO_FILENAME: str = "Homer.mp4"
    ENDPOINTS: list = [
        {'ip_address': "192.168.2.158",
         'port': 50000},
        {'ip_address': "192.168.2.159",
         'port': 50000},
        {'ip_address': "192.168.2.161",
         'port': 50000},
        {'ip_address': "192.168.2.157",
         'port': 50000}]

    python_file_path: str = ""
    matrix: Matrix = Matrix()
    fading_color_frame_provider: FadingColorFrameProvider = None
    video_frame_provider: VideoFrameProvider = None

    def __init__(self) -> None:
        self.matrix.configure(self.ENDPOINTS)
        QMainWindow.__init__(self)
        self.python_file_path = os.path.dirname(os.path.abspath(__file__))
        self._init_window_design()
        self.fading_color_frame_provider = FadingColorFrameProvider(self.ENDPOINTS)
        self.video_frame_provider = VideoFrameProvider(self.ENDPOINTS, self.VIDEO_FILENAME)
        self.TEXT = self.edt_text.text()
        print("Text: " + str(self.edt_text.text()))
        self.BACKROUND_COLOR = [255, 255, 255]
        # self.SCALE = self.edt_scale.text()
        self.SCALE = 1
        print("Scale: " + str(self.edt_scale.text()))
        self.COLOR = [0, 0, 0]
        self.THICKNESS = self.edt_thickness.text()
        print("Thickness: " + str(self.edt_thickness.text()))
        self.SPEED = self.edt_speed.text()
        print("Speed: " + str(self.edt_speed.text()))
        self.MATIRX_WIDTH = 50
        self.MATRIX_HEIGHT = 28
        self.FONT_FAMILY = "dummy"

        self.run_text_provider = RunTextProvider(self.ENDPOINTS, self.LAYOUT, self.TEXT, self.BACKROUND_COLOR,
                                                 self.SCALE, self.COLOR, self.THICKNESS, self.FONT_FAMILY, self.SPEED,
                                                 self.MATIRX_WIDTH, self.MATRIX_HEIGHT)

        self.show()

    def _init_window_design(self) -> None:
        uic.loadUi(os.path.join(self.python_file_path, "main_window.ui"), self)

        self.btn_clear.clicked.connect(self.on_btn_clear_click)

        # main effects
        self.btn_start_running_text.clicked.connect(self.on_btn_start_running_text_click)
        self.btn_stop_running_text.clicked.connect(self.on_btn_stop_running_text_click)
        self.btn_start_video.clicked.connect(self.on_btn_start_video_click)
        self.btn_stop_video.clicked.connect(self.on_btn_stop_video_click)
        self.btn_start_picture.clicked.connect(self.on_btn_start_picture_click)
        self.btn_stop_picture.clicked.connect(self.on_btn_stop_picture_click)

        # functions for running effects
        self.btn_back_color.clicked.connect(self.background_color_picker)
        self.btn_color.clicked.connect(self.text_color_picker)
        self.btn_choose_file_1.clicked.connect(self.on_btn_choose_file_1_click)
        self.btn_choose_file_2.clicked.connect(self.on_btn_choose_file_2_click)

        # additional effects
        self.btn_start_rainbow.clicked.connect(self.on_btn_start_rainbow_click)
        self.btn_stop_rainbow.clicked.connect(self.on_btn_stop_rainbow_click)
        self.btn_start_simple_color.clicked.connect(self.on_btn_start_simple_color_click)
        self.btn_stop_simple_color.clicked.connect(self.on_btn_stop_simple_color_click)
        self.btn_start_fading_pixels.clicked.connect(self.on_btn_start_fading_pixels_click)
        self.btn_stop_fading_pixels.clicked.connect(self.on_btn_stop_fading_pixels_click)
        self.btn_start_audio_meter.clicked.connect(self.on_btn_start_audio_meter_click)
        self.btn_stop_audio_meter.clicked.connect(self.on_btn_stop_audio_meter_click)

        # functions for additional effects
        self.btn_simple_color_color.clicked.connect(self.on_btn_simple_color_color_click)








    @pyqtSlot()
    def on_btn_clear_click(self):
        self.matrix.clear()

    @pyqtSlot()
    def on_btn_fill_click(self):
        color = QColorDialog.getColor()
        if color.isValid():
                self.matrix.fill([color.red(), color.green(), color.blue()])



    @pyqtSlot()
    def on_btn_start_running_text_click(self):
        self.matrix.start_frame_sequence(self.run_text_provider)
        print(self.scale)

    @pyqtSlot()
    def on_btn_stop_running_text_click(self):
        self.matrix.stop_frame_sequence()  # Kann ich hier auf einen Befehl iwie ausführen

    @pyqtSlot()
    def on_btn_start_video_click(self):
        self.matrix.start_frame_sequence(self.video_frame_provider)

    @pyqtSlot()
    def on_btn_stop_video_click(self):
        self.matrix.stop_frame_sequence()

    @pyqtSlot()
    def on_btn_start_picture_click(self):
        img_filename_and_filter = QFileDialog.getOpenFileName(caption="Select image file",
                                                              filter="Image files (*.jpg *.gif *.bmp *.png)")
        if img_filename_and_filter is not None:
            img_filename = img_filename_and_filter[0]
            if img_filename != "":
                img = cv2.imread(img_filename, cv2.IMREAD_COLOR)
                if img is not None:
                    img_frame: list = self.image_frame_builder.build_frame(img)
                    self.matrix.show_image_frame(img_frame)

    @pyqtSlot()
    def on_btn_stop_picture_click(self):
        pass

    @pyqtSlot()
    def on_btn_choose_file_1_click(self):
        pass

    @pyqtSlot()
    def on_btn_choose_file_2_click(self):
        pass

    def on_btn_simple_color_color_click(self):
        pass



    @pyqtSlot()
    def background_color_picker(self):
        color = QColorDialog.getColor()
        if color.isValid():
            print("Back Color = " + str(color))
            color_list = [color.red(), color.green(), color.blue()]
            self.BACKROUND_COLOR = color_list
            print("Back Color = " + str(self.BACKROUND_COLOR))

    @pyqtSlot()
    def text_color_picker(self):
        color = QColorDialog.getColor()
        if color.isValid():
            print("Text Color = " + str(color))
            color_list = [color.red(), color.green(), color.blue()]
            self.COLOR = color_list
            print("Text Color = " + str(self.COLOR))

    def _show_error_dialog(self, title: str, message: str):
        msg: QMessageBox = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.exec_()

    def _show_message_dialog(self, title: str, message: str):
        msg: QMessageBox = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.exec_()



