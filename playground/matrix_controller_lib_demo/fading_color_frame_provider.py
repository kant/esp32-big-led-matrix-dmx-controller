from matrix_controller import FrameProvider


class FadingColorFrameProvider(FrameProvider):

    PANEL_LED_COUNT: int = 350

    endpoints: list = []
    color_red: int = 0
    color_green: int = 0
    color_blue: int = 0
    color_to_vary: int = 0

    def __init__(self, endpoints: list):
        FrameProvider.__init__(self)
        self.endpoints = endpoints
        self._init_colors()

    def prepare(self) -> None:
        self._init_colors()

    def provide_first(self) -> list:
        color: list = [self.color_red, self.color_green, self.color_blue]
        return self._build_frame(color)

    def provide_next(self, previous_frame: list) -> list:
        if self.color_to_vary == 0:
            self.color_red += 10
            if self.color_red > 255:
                self.color_red = 0
                self.color_to_vary += 1
        elif self.color_to_vary == 1:
            self.color_green += 10
            if self.color_green > 255:
                self.color_green = 0
                self.color_to_vary += 1
        else:
            self.color_blue += 10
            if self.color_blue > 255:
                self.color_blue = 0
                self.color_to_vary += 1

        if self.color_to_vary > 2:
            self.color_to_vary = 0

        color: list = [self.color_red, self.color_green, self.color_blue]
        return self._build_frame(color)

    def complete(self) -> None:
        pass

    def _init_colors(self):
        self.color_red = 0
        self.color_green = 0
        self.color_blue = 0
        self.color_to_vary = 0

    def _build_frame(self, color: list) -> list:
        frame: list = []
        for endpoint in self.endpoints:
            panel_sub_frame: dict = {
                'pixel_data': self._build_pixel_data(color),
                'endpoint': endpoint
            }
            frame.append(panel_sub_frame)
        return frame

    def _build_pixel_data(self, color: list) -> bytearray:
        pixel_data: bytearray = bytearray()
        # following bytes represent pixel data; each pixel consists of 3 bytes for RGB
        for led in range(self.PANEL_LED_COUNT):
            pixel_data.append(color[0])
            pixel_data.append(color[1])
            pixel_data.append(color[2])
        return pixel_data