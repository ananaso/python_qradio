#!/usr/bin/env python3
import collections
import struct

from Protocol import Protocol

class QradioProtocolCb(Protocol):
    RADIOSYNC = '\x52\x54\x4C\x20'.encode('latin-1')
    CMDACK = '\x52\x54\x4C\x22'.encode('latin-1')
    FRAMESYNC = '\xDE\xAD\xBE\xEF'.encode('latin-1')
    
    def __init__(self, allow_empty_data = None):
        super().__init__(allow_empty_data)
        self.cmd_counter = 0
        #buffer that contains the makings of a telemetry packet
        self.tlm_buffer = []
        #circular buffer for telemetry data
        self.input_buffer = collections.deque([], maxlen=(1115*20))
        self.PktLen = 0
        self.TotalPktLen = 0
        
    def write_data(self, data):
        data = Protocol.write_data(data)
        
        # This is a header required by the radio command interface
        # Command length = the number of bytes of the entire command including
        #   the radio header
        cmd_length = len(data) + 16 + 4
        # Bit length = the number of bits in the data which also includes our
        #   our framesych pattern 0xDEADBEEF
        cmd_data_bit_length = (len(data) + 4) * 8
        
        data = QradioProtocolCb.RADIOSYNC + \
            struct.pack(">I", cmd_length) + \
            struct.pack(">I", self.cmd_counter) + \
            struct.pack(">I", cmd_data_bit_length) + \
            QradioProtocolCb.FRAMESYNC + \
            data
            
        self.cmd_counter += 1
        return data
        
    def find_packets(self):
        header_size = 8 + 4
        size = 1
        
        # Read off the receive queue until there's nothing left or we find part
        #   of a frame synch
        # This loop should continue reading until we can't read anymore or until
        #   we find 0xDE
        while (size != 0) and (self.PktLen == 0):
            self.tlm_buffer.append(self.input_buffer.pop())
            print(f"tlm_buffer: {self.tlm_buffer}")
            size = len(self.tlm_buffer)
            if size == 0: # nothing more to read
                return ""
            elif ord(self.tlm_buffer[0]) == 222: #0xDE
                # potentially found the start of the frame
                self.PktLen = 1
                break
            else:
                self.tlm_buffer.clear()
    
        # Get the rest of the frame synch if we don't have it yet
        if (self.PktLen >= 1) and (self.PktLen < 4):
            for i in range(self.PktLen, 4):
                self.tlm_buffer.append(self.input_buffer.pop())
            self.PktLen = len(self.tlm_buffer)
            # if we don't have the full synch pattern yet
            if self.PktLen < 4:
                return ""
        
        # We've found the frame synch but we don't have the entire header yet
        if (self.PktLen >= 4) and (self.PktLen < header_size):
            for i in range(self.PktLen, header_size):
                self.tlm_buffer.append(self.input_buffer.pop())
            self.PktLen = len(self.tlm_buffer)
            
            # Did we get enough to keep going?
            if self.PktLen < header_size:
                # Nothing left to read
                return ""
        
        # We have the header! Determine the packet length and attempt to read
        #   the rest of the command
        if self.PktLen == header_size:
            self.TotalPktLen = ord(self.tlm_buffer[8]) << 8 | ord(self.tlm_buffer[9])
            # CCSDS len = Data - 1 + 8 bytes header + 4 bytes sync
            self.TotalPktLen += 11
            
            # Trying to detect if we get a bit error in the command length
            #   field. I don't want us trying to read an erroneous command
            #   forever. Nothing in the implementation is limiting the command
            #   length to 1115, it's just a nice round number in the system
            #   based on RS codeblocks
            if self.TotalPktLen > 1115:
                # convert to strs without the preceding 0x for additional vals
                msg_id = hex(ord(self.tlm_buffer[4])) + \
                    hex(ord(self.tlm_buffer[5]))[2:]
                print(f"[ERROR]Received a telemetry packet length error: packet len {self.TotalPktLen} MsgId: {msg_id}")
                
                self.PktLen = 0
                self.TotalPktLen = 0
                self.tlm_buffer.clear()
                return ""
            
        # Try to get the rest of the message
        if self.PktLen < self.TotalPktLen:
            for i in range(self.PktLen, self.TotalPktLen):
                self.tlm_buffer.append(self.input_buffer.pop())
            self.PktLen = len(self.tlm_buffer)
            
            # if we didn't get the full message, return
            if self.PktLen < self.TotalPktLen:
                return ""
        
        # We've received the full packet
        if self.PktLen == self.TotalPktLen:
            # isolate the actual telemetry message
            tlm_packet = self.tlm_buffer[4:self.TotalPktLen]
            # Reset the telemetry parsing variables
            self.PktLen = 0
            self.TotalPktLen = 0
            self.tlm_buffer.clear()
            return ''.join(str(x) for x in tlm_packet)
            
    def read_data(self, data):
        tlm_pkt = '\xAA'.encode('latin-1')
        output_buffer = ''.encode('latin-1')
        
        # push data onto the circular buffer
        if len(data) != 0:
            data = data.decode('latin-1')
            for i in range(0, len(data)):
                data_chunk = data[i]
                self.input_buffer.append(data_chunk)
        else:
            return self.STOP
        
        # find telemetry packets
        pkt_cnt = 0
        while tlm_pkt != '':
            tlm_pkt = self.find_packets()
            if tlm_pkt != '':
                output_buffer = '{}{}'.format(output_buffer, tlm_pkt)
                pkt_cnt += 1
        #print(f"{pkt_cnt} packets in frame")
        #print(f"{output_buffer}")
        # if buffer is full
        if len(self.input_buffer) == self.input_buffer.maxlen:
            print(self.input_buffer)
        # return telemetry packets
        if (output_buffer == None) or len(output_buffer) == 0:
            return self.STOP
        else:
            return super().read_data(output_buffer)
