import time
import threading

from time import sleep

from .udp_connection import UdpConnection
from .packet_builder import PacketBuilder
from .frame_queue import FrameQueue


class FrameSenderThread(threading.Thread):

    MASTER_TIME_OFFSET: int = 100           # 100ms
    MASTER_TIME_SYNC_INTERVAL: int = 1000   # 1000ms
    FRAME_DISTANCE: int = 40                # 40ms / 25fps

    connection: UdpConnection = UdpConnection()               # connection object to handle UDP communication
    packet_builder: PacketBuilder = PacketBuilder()     # packet builder to prepare packets the are sent over UDP

    stop_event: threading.Event = threading.Event()     # event to signal the thread that it should stop
    frame_queue: FrameQueue = None                      # queue to hold frames
    endpoints: list                                     # list of endpoints

    def __init__(self, frame_queue: FrameQueue, endpoints: list):
        threading.Thread.__init__(self)
        self.frame_queue = frame_queue
        self.endpoints = endpoints

    def run(self):
        self.stop_event.clear()
        self.connection.open()

        master_time_ms: float = self._broadcast_master_time()
        next_transmission_time_ms: float = master_time_ms

        last_send_time_packet_time: float = master_time_ms

        while not self.stop_event.is_set():
            frame: list = self.frame_queue.fetch()
            if len(frame) > 0:
                # prepare packets for transmission
                time_to_present_frame: float = next_transmission_time_ms + self.MASTER_TIME_OFFSET
                packets_to_transmit: list = []
                for panel_sub_frame in frame:
                    pixel_data: bytearray = panel_sub_frame['pixel_data']
                    endpoint: str = panel_sub_frame['endpoint']
                    packet_to_transmit: dict = {
                        'endpoint': endpoint,
                        'packet_data': self.packet_builder.build_frame_packet(time_to_present_frame, pixel_data)
                    }
                    packets_to_transmit.append(packet_to_transmit)

                # calculate wait time
                wait_time_ms: float = (next_transmission_time_ms - self._get_current_time_ms())
                if wait_time_ms > 0.0:
                    # wait
                    sleep(wait_time_ms / 1000.0)
                else:
                    # wait time is negative; so we are behind the schedule;
                    # check if this might be caught up or if the schedule should be adjusted
                    time_behind_ms: float = \
                        abs(wait_time_ms) - (5 * self.FRAME_DISTANCE) # 5 times frame distance tolerance
# DEBUG
                    print("### behind schedule for {0} ms".format(abs(wait_time_ms)))
                    if time_behind_ms > 0.0:
                        # tolerance overshot, so adjust the schedule by 2 frames
                        next_transmission_time_ms += (2 * self.FRAME_DISTANCE)
# DEBUG
                        print("### adjusted schedule by 2 frames")

                # transmit
                for packet in packets_to_transmit:
                    self.connection.send_packet(packet['endpoint'], packet['packet_data'])

                # schedule next transmission
                next_transmission_time_ms += self.FRAME_DISTANCE
# DEBUG
            else:
                print("### frame queue is empty")

            # cyclically broadcast updates of the master time
            current_time_ms: float = self._get_current_time_ms()
            if (current_time_ms - last_send_time_packet_time) > self.MASTER_TIME_SYNC_INTERVAL:
                last_send_time_packet_time = current_time_ms
                self._broadcast_master_time()

        self.connection.close()

    def _broadcast_master_time(self) -> float:
        master_time_ms = self._get_current_time_ms()
        master_time_packet = self.packet_builder.build_master_time_packet(master_time_ms)
        for endpoint in self.endpoints: # type:str
            self.connection.send_packet(endpoint, master_time_packet)
        return master_time_ms

    def _get_current_time_ms(self) -> float:
        return time.time() * 1000

    def stop_and_wait(self) -> None:
        # signal the thread to stop
        self.stop_event.set()
        # wait until the thread stopped
        while self.is_alive():
            sleep(0.01)
