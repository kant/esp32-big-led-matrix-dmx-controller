import cv2


class ImageFrameBuilder(object):

    PANEL_LED_COUNT: int = 350

    endpoints: list = []

    def __init__(self, endpoints: list):
        self.endpoints = endpoints

    def build_frame(self, image: object, endpoints: list) -> list:
        down_scaled_image = cv2.resize(image, (50, 28), interpolation=cv2.INTER_AREA)
        top_left_image = down_scaled_image[0:14, 0:25]
        top_right_image = down_scaled_image[0:14, 25:50]
        bottom_left_image = down_scaled_image[14:28, 0:25]
        bottom_right_image = down_scaled_image[14:28, 25:50]
        top_left_panel_sub_frame: dict = {
            'pixel_data': self._build_sub_panel_pixel_date(top_left_image),
            'endpoint': self.endpoints[0]
        }
        top_right_panel_sub_frame: dict = {
            'pixel_data': self._build_sub_panel_pixel_date(top_right_image),
            'endpoint': self.endpoints[1]
        }
        bottom_left_panel_sub_frame: dict = {
            'pixel_data': self._build_sub_panel_pixel_date(bottom_left_image),
            'endpoint': self.endpoints[2]
        }
        bottom_right_panel_sub_frame: dict = {
            'pixel_data': self._build_sub_panel_pixel_date(bottom_right_image),
            'endpoint': self.endpoints[3]
        }
        frame: list = []
        frame.append(top_left_panel_sub_frame)
        frame.append(top_right_panel_sub_frame)
        frame.append(bottom_left_panel_sub_frame)
        frame.append(bottom_right_panel_sub_frame)
        return frame

    def _build_sub_panel_pixel_date(self, image: object) -> bytearray:
        # only dummy implementation!
        return self._build_pixel_data([0, 255, 0])

    def _build_pixel_data(self, color: list) -> bytearray:
        pixel_data: bytearray = bytearray()
        # following bytes represent pixel data; each pixel consists of 3 bytes for RGB
        for led in range(self.PANEL_LED_COUNT):
            pixel_data.append(color[0])
            pixel_data.append(color[1])
            pixel_data.append(color[2])
        return pixel_data