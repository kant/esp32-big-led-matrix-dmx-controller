import socket


def main():
    print("client connects server and sends data...")

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect(("127.0.0.1", 50001))
    message = bytearray()
    message.append(1)
    data = "Hello".encode('utf-8')
    message.append(len(data))
    message += data
    tcp_socket.send(message)
    tcp_socket.close()

    print("done")


if __name__ == '__main__':
    main()
