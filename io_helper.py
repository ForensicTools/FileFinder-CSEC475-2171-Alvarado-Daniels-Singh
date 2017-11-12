
"""
File: io_helper.py
Purpose: Holds functions to take care of annoying lower level tasks
Author(s): Joncarlo Alvarado, Thomas Daniels 
"""

import os

def read_image(offset, size=512):
    """
    Purpose: Reads a given part of the disk
    @param   (int) offset - the place to start reading. offset%512 MUST = 0
    @param   (int) size - how much data to read. Defaults to 512 bytes.
              size%512 MUST = 0
    @return  (str) the data on that part of the disk
    """

    # Builds the string specifying the primary parition's file path.
    systemDrive = '\\\\.\\' + os.getenv('SystemDrive')

    # Opens the primary partition, seeks to a offset, and then
    # returns the amout of bytes specified by the size parameter.
    image = open(systemDrive, 'rb')
    image.seek(offset)

    return image.read(size)

	
def hexToInt(hexString):
    """
    Purpose:  Converts little endian bytes to an integer
    @param   (str) hexString - bytes presented by Python as '\x3f\x00' and
              so on in little endian
    @return  (int) a big endian version of hexString in hex characters
    """

    result = ''
    for byte in hexString:
        hexChar = "{0:x}".format(ord(byte))
        if(len(hexChar) == 1):
            hexChar = '0' + hexChar
        result = hexChar + result

    return int(result, 16)
