import typing
import os
from time import sleep

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QColorDialog, QMessageBox, QFileDialog
from PyQt5 import uic

import cv2

from matrix_controller import Matrix
from image_frame_builder import ImageFrameBuilder
from fading_color_frame_provider import FadingColorFrameProvider
from video_frame_provider import VideoFrameProvider


class MainWindow(QMainWindow):

    ENDPOINTS: list = [
        {'ip_address': "192.168.2.158",
         'port': 50000},
        {'ip_address': "192.168.2.159",
         'port': 50000},
        {'ip_address': "192.168.2.161",
         'port': 50000},
        {'ip_address': "192.168.2.157",
         'port': 50000}]
    VIDEO_FILENAME: str = "Homer.mp4"

    python_file_path: str = ""
    matrix: Matrix = Matrix()
    image_frame_builder: ImageFrameBuilder = None
    fading_color_frame_provider: FadingColorFrameProvider = None
    video_frame_provider: VideoFrameProvider = None

    def __init__(self) -> None:
        QMainWindow.__init__(self)
        self.python_file_path = os.path.dirname(os.path.abspath(__file__))
        self._init_window_design()
        self.image_frame_builder = ImageFrameBuilder(self.ENDPOINTS)
        self.fading_color_frame_provider = FadingColorFrameProvider(self.ENDPOINTS)
        self.video_frame_provider = VideoFrameProvider(self.ENDPOINTS, self.VIDEO_FILENAME)
        self.show()

    def _init_window_design(self) -> None:
        uic.loadUi(os.path.join(self.python_file_path, "main_window.ui"), self)
        self.btn_configure.clicked.connect(self.on_btn_configure_click)
        self.btn_clear.clicked.connect(self.on_btn_clear_click)
        self.btn_fill.clicked.connect(self.on_btn_fill_click)
        self.btn_show_image.clicked.connect(self.on_btn_show_image_click)
        self.btn_show_image_with_cartoon_effect.clicked.connect(self.on_btn_show_image_with_cartoon_effect_click)
        self.btn_start_color_fading.clicked.connect(self.on_btn_start_color_fading_click)
        self.btn_stop_color_fading.clicked.connect(self.on_btn_stop_color_fading_click)
        self.btn_start_video.clicked.connect(self.on_btn_start_video_click)
        self.btn_stop_video.clicked.connect(self.on_btn_stop_video_click)
        self.btn_get_network_settings.clicked.connect(self.on_btn_get_network_settings_click)
        self.btn_set_network_settings.clicked.connect(self.on_btn_set_network_settings_click)

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
    def on_btn_show_image_click(self):
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
    def on_btn_show_image_with_cartoon_effect_click(self):
        img_filename_and_filter = QFileDialog.getOpenFileName(caption="Select image file",
                                                              filter="Image files (*.jpg *.gif *.bmp *.png)")
        if img_filename_and_filter is not None:
            img_filename = img_filename_and_filter[0]
            if img_filename != "":
                img = cv2.imread(img_filename, cv2.IMREAD_COLOR)
                if img is not None:
                    img = self._make_cartoon_image(img)
                    img_frame: list = self.image_frame_builder.build_frame(img)
                    self.matrix.show_image_frame(img_frame)

    def _make_cartoon_image(self, img):
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred_img = cv2.medianBlur(gray_img, 5)
        edges_img = cv2.adaptiveThreshold(blurred_img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 5)
        homogen_colors2_img = cv2.bilateralFilter(img, 9, 300, 300)
        cartoon_img = cv2.bitwise_and(homogen_colors2_img, homogen_colors2_img, mask=edges_img)
        return cartoon_img

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

    @pyqtSlot()
    def on_btn_get_network_settings_click(self):
        ip_address: str = self.edt_ip_address.text()
        received_network_settings: dict = {}

        success: bool = self.matrix.get_network_settings(ip_address, received_network_settings)

        if not success:
            self._show_error_dialog("Error", "Getting network settings failed")
        else:
            use_dhcp: bool = received_network_settings['use_dhcp']
            self.chb_use_dhcp.setChecked(use_dhcp)
            mac_address: str = received_network_settings['mac_address']
            self.edt_mac_address.setText(mac_address)
            static_ip_address: str = received_network_settings['ip_address']
            self.edt_static_ip_address.setText(static_ip_address)
            subnet_mask: str = received_network_settings['subnet_mask']
            self.edt_subnet_mask.setText(subnet_mask)
            gateway: str = received_network_settings['gateway']
            self.edt_gateway.setText(gateway)
            dns_server: str = received_network_settings['dns_server']
            self.edt_dns_server.setText(dns_server)
            self._show_message_dialog("Information", "Received network settings")

    @pyqtSlot()
    def on_btn_set_network_settings_click(self):
        ip_address: str = self.edt_ip_address.text()

        new_network_settings: dict = {}
        use_dhcp: bool = self.chb_use_dhcp.isChecked()
        new_network_settings['use_dhcp'] = use_dhcp
        static_ip_address: str = self.edt_static_ip_address.text()
        new_network_settings['ip_address'] = static_ip_address
        subnet_mask: str = self.edt_subnet_mask.text()
        new_network_settings['subnet_mask'] = subnet_mask
        gateway: str = self.edt_gateway.text()
        new_network_settings['gateway'] = gateway
        dns_server: str = self.edt_dns_server.text()
        new_network_settings['dns_server'] = dns_server

        success: bool = self.matrix.set_network_settings(ip_address, new_network_settings)
        if not success:
            self._show_error_dialog("Error", "Setting network settings failed")
        else:
            self._show_message_dialog("Information", "Sent network settings, waiting 10 seconds for restart.")
            sleep(10)

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
