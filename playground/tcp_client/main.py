import socket
import struct


IP = "192.168.2.158"
# IP = "192.168.2.159"
# IP = "192.168.2.161"
# IP = "192.168.2.157"

PORT = 50001


def ip_address_bytes_to_str(ip_address_bytes):
    ip_address_str = ''.join('{:d}.'.format(x) for x in ip_address_bytes)
    ip_address_str = ip_address_str[0:len(ip_address_str) - 1]
    return ip_address_str


def get_network_seetings():
    print("client connects server and sends cmd to receive network settings...")

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((IP, PORT))
    message = bytearray()
    message.append(1)
    bytes_to_send = len(message)
    total_bytes_sent = 0
    connection_broken = False
    while total_bytes_sent < bytes_to_send:
        bytes_sent = tcp_socket.send(message)
        if bytes_sent == 0:
            print("  connection broken")
            connection_broken = True
            break
        total_bytes_sent += bytes_sent
    if not connection_broken:
        bytes_to_receive = tcp_socket.recv(1)
        if bytes_to_receive == b'':
            print("  connection broken")
        elif bytes_to_receive[0] == 23:

            bytes_read = 0
            received_data = bytearray()
            while bytes_read < bytes_to_receive[0]:
                data = tcp_socket.recv(min(bytes_to_receive[0] - bytes_read, bytes_to_receive[0]))
                if data == b'':
                    print("  connection broken")
                    connection_broken = True
                    break
                bytes_read += len(data)
                received_data += data
            if not connection_broken:
                print("  answer: {0}".format(''.join('0x{:02x} '.format(x) for x in received_data)))
                useDhcp = received_data[0]
                macAddress = ''.join('0x{:02x} '.format(x) for x in received_data[1:7])
                ipAddress = ip_address_bytes_to_str(received_data[7:11])
                subnetMask = ip_address_bytes_to_str(received_data[11:15])
                gateway = ip_address_bytes_to_str(received_data[15:19])
                dnsServer = ip_address_bytes_to_str(received_data[19:23])
                print("    useDhcp = {0}".format(useDhcp))
                print("    macAddress = {0}".format(macAddress))
                print("    ipAddress = {0}".format(ipAddress))
                print("    subnetMask = {0}".format(subnetMask))
                print("    gateway = {0}".format(gateway))
                print("    dnsServer = {0}".format(dnsServer))
        else:
            print("  answer has unexpected size ({0} bytes); expected size = {1} bytes".format(bytes_to_receive[0], 23))
    tcp_socket.close()

    print("done")


def set_network_seetings():
    print("client connects server and sends cmd to send network settings...")

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((IP, PORT))
    message = bytearray()
    message.append(2)

    message.append(17)

    message.append(1)

    message.append(192)
    message.append(168)
    message.append(1)
    message.append(101)

    message.append(255)
    message.append(255)
    message.append(255)
    message.append(0)

    message.append(192)
    message.append(168)
    message.append(1)
    message.append(1)

    message.append(192)
    message.append(168)
    message.append(1)
    message.append(1)

    bytes_to_send = len(message)
    total_bytes_sent = 0
    connection_broken = False
    while total_bytes_sent < bytes_to_send:
        bytes_sent = tcp_socket.send(message)
        if bytes_sent == 0:
            print("  connection broken while sending")
            connection_broken = True
            break
        total_bytes_sent += bytes_sent
    if not connection_broken:
        bytes_to_receive = tcp_socket.recv(1)
        if bytes_to_receive == b'':
            print("  connection broken")
        elif bytes_to_receive[0] == 1:
            print("  network settings have been successfully sent to the server")
        else:
            print("  received unexpected answer: {0}".format(bytes_to_receive[0]))
    tcp_socket.close()

    print("done")


def main():
    print("get network settings")
    get_network_seetings()

    # print("set network settings")
    # set_network_seetings()


if __name__ == '__main__':
    main()
