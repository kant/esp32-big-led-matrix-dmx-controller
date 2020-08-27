import typing
import os

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QColorDialog
from PyQt5 import uic

from matrix_controller import Matrix
from fading_color_frame_provider import FadingColorFrameProvider
from video_frame_provider import VideoFrameProvider


class MainWindow(QMainWindow):

    ENDPOINTS: list = ["192.168.2.158", "192.168.2.159", "192.168.2.161", "192.168.2.157"]
    VIDEO_FILENAME: str = "Homer.mp4"

    python_file_path: str = ""
    matrix: Matrix = Matrix()
    fading_color_frame_provider: FadingColorFrameProvider = None
    video_frame_provider: VideoFrameProvider = None

    def __init__(self) -> None:
        QMainWindow.__init__(self)
        self.python_file_path = os.path.dirname(os.path.abspath(__file__))
        self._init_window_design()
        self.fading_color_frame_provider = FadingColorFrameProvider(self.ENDPOINTS)
        self.video_frame_provider = VideoFrameProvider(self.ENDPOINTS, self.VIDEO_FILENAME)
        self.show()

    def _init_window_design(self) -> None:
        uic.loadUi(os.path.join(self.python_file_path, "main_window.ui"), self)
        self.btn_configure.clicked.connect(self.on_btn_configure_click)
        self.btn_clear.clicked.connect(self.on_btn_clear_click)
        self.btn_fill.clicked.connect(self.on_btn_fill_click)
        self.btn_start_color_fading.clicked.connect(self.on_btn_start_color_fading_click)
        self.btn_stop_color_fading.clicked.connect(self.on_btn_stop_color_fading_click)
        self.btn_start_video.clicked.connect(self.on_btn_start_video_click)
        self.btn_stop_video.clicked.connect(self.on_btn_stop_video_click)

    @pyqtSlot()
    def on_btn_configure_click(self):
        self.matrix.configure(self.ENDPOINTS)

    @pyqtSlot()
    def on_btn_clear_click(self):
        self.matrix.clear()

    @pyqtSlot()
    def on_btn_fill_click(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.matrix.fill([color.red(), color.green(), color.blue()])

    @pyqtSlot()
    def on_btn_start_color_fading_click(self):
        self.matrix.start_frame_sequence(self.fading_color_frame_provider)

    @pyqtSlot()
    def on_btn_stop_color_fading_click(self):
        self.matrix.stop_frame_sequence()

    @pyqtSlot()
    def on_btn_start_video_click(self):
        self.matrix.start_frame_sequence(self.video_frame_provider)

    @pyqtSlot()
    def on_btn_stop_video_click(self):
        self.matrix.stop_frame_sequence()
