import socket


class UdpConnection(object):

    udp_socket: socket.socket = None

    def open(self) -> None:
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
        self.udp_socket.settimeout(5)

    def send_packet(self, endpoint: dict, packet: bytearray) -> None:
        self.udp_socket.sendto(packet, (endpoint['ip_address'], endpoint['port']))

    def send_packets(self, packets: list) -> None:
        for packet in packets:
            self.send_packet(packet['endpoint'], packet['packet_data'])

    def close(self) -> None:
        self.udp_socket.close()
        self.udp_socket = None
