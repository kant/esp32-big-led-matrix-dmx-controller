import socket


def main():
    print("server is running and waiting for clients to connect...")

    tcp_client_socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_client_socket_server.bind(("127.0.0.1", 50001))
    tcp_client_socket_server.listen(1)

    while True:
        client_socket, client_addr = tcp_client_socket_server.accept()
        print("  client {0} connected and send the following:".format(client_addr))
        connection_broken = False
        while True:
            data = client_socket.recv(1)
            if data == b'':
                print("  connection broken")
                connection_broken = True
                break
            command_id = data[0]
            print("  command id = {0}".format(command_id))
            if command_id == 1:
                data = client_socket.recv(1)
                if data == b'':
                    print("  connection broken")
                    connection_broken = True
                    break
                data_length = data[0]
                print("  data length = {0}".format(data_length))
                bytes_read = 0
                received_data = bytearray()
                while bytes_read < data_length:
                    data = client_socket.recv(min(data_length - bytes_read, data_length))
                    if data == b'':
                        print("  connection broken")
                        connection_broken = True
                        break
                    bytes_read += len(data)
                    received_data += data
                if not connection_broken:
                    print("  data:")
                    print("    {0}".format(received_data.decode('utf-8')))
                    break
            if connection_broken:
                break
        print("  closed connection to client")
        client_socket.close()
        print("waiting for more clients to connect...")


if __name__ == '__main__':
    main()
