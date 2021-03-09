#!/usr/bin/env python3
# socket_echo_client.py

import socket
import sys

from qradio_protocol_cb import QradioProtocolCb

# Get IP/Port from cmd args if available
host = 'localhost'
port = 51104
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

# initialize the Qradio Protocol
qradio = QradioProtocolCb()

try:

    while True:
        # Send data
        #message = b'This is the message.  It will be repeated.'
        message = input("> ").encode('utf-8')
        packet = qradio.write_data(message)
        print('sending {!r}'.format(packet))
        sock.sendall(packet)

        # Look for the response
        amount_received = 0
        amount_expected = len(packet)

        while amount_received < amount_expected:
            data = sock.recv(16)
            amount_received += len(data)
            print('received {!r}'.format(data))

finally:
    print('closing socket')
    sock.close()
