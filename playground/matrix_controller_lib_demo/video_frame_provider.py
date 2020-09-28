import cv2

from matrix_controller import FrameProvider
from image_frame_builder import ImageFrameBuilder


class VideoFrameProvider(FrameProvider):

    PANEL_LED_COUNT: int = 350

    endpoints: list = []
    video_filename: str = ""
    video_capture: cv2.VideoCapture = None
    image_frame_builder: ImageFrameBuilder = None

    def __init__(self, endpoints: list, video_filename: str):
        FrameProvider.__init__(self)
        self.endpoints = endpoints
        self.video_filename = video_filename
        self.image_frame_builder = ImageFrameBuilder(self.endpoints)

    def prepare(self) -> None:
        self.video_capture = cv2.VideoCapture(self.video_filename)

    def provide_first(self) -> list:
        success, image = self.video_capture.read()
        if not success:
            print("### opencv video capture read failed")
            return []
        return self.image_frame_builder.build_frame(image, self.endpoints)

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
        return self.image_frame_builder.build_frame(image, self.endpoints)

    def complete(self) -> None:
        self.video_capture.release()
