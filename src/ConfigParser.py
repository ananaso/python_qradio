#!/usr/bin/env python3

class ConfigParser:
    def handle_true_false_nil(tfnVal):
        lookupTable = {
            "NIL": None,
            "NULL": None,
            "NONE": None,
            "TRUE": True,
            "FALSE": False
        }
        # default to None if not found in table
        return lookupTable.get(tfnVal, None)
