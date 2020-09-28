from matrix_controller import FrameProvider
import cv2
import numpy as np


class RunTextProvider(FrameProvider):

    PANEL_LED_COUNT: int = 350

    endpoints: list = []

    def __init__(self, endpoints: list, layout: int, text: str, background_color: list, scale: float,
                 color: list, thickness: int, font_family: str, speed: int,
                 matrix_width: int, matrix_height: int):

        FrameProvider.__init__(self)
        self.endpoints = endpoints
        self.text = text
        self.background_color = background_color
        self.scale = scale
        self.color = color
        self.thickness: int = int(thickness)
        self.font_family = font_family
        self.speed = speed
        self.x_add: int = 1
        self.matrix_width = matrix_width
        self.matrix_height = matrix_height
        self.x_temp = 0
        self.x = 50
        self.text_size = 1

    def prepare(self) -> None:
        # Calculate speed
        if self.speed == 1:
            self.x_add = 1
            # x + 0,5
        if self.speed == 2:
            self.x_add = 2
            # x + 1
        if self.speed == 3:
            self.x_add = 3
            # x + 1,5
        if self.speed == 4:
            self.x_add = 4
            # x + 2
        if self.speed == 5:
            self.x_add = 5
            # x + 2,5

        # # Calculate Start point
        self.text_size = self.create_frame_with_text(1)[1]
        # self.x = 0 - self.text_size[0]

    def provide_first(self) -> list:
        image = self.create_frame_with_text(self.x)[0]

        return self._build_frame(image)

    def provide_next(self, previous_frame: list) -> list:
        if self.x < 0 - self.text_size[0]:
            # self.x = 0 - self.text_size[0]
            self.x = 50

        print("next: X = " + str(self.x))
        image = self.create_frame_with_text(self.x)[0]

        self.x = self.x - self.x_add

        return self._build_frame(image)

    def complete(self) -> None:
        pass

    def _build_frame(self, image: object) -> list:
        down_scaled_image = cv2.resize(image, (50, 28), interpolation=cv2.INTER_AREA)
        top_left_image = down_scaled_image[0:14, 0:25]
        top_right_image = down_scaled_image[0:14, 25:50]
        bottom_left_image = down_scaled_image[14:28, 0:25]
        bottom_right_image = down_scaled_image[14:28, 25:50]
        top_left_panel_sub_frame: dict = {
            'pixel_data': self._build_sub_panel_pixel_data(top_left_image),
            'endpoint': self.endpoints[0]
        }
        top_right_panel_sub_frame: dict = {
            'pixel_data': self._build_sub_panel_pixel_data(top_right_image),
            'endpoint': self.endpoints[1]
        }
        bottom_left_panel_sub_frame: dict = {
            'pixel_data': self._build_sub_panel_pixel_data(bottom_left_image),
            'endpoint': self.endpoints[2]
        }
        bottom_right_panel_sub_frame: dict = {
            'pixel_data': self._build_sub_panel_pixel_data(bottom_right_image),
            'endpoint': self.endpoints[3]
        }
        frame: list = []
        frame.append(top_left_panel_sub_frame)
        frame.append(top_right_panel_sub_frame)
        frame.append(bottom_left_panel_sub_frame)
        frame.append(bottom_right_panel_sub_frame)
        return frame

    def _build_sub_panel_pixel_data(self, image) -> bytearray:
        package = bytearray()
        height: int = image.shape[0]
        width: int = image.shape[1]
        for x in range(0, height, 2):
            for y in range(0, width, 1):
                b, g, r = (image[x, y])
                package.append(r)
                package.append(g)
                package.append(b)
                # pixel__arr = [r, g, b]
                # binary_format = bytearray(pixel__arr)
                # p1_bin_file.write(binary_format)

            x = x + 1
            for y in range(width - 1, -1, -1):
                b, g, r = (image[x, y])
                package.append(r)
                package.append(g)
                package.append(b)
                # pixel__arr = [r, g, b]
                # binary_format = bytearray(pixel__arr)
                # p1_bin_file.write(binary_format)

        return package


    def create_frame_with_text(self, x:int):
        width = self.matrix_width
        height = self.matrix_height

        im = np.zeros((height, width, 3), np.uint8)
        im[:] = color = [self.background_color[2], self.background_color[1], self.background_color[0]]

        font = cv2.FONT_HERSHEY_SIMPLEX  # Font of the text
        textsize = cv2.getTextSize(self.text, font, self.scale, self.thickness)[0]  # get text size

        y = height / 2 + textsize[1] / 2

        position = (x, int(y))  # Text position

        cv2.putText(im, self.text, position, font, self.scale, [self.color[2], self.color[1], self.color[0]],
                    self.thickness, cv2.LINE_4)

        return [im, textsize]

