import typing
import os
from time import sleep

import ntpath

import cv2
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QColorDialog, QMessageBox, QFileDialog
from PyQt5 import uic


from matrix_controller import Matrix
from fading_color_frame_provider import FadingColorFrameProvider
from video_frame_provider import VideoFrameProvider
from run_text_provider import RunTextProvider
from picture_provider import PictureProvider


class MainWindow(QMainWindow):
    LAYOUT = 1

    # Initialize Endpoints
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
    picture_provider: PictureProvider = None

    def __init__(self) -> None:
        self.matrix.configure(self.ENDPOINTS)
        QMainWindow.__init__(self)
        self.python_file_path = os.path.dirname(os.path.abspath(__file__))
        self._init_window_design()

        # Variables
        self.TEXT = "Hello World"
        self.BACKGROUND_COLOR = [255, 255, 255]
        self.SCALE = 1
        self.COLOR = [0, 0, 0]
        self.THICKNESS = 1
        self.FONT_FAMILY = "dummy"
        self.SPEED = 1
        self.MATRIX_WIDTH = 50
        self.MATRIX_HEIGHT = 28

        self.VIDEO_FILENAME: str = "dummy.mp4"

        # initialize providers
        self.run_text_provider = RunTextProvider(self.ENDPOINTS, self.LAYOUT, self.TEXT, self.BACKGROUND_COLOR,
                                                 self.SCALE, self.COLOR, self.THICKNESS, self.FONT_FAMILY, self.SPEED,
                                                 self.MATRIX_WIDTH, self.MATRIX_HEIGHT)
        self.video_frame_provider = VideoFrameProvider(self.ENDPOINTS, self.VIDEO_FILENAME)
        self.picture_provider = PictureProvider(self.ENDPOINTS)

        # Show Window
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
        # line edits
        self.TEXT = self.edt_text.text()
        self.SCALE = self.edt_scale.text()
        self.THICKNESS = self.edt_thickness.text()
        self.SPEED = self.edt_speed.text()

        # additional effects
        self.btn_start_rainbow.clicked.connect(self.on_btn_start_rainbow_click)
        self.btn_stop_rainbow.clicked.connect(self.on_btn_stop_rainbow_click)
        self.btn_start_simple_color.clicked.connect(self.on_btn_start_simple_color_click)
        self.btn_stop_simple_color.clicked.connect(self.on_btn_stop_simple_color_click)
        self.btn_start_fading_pixels.clicked.connect(self.on_btn_start_fading_pixels_click)
        self.btn_stop_fading_pixels.clicked.connect(self.on_btn_stop_fading_pixels_click)
        self.btn_start_audio_meter.clicked.connect(self.on_btn_start_audio_meter_click)
        self.btn_stop_audio_meter.clicked.connect(self.on_btn_stop_audio_meter_click)

    # Clear
    @pyqtSlot()
    def on_btn_clear_click(self):
        self.matrix.clear()

    # Main
    @pyqtSlot()
    def on_btn_start_running_text_click(self):
        print("Text: " + str(self.edt_text.text()))
        print("Scale: " + str(self.edt_scale.text()))
        print("Thickness: " + str(self.edt_thickness.text()))
        print("Speed: " + str(self.edt_speed.text()))
        print("Background - Color: " + str(self.BACKGROUND_COLOR))
        print("Color: " + str(self.COLOR))
        self.matrix.start_frame_sequence(self.run_text_provider)

    @pyqtSlot()
    def on_btn_stop_running_text_click(self):
        self.matrix.stop_frame_sequence()

    @pyqtSlot()
    def on_btn_start_video_click(self):
        filename = QFileDialog.getOpenFileName(caption="Select video file", filter="Video files (*.mp4)")
        head, tail = ntpath.split(filename[0])
        self.VIDEO_FILENAME = ntpath.basename(tail)

        print("Video filename constant = " + str(self.VIDEO_FILENAME))
        print("result of filename = " + str(filename))
        print("Video filename temp = " + str(filename[0]))

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
                    img = self._make_cartoon_image(img)
                    picture: list = self.picture_provider.build_frame(img)
                    self.matrix.show_image_frame(picture)

    @pyqtSlot()
    def on_btn_stop_picture_click(self):
        pass


    # Effects
    @pyqtSlot()
    def on_btn_start_rainbow_click(self):
        pass

    @pyqtSlot()
    def on_btn_stop_rainbow_click(self):
        pass

    @pyqtSlot()
    def on_btn_start_simple_color_click(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.matrix.fill([color.red(), color.green(), color.blue()])

    @pyqtSlot()
    def on_btn_stop_simple_color_click(self):
        self.matrix.clear()

    @pyqtSlot()
    def on_btn_start_fading_pixels_click(self):
        pass

    @pyqtSlot()
    def on_btn_stop_fading_pixels_click(self):
        pass

    @pyqtSlot()
    def on_btn_start_audio_meter_click(self):
        pass

    @pyqtSlot()
    def on_btn_stop_audio_meter_click(self):
        pass

    # Functions
    def background_color_picker(self):
        color = QColorDialog.getColor()
        if color.isValid():
            print("Back Color = " + str(color))
            color_list = [color.red(), color.green(), color.blue()]
            self.BACKGROUND_COLOR = color_list
            print("Back Color = " + str(self.BACKGROUND_COLOR))


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


############################################

#   Video geht net (frame que empty)
#   Picture geht net (stürtzt ab)
#   RUnning text geth (nimmt keine Argumete)
#
#
#
#
