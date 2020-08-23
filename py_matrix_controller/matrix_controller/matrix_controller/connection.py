import socket

class Connection(object):

    UDP_PORT: int = 50000

    udp_socket: socket.socket = None

    def open(self) -> None:
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
        self.udp_socket.settimeout(5)

    def broadcast(self, packet: bytearray) -> None:
        self.udp_socket.sendto(packet, ("<broadcast>", self.UDP_PORT))

    def send_packet(self, endpoint: str, packet: bytearray) -> None:
        self.udp_socket.sendto(packet, (endpoint, self.UDP_PORT))

    def close(self) -> None:
        self.udp_socket.close()
        self.udp_socket = None
