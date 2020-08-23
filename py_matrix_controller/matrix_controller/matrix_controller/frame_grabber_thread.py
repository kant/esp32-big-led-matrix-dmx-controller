import time
import threading

from time import sleep

from .frame_queue import FrameQueue
from .frame_provider import FrameProvider


class FrameGrabberThread(threading.Thread):

    FRAME_DISTANCE: int = 40    # 40ms / 25fps

    stop_event: threading.Event = threading.Event()     # event to signal the thread that it should stop
    frame_provider: FrameProvider = None                # frame provider instance used by the thread to grab the frames
    frame_queue: FrameQueue = None                      # queue to hold frames

    def __init__(self, frame_provider: FrameProvider, frame_queue: FrameQueue):
        threading.Thread.__init__(self)
        self.frame_provider = frame_provider
        self.frame_queue = frame_queue

    def run(self):
        self.stop_event.clear()
        self._prepare()
        # grab the first frame and add it to the queue
        frame: list = self._grab_first()
        self._add_to_frame_queue(frame)
        while not self.stop_event.is_set():
            # grab the next frame and add it to the queue
            frame: list = self._grab_next(frame)
            self._add_to_frame_queue(frame)
        self._complete()

    def _prepare(self) -> None:
        self.frame_provider.prepare()

    def _add_to_frame_queue(self, frame_packets: list):
        while (not self.frame_queue.add(frame_packets)) and (not self.stop_event.is_set()):
            sleep(self.FRAME_DISTANCE / 1000.0)

    def _grab_first(self) -> list:
        return self.frame_provider.provide_first()

    def _grab_next(self, previous_frame: list) -> list:
        return self.frame_provider.provide_next(previous_frame)

    def _complete(self) -> None:
        self.frame_provider.complete()

    def stop_and_wait(self) -> None:
        # signal the thread to stop
        self.stop_event.set()
        # wait until the thread stopped
        while self.is_alive():
            sleep(0.01)
