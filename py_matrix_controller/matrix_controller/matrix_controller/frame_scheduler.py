from time import sleep

from .frame_grabber_thread import FrameGrabberThread
from .frame_queue import FrameQueue
from .frame_sender_thread import  FrameSenderThread
from .frame_provider import FrameProvider


class FrameScheduler(object):
    GRABBER_LEAD_TIME_MS: int = 50     # 50ms lead time for the grabber thread before transmission starts

    frame_grabber_thread: FrameGrabberThread
    frame_queue: FrameQueue
    frame_sender_thread: FrameSenderThread
    frame_provider: FrameProvider

    def __init__(self, frame_provider: FrameProvider, endpoints: list):
        self.frame_provider = frame_provider
        self.frame_queue = FrameQueue()
        self.frame_grabber_thread = FrameGrabberThread(self.frame_provider, self.frame_queue)
        self.frame_sender_thread = FrameSenderThread(self.frame_queue, endpoints)

    def start(self) -> None:
        self.frame_queue.clear()
        self.frame_grabber_thread.start()
        sleep(self.GRABBER_LEAD_TIME_MS / 1000.0)
        self.frame_sender_thread.start()

    def stop_and_wait(self) -> None:
        self.frame_sender_thread.stop_and_wait()
        self.frame_grabber_thread.stop_and_wait()
