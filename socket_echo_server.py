#!/usr/bin/env python3
# socket_echo_server.py

import socket
import sys
import struct

from qradio_protocol_cb import QradioProtocolCb

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
    
    try:
        connection, client_address = sock.accept()
    except KeyboardInterrupt:
        # close a bit more gracefully
        print('shutting down')
        sys.exit()
        
    try:
        print('connection from', client_address)
        
        stillConnected = True
        while stillConnected:
            whole_data = b''
            cmd_length = -1
            radiosync = b''
            
            # Receive the data in small chunks
            while len(whole_data) != cmd_length:
                data = connection.recv(16)
                # if the connection to cosmos is closed we get empty data
                if data == b'':
                    # make sure to close the connection on our side too
                    stillConnected = False
                    break
                print(f"received {data!r}")
                whole_data += data
                # determine command length if that part of header is received
                if cmd_length == -1 and len(whole_data) >= 8:
                    radiosync = whole_data[:4]
                    if radiosync == qradio.RADIOSYNC:
                        cmd_length = struct.unpack(">I", whole_data[4:8])[0]
            
            framesync = whole_data[16:20]
            if framesync == qradio.FRAMESYNC:
                cmd_counter = struct.unpack(">I", whole_data[8:12])[0]
                cmd_data_bit_length = struct.unpack(">I", whole_data[12:16])[0]
                data = whole_data[20:]
                # pretty-print data
                data_str = f"data:\t"
                data_chunk = ''
                for i in range(0, len(data)):
                    data_chunk += format(data[i], '02X') + ' '
                    if (i+1) % 8 == 0:
                        data_chunk += '\n\t\t'
                        data_str += data_chunk
                        data_chunk = ''
                print("Unfurled received packet:")
                print(f"\tRADIOSYNC: 0x{radiosync.hex()}")
                print(f"\tcmd_length: {cmd_length}")
                print(f"\tcmd_counter: {cmd_counter}")
                print(f"\tcmd_data_bit_length: {cmd_data_bit_length}")
                print(f"\tFRAMESYNC: 0x{framesync.hex()}")
                print(f"\t{data_str}")
        
        """
        REMOVED SENDBACK SINCE IT ISN'T WHAT COSMOS EXPECTS/WANTS
        # read data through qradio protocol
        packet = qradio.read_data(whole_data)
        print(packet)
            
        # echo command
        print('sending data back to the client')
        connection.sendall('\xaa'.encode('latin-1'))
        """
    finally:
        # Clean up the connection
        connection.close()
