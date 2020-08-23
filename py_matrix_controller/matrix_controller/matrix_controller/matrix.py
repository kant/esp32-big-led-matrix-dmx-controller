import time

from .connection import Connection
from .packet_builder import PacketBuilder
from .frame_scheduler import FrameScheduler
from .frame_provider import FrameProvider


class Matrix(object):

    MASTER_TIME_OFFSET: int = 50    # 50ms
    BLACK_COLOR: list = [0, 0, 0]   # all LEDs black

    endpoints: list = []
    connection: Connection = Connection()
    packet_builder: PacketBuilder = PacketBuilder()
    frame_scheduler: FrameScheduler = None

    def configure(self, endpoints: list) -> None:
        print("Matrix.configure() called with end_points = {0}".format(endpoints))
        self.endpoints = endpoints

    def fill(self, color: list) -> None:
        print("Matrix.fill() called with color = {0}".format(color))
        if len(self.endpoints) > 0:
            self.connection.open()
            master_time_ms: float = self._broadcast_master_time()
            time_to_present_frame: float = master_time_ms + self.MASTER_TIME_OFFSET
            frame_packet: bytearray = \
                self.packet_builder.build_frame_packet_with_all_leds_same_color(time_to_present_frame, color)
            self._send_frame_packet(frame_packet)
            self.connection.close()

    def _broadcast_master_time(self) -> float:
        master_time_ms = self._get_current_time_ms()
        master_time_packet = self.packet_builder.build_master_time_packet(master_time_ms)
        self.connection.broadcast(master_time_packet)
        return master_time_ms

    def _get_current_time_ms(self) -> float:
        return time.time() * 1000

    def _send_frame_packet(self, frame_packet: bytearray) -> None:
        for endpoint in self.endpoints: # type:str
            self.connection.send_packet(endpoint, frame_packet)

    def clear(self) -> None:
        print("Matrix.clear() called")
        self.fill(self.BLACK_COLOR)

    def start_frame_sequence(self, frame_provider: FrameProvider) -> None:
        print("Matrix.start_frame_sequence() called")
        self.frame_scheduler = FrameScheduler(frame_provider)
        self.frame_scheduler.start()

    def stop_frame_sequence(self) -> None:
        print("Matrix.stop_frame_sequence() called")
        if self.frame_scheduler is not None:
            self.frame_scheduler.stop_and_wait()
