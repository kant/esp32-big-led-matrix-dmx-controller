import socket
s = socket.socket()
s.connect(('192.168.2.157', 80))

message = "Hello World"
s.send(message)

data = ""
while len(data) < len(message):
    data += s.recv(1)

print(data)
