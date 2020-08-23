import queue


class FrameQueue(object):

    MAX_QUEUE_SIZE: int = 10

    frame_queue: queue.Queue = queue.Queue(MAX_QUEUE_SIZE)    # some thread-safe queue

    def add(self, frame: list) -> bool:
        if not self.frame_queue.full():
            self.frame_queue.put(frame)
            return True
        else:
            return False

    def fetch(self) -> list:
        if not self.frame_queue.empty():
            return self.frame_queue.get()
        else:
            return []

    def clear(self) -> None:
        while not self.frame_queue.empty():
            self.frame_queue.get()
