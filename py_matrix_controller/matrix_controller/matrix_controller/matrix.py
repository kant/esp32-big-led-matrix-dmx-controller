import time

from .tcp_connection import TcpConnection
from .udp_connection import UdpConnection
from .packet_builder import PacketBuilder
from .frame_scheduler import FrameScheduler
from .frame_provider import FrameProvider


class Matrix(object):

    MASTER_TIME_OFFSET: int = 100   # 100ms
    BLACK_COLOR: list = [0, 0, 0]   # all LEDs black

    endpoints: list = []
    udp_connection: UdpConnection = UdpConnection()
    tcp_connection: TcpConnection = TcpConnection()
    packet_builder: PacketBuilder = PacketBuilder()
    frame_scheduler: FrameScheduler = None

    def configure(self, endpoints: list) -> None:
        print("Matrix.configure() called with end_points = {0}".format(endpoints))
        self.endpoints = endpoints

    def fill(self, color: list) -> None:
        print("Matrix.fill() called with color = {0}".format(color))
        if len(self.endpoints) > 0:
            self.udp_connection.open()
            master_time_ms: float = self._broadcast_master_time()
            time_to_present_frame: float = master_time_ms + self.MASTER_TIME_OFFSET
            frame_packet: bytearray = \
                self.packet_builder.build_frame_packet_with_all_leds_same_color(time_to_present_frame, color)
            self._send_frame_packet(frame_packet)
            self.udp_connection.close()

    def _broadcast_master_time(self) -> float:
        master_time_ms = self._get_current_time_ms()
        master_time_packet = self.packet_builder.build_master_time_packet(master_time_ms)
        for endpoint in self.endpoints:     # type: dict
            self.udp_connection.send_packet(endpoint, master_time_packet)
        return master_time_ms

    def _get_current_time_ms(self) -> float:
        return time.time() * 1000

    def _send_frame_packet(self, frame_packet: bytearray) -> None:
        for endpoint in self.endpoints:     # type: dict
            self.udp_connection.send_packet(endpoint, frame_packet)

    def show_image_frame(self, img_frame: list) -> None:
        print("Matrix.show_image_frame() called with img_frame = {0}".format(img_frame))
        if len(self.endpoints) > 0:
            self.udp_connection.open()
            master_time_ms: float = self._broadcast_master_time()
            time_to_present_frame: float = master_time_ms + self.MASTER_TIME_OFFSET

# TODO: bis auf img_frame ist dieser Code identisch mit dem Code in frame_sender_thread.py; Code-Duplizierung aufheben!
            packets_to_transmit: list = []
            for panel_sub_frame in img_frame:
                pixel_data: bytearray = panel_sub_frame['pixel_data']
                endpoint: str = panel_sub_frame['endpoint']
                packet_to_transmit: dict = {
                    'endpoint': endpoint,
                    'packet_data': self.packet_builder.build_frame_packet(time_to_present_frame, pixel_data)
                }
                packets_to_transmit.append(packet_to_transmit)

# TODO: dieser Code ist identisch mit dem Code in frame_sender_thread.py; Code-Duplizierung aufheben!
            for packet in packets_to_transmit:
                self.udp_connection.send_packet(packet['endpoint'], packet['packet_data'])

            self.udp_connection.close()

    def clear(self) -> None:
        print("Matrix.clear() called")
        self.fill(self.BLACK_COLOR)

    def start_frame_sequence(self, frame_provider: FrameProvider) -> None:
        print("Matrix.start_frame_sequence() called")
        self.frame_scheduler = FrameScheduler(frame_provider, self.endpoints)
        self.frame_scheduler.start()

    def stop_frame_sequence(self) -> None:
        print("Matrix.stop_frame_sequence() called")
        if self.frame_scheduler is not None:
            self.frame_scheduler.stop_and_wait()

    def get_network_settings(self, ip_address: str, received_network_settings: dict) -> bool:
        print("Matrix.get_network_settings() called")
        return self.tcp_connection.send_cmd_get_network_settings(ip_address, received_network_settings)

    def set_network_settings(self, ip_address: str, new_network_settings: dict) -> bool:
        print("Matrix.set_network_settings() called")
        return self.tcp_connection.send_cmd_set_network_settings(ip_address, new_network_settings)
