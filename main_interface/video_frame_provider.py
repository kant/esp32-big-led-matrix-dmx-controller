import cv2

from matrix_controller import FrameProvider


class VideoFrameProvider(FrameProvider):

    PANEL_LED_COUNT: int = 350

    endpoints: list = []
    video_filename: str = ""
    video_capture: cv2.VideoCapture = None

    def __init__(self, endpoints: list, video_filename: str):
        FrameProvider.__init__(self)
        self.endpoints = endpoints
        self.video_filename = video_filename

    def prepare(self) -> None:
        self.video_capture = cv2.VideoCapture(self.video_filename)

    def provide_first(self) -> list:
        success, image = self.video_capture.read()
        if not success:
            print("### opencv video capture read failed")
            return []
        return self._build_frame(image)

    def provide_next(self, previous_frame: list) -> list:
        success, image = self.video_capture.read()
        if not success:
            # reached end of video; reopen it and start from the beginning
            self.video_capture.release()
            self.video_capture = cv2.VideoCapture(self.video_filename)
            success, image = self.video_capture.read()
            if not success:
                print("### opencv video capture read after reopening failed")
                return []
        return self._build_frame(image)

    def complete(self) -> None:
        self.video_capture.release()

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



    # def _build_pixel_data(self, color: list) -> bytearray:
    #     pixel_data: bytearray = bytearray()
    #     # following bytes represent pixel data; each pixel consists of 3 bytes for RGB
    #     for led in range(self.PANEL_LED_COUNT):
    #         pixel_data.append(color[0])
    #         pixel_data.append(color[1])
    #         pixel_data.append(color[2])
    #     return pixel_data