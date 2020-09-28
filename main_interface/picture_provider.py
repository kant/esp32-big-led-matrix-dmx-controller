import cv2


class PictureProvider(object):
    IMAGE_WIDTH: int = 50  # must be multiples of 2
    IMAGE_HEIGHT: int = 28  # must be multiples of 2
    PANEL_LED_COUNT: int = (IMAGE_WIDTH * IMAGE_HEIGHT) / 4  # matrix of 2x2 panels is expected
    # matrix layout:
    # [0 1]
    # [2 3]

    endpoints: list = []

    def __init__(self, endpoints: list):
        self.endpoints = endpoints

    def build_frame(self, image: object) -> list:
        down_scaled_image = cv2.resize(image, (self.IMAGE_WIDTH, self.IMAGE_HEIGHT), interpolation=cv2.INTER_AREA)
        top_left_image = down_scaled_image[0:int(self.IMAGE_HEIGHT/2),
                                           0:int(self.IMAGE_WIDTH/2)]
        top_right_image = down_scaled_image[0:int(self.IMAGE_HEIGHT/2),
                                            int(self.IMAGE_WIDTH/2):self.IMAGE_WIDTH]
        bottom_left_image = down_scaled_image[int(self.IMAGE_HEIGHT/2):self.IMAGE_HEIGHT,
                                              0:int(self.IMAGE_WIDTH/2)]
        bottom_right_image = down_scaled_image[int(self.IMAGE_HEIGHT/2):self.IMAGE_HEIGHT,
                                               int(self.IMAGE_WIDTH/2):self.IMAGE_WIDTH]
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
        pixel_data: bytearray = bytearray()
        for row in range(int(self.IMAGE_HEIGHT/2)):
            for col in range(int(self.IMAGE_WIDTH/2)):
                x: int = col
                if (row % 2) != 0:
                    # row index is odd (1, 3, 5, 6, ...), leds are mounted from right to left
                    x = int(self.IMAGE_WIDTH/2) - 1 - col
                pixel_data.extend(self._get_pixel_color_bytes(image, x, row))
        return pixel_data

    def _get_pixel_color_bytes(self, image: object, x: int, y: int) -> bytearray:
        pixel_color_bytes: bytearray = bytearray()
        pixel_color_bytes.append(image[y, x, 2])
        pixel_color_bytes.append(image[y, x, 1])
        pixel_color_bytes.append(image[y, x, 0])
        return pixel_color_bytes
