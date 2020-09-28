import socket


class UdpConnection(object):

    udp_socket: socket.socket = None

    def open(self) -> None:
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
        self.udp_socket.settimeout(5)

<<<<<<< HEAD
    def broadcast(self, packet: bytearray) -> None:
        self.udp_socket.sendto(packet, ("192.168.2.158", self.UDP_PORT))
        self.udp_socket.sendto(packet, ("192.168.2.159", self.UDP_PORT))
        self.udp_socket.sendto(packet, ("192.168.2.161", self.UDP_PORT))
        self.udp_socket.sendto(packet, ("192.168.2.157", self.UDP_PORT))

        # self.udp_socket.sendto(packet, ("<broadcast>", self.UDP_PORT))
=======
    def send_packet(self, endpoint: dict, packet: bytearray) -> None:
        self.udp_socket.sendto(packet, (endpoint['ip_address'], endpoint['port']))
>>>>>>> 12774f778f3af5d9e7665028555e0d331076a9ee

    def send_packets(self, packets: list) -> None:
        for packet in packets:
            self.send_packet(packet['endpoint'], packet['packet_data'])

    def close(self) -> None:
        self.udp_socket.close()
        self.udp_socket = None
