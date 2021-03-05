#!/usr/bin/env python3
import collections
import struct

class QradioProtocolCb(Protocol):
    RADIOSYNC = "\x52\x54\x4C\x20"
    CMDACK = "\x52\x54\x4C\x22"
    FRAMESYNC = "\xDE\xAD\xBE\xEF"
    
    def __init__(self, allow_empty_data = None):
        self.cmd_counter = [0]
        #buffer that contains the makings of a telemetry packet
        self.tlm_buffer = []
        #circular buffer for telemetry data
        self.input_buffer = collections.deque(maxlen=(1115*20))
        self.PktLen = 0
        self.TotalPktLen = 0
        super(allow_empty_data)
        
    def write_data(data)
        cmd_length = [0]
        cmd_data_bit_length = [0]
        
        data = super.write_data(data)
        
        # This is a header required by the radio command interface
        # Command length = the number of bytes of the entire command including
        #   the radio header
        cmd_length[0] = len(data) + 16 + 4
        # Bit length = the number of bits in the data which also includes our
        #   our framesych pattern 0xDEADBEEF
        cmd_data_bit_length[0] = (len(data) + 4) * 8
        
        data = QradioProtocolCb.RADIOSYNC + 
            struct.pack(">I", cmd_length) + 
            struct.pack(">I", self.cmd_counter) +
            struct.pack(">I", cmd_data_bit_length) +
            QradioProtocolCb.FRAMESYNC +
            data
            
        self.cmd_counter[0] += 1
        return data
        
    def find_packets():
        header_size = 8 + 4
        size = 1
        
        # Read off the receive queue until there's nothing left or we find part
        #   of a frame synch
        # This loop should continue reading until we can't read anymore or until
        #   we find 0xDE
        while ((size != 0) && (self.PktLen == 0)):
            self.tlm_buffer[0] = self.input_buffer.pop()
            size = len(self.tlm_buffer)
            if size == 0: # nothing more to read
                return ""
            elif self.tlm_buffer[0].
