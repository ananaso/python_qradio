#!/usr/bin/env python3
from .ConfigParser import ConfigParser

class Protocol:
    # Not sure what :STOP is or where it was defined in the ruby code, but
    # I'm gonna put it here so that it can be redefined quickly.
    STOP = "STOP"

    # @param allow_empty_data [true/false/nil] Whether or not this protocol will
    # allow an empty string to be passed down to later Protocols (instead of 
    # returning :STOP). Can be true, false, or nil, where nil is interpreted as
    # true unless the Protocol is the last Protocol of the chain.
    def __init__(self, allow_empty_data = None):
        self.interface = None
        self.allow_empty_data =
            ConfigParser.handle_true_false_nil(allow_empty_data)
        
    # why did the ruby have these reset functions?
    def reset():
        return
    
    def connect_reset():
        return reset()
        
    def disconnect_reset():
        return reset()
    
    def read_data(data):
        if (len(data) <= 0):
            if self.allow_empty_data == None:
                # not sure if this is correct, the ruby is confusing
                if self.interface and self.interface.read_protocols[-1] == self.interface:
                    # not sure if correct, what is :STOP in the ruby?
                    return self.STOP
            elif not allow_empty_data:
                return self.STOP
        return data
        
    # added these, but they seem to just be echo functions?
    def read_packet(packet):
        return packet
        
    def write_packet(packet):
        return packet
        
    def write_data(data):
        return data
        
    def post_write_interface(packet, data):
        return packet, data
