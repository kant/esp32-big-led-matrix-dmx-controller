import socket


class TcpConnection(object):

    TCP_PORT: int = 50001

    tcp_socket: socket.socket = None

    def send_cmd_get_network_settings(self, ip_address: str, received_network_settings: dict) -> bool:
        success: bool = False
        self._open(ip_address)
        message: bytearray = bytearray()
        message.append(1) # first byte is the command identifier (1 = TCP_CMD_GET_NETWORK_SETTINGS)
        # command has no parameter, so send it to the TCP server
        bytes_to_send: int = len(message)
        total_bytes_sent: int = 0
        connection_broken: bool = False
        # send the command
        while total_bytes_sent < bytes_to_send:
            bytes_sent: int = self.tcp_socket.send(message)
            if bytes_sent == 0:
                connection_broken = True
                break
            total_bytes_sent += bytes_sent
        if not connection_broken:
            # receive the answer from the TCP server
            bytes_to_receive: bytes = self.tcp_socket.recv(1) # first byte of the answer is the number of following bytes
            if bytes_to_receive[0] == 23: # only if the number of the following bytes is correct, receive the answer
                bytes_read: int = 0
                received_data: bytearray = bytearray()
                # receive the answer
                while bytes_read < bytes_to_receive[0]:
                    data: bytes = self.tcp_socket.recv(min(bytes_to_receive[0] - bytes_read, bytes_to_receive[0]))
                    if data == b'':
                        connection_broken = True
                        break
                    bytes_read += len(data)
                    received_data += data
                if not connection_broken:
                    # received complete answer from TCP server
                    received_network_settings['use_dhcp'] = bool(received_data[0])
                    received_network_settings['mac_address'] = self._mac_address_bytes_to_str(received_data[1:7])
                    received_network_settings['ip_address'] = self._ip_address_bytes_to_str(received_data[7:11])
                    received_network_settings['subnet_mask'] = self._ip_address_bytes_to_str(received_data[11:15])
                    received_network_settings['gateway'] = self._ip_address_bytes_to_str(received_data[15:19])
                    received_network_settings['dns_server'] = self._ip_address_bytes_to_str(received_data[19:23])
                    success = True
        self._close()
        return success

    def send_cmd_set_network_settings(self, ip_address: str, new_network_settings: dict) -> bool:
        success: bool = False
        self._open(ip_address)
        message: bytearray = bytearray()
        message.append(2) # first byte is the command identifier (2 = TCP_CMD_SET_NETWORK_SETTINGS)
        message.append(17) # second byte is length of parameter data
        if new_network_settings['use_dhcp']:
            message.append(1)
        else:
            message.append(0)
        message.extend(self._ip_address_str_to_bytes(new_network_settings['ip_address']))
        message.extend(self._ip_address_str_to_bytes(new_network_settings['subnet_mask']))
        message.extend(self._ip_address_str_to_bytes(new_network_settings['gateway']))
        message.extend(self._ip_address_str_to_bytes(new_network_settings['dns_server']))
        bytes_to_send: int = len(message)
        total_bytes_sent: int = 0
        connection_broken: bool = False
        # send the command and parameter to the TCP server
        while total_bytes_sent < bytes_to_send:
            bytes_sent:int  = self.tcp_socket.send(message)
            if bytes_sent == 0:
                connection_broken = True
                break
            total_bytes_sent += bytes_sent
        if not connection_broken:
            # receive the acknowledgement from the TCP server
            bytes_to_receive: bytes = self.tcp_socket.recv(1)
            if bytes_to_receive[0] == 1: # 1 = positive acknowledgement
                success = True
        self._close()
        return success

    def _open(self, ip_address: str) -> None:
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.connect((ip_address, self.TCP_PORT))

    def _mac_address_bytes_to_str(self, mac_address_bytes: bytearray) -> str:
        mac_address_str: str = ''.join('{:02x}:'.format(x) for x in mac_address_bytes)
        mac_address_str = mac_address_str[0:len(mac_address_str) - 1]
        return mac_address_str

    def _ip_address_bytes_to_str(self, ip_address_bytes: bytearray) -> str:
        ip_address_str: str = ''.join('{:d}.'.format(x) for x in ip_address_bytes)
        ip_address_str = ip_address_str[0:len(ip_address_str) - 1]
        return ip_address_str

    def _ip_address_str_to_bytes(self, ip_address_str: str) -> bytearray:
        ip_address_bytes: bytearray = bytearray()
        ip_address_part_strs: list = ip_address_str.split('.')
        if len(ip_address_part_strs) == 4:
            for part_str in ip_address_part_strs:
                part_int: int = int(part_str)
                ip_address_bytes.append(part_int)
        return ip_address_bytes

    def _close(self) -> None:
        self.tcp_socket.close()
        self.tcp_socket = None
