import socket


# IP = "127.0.0.1"
IP = "192.168.2.162"

PORT = 50001

def main():
    print("client connects server and sends data...")

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((IP, PORT))
    message = bytearray()
    message.append(1)
    data = "Hello".encode('utf-8')
    message.append(len(data))
    message += data
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
        answer = tcp_socket.recv(1)
        if answer == b'':
            print("  connection broken")
        elif answer[0] == 1:
            print("  server has accepted the command")
    tcp_socket.close()

    print("done")


if __name__ == '__main__':
    main()
