#!/usr/bin/env python3
# socket_echo_server.py

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

# Bind the socket to the port
server_address = (host, port)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

# initialize the Qradio Protocol
qradio = QradioProtocolCb()

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address)

        # Receive the data in small chunks
        whole_data = ''.encode('latin-1')
        while True:
            data = connection.recv(16)
            print('received {!r}'.format(data))
            if not data:
                break
            whole_data += data
        
        # read data through qradio protocol
        packet = qradio.read_data(whole_data)
        print(packet)
        
        # echo command
        if packet:
            print('sending data back to the client')
            connection.sendall(packet)
    finally:
        # Clean up the connection
        connection.close()
