import struct


class PacketBuilder(object):

    PANEL_LED_COUNT: int = 350

    def build_master_time_packet(self, master_time_ms: float) -> bytearray:
        master_time_packet: bytearray = bytearray()
        # 8 bytes represent the master time
        # round time (float), pack it with little-Endian as unsigned long long (uint64_t in C/C++)
        master_time_packet += struct.pack('<Q', round(master_time_ms))
        return master_time_packet

    def build_frame_packet_with_all_leds_same_color(self, time_to_present_frame: float, color: list) -> bytearray:
        frame_packet: bytearray = bytearray()
        # first 8 bytes represent the master time at which the frame shall be presented
        # round time (float), pack it with little-Endian as unsigned long long (uint64_t in C/C++)
        frame_packet += struct.pack('<Q', round(time_to_present_frame))
        # following bytes represent pixel data; each pixel consists of 3 bytes for RGB
        for led in range(self.PANEL_LED_COUNT):
            frame_packet.append(color[0])
            frame_packet.append(color[1])
            frame_packet.append(color[2])
        return frame_packet

    def build_frame_packet(self, time_to_present_frame: float, pixel_data: bytearray) -> bytearray:
        frame_packet: bytearray = bytearray()
        # first 8 bytes represent the master time at which the frame shall be presented
        # round time (float), pack it with little-Endian as unsigned long long (uint64_t in C/C++)
        frame_packet += struct.pack('<Q', round(time_to_present_frame))
        # following bytes represent pixel data; each pixel consists of 3 bytes for RGB
        frame_packet += pixel_data
        return frame_packet

    def build_frame_packets(self, time_to_present_frame: float, frame: list) -> list:
        packets_to_transmit: list = []
        for panel_sub_frame in frame:
            pixel_data: bytearray = panel_sub_frame['pixel_data']
            endpoint: str = panel_sub_frame['endpoint']
            packet_to_transmit: dict = {
                'endpoint': endpoint,
                'packet_data': self.build_frame_packet(time_to_present_frame, pixel_data)
            }
            packets_to_transmit.append(packet_to_transmit)
        return packets_to_transmit
