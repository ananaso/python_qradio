#!/usr/bin/env python3
# socket_echo_client.py

import socket
import sys

# Get IP/Port from cmd args if available
host = 'localhost'
port = 51103
try:
    host = sys.argv[1]
    port = int(sys.argv[2])
except IndexError:
    print("Using default host/port")
except ValueError:
    print("Port must be an integer, using default port")

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = (host, port)
print('connecting to {} port {}'.format(*server_address))
sock.connect(server_address)

try:

    while True:
        # Send data
        message = input("> ").encode('utf-8')
        #message = b'This is the message.  It will be repeated.'
        print('sending {!r}'.format(message))
        sock.sendall(message)

        # Look for the response
        amount_received = 0
        amount_expected = len(message)

        while amount_received < amount_expected:
            data = sock.recv(16)
            amount_received += len(data)
            print('received {!r}'.format(data))

finally:
    print('closing socket')
    sock.close()
