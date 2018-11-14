
import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP
sock.bind((UDP_IP, UDP_PORT))
print("Starting UDP listener at:", UDP_IP, ' port: ', UDP_PORT, sock)

while True:
    data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
    print('\n', data.decode())
