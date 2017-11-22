"""
File: fileFinder.py
Author(s): Tom Daniels, Joncarlo Alvarado
Purpose: Finds and attempts to recover a deleted file in the NTFS file system
"""
################################################################################
#                                                                              #
#                            Imports and Definitions                           #
#                                                                              #
################################################################################
import ctypes, os, sys
from io_helper import *

# TODO: Remove this import. It's here for debugging
import binascii

SECTOR_SIZE=512      # Assume the size of a sector is 512 bytes
CLUSTER_SIZE=8       # Assume the size of a cluster is 8 sectors
SECTOR_OFFSET=11     # Offset that tells us # of bytes per sector. 2 bytes
CLUSTER_OFFSET=13    # Offset that tells us # of sectors per cluster. 1 byte
MFT_OFFSET=48        # Offset that tells us which cluster MFT starts at. 8 bytes
MFT_ENTRY_SIZE=1024  # The size, in bytes, of an MFT
MFT_MAGIC="FILE"     # The magic number for MFT entries
FILE_SECT=48         # The file name section has, among other things, the file name
ATTR_HEADER=24       # The size of the attribute headers
NAME_IN_UNI=66       # The offset into $FILE_NAME that the file's name is
NAME_LEN=64          # The offset into $FILE_NAME where the length of the file name is
FSIZE_OFFSET=40

################################################################################
#                                                                              #
#                                   Functions                                  #
#                                                                              #
################################################################################
def getMFTStartIndex():
    """
    Purpose: Gets the offset of the MFT in bytes
    @return  (int) Offset of the MFT in bytes
    """
    global SECTOR_SIZE, CLUSTER_SIZE, SECTOR_OFFSET, CLUSTER_OFFSET, MFT_OFFSET
    
    bootSector = read_image(0, SECTOR_SIZE) # Read 1st disk sector

    # Redefine SECTOR_SIZE or CLUSTER_SIZE if they're different than expected
    SECTOR_SIZE = hexToInt(bootSector[SECTOR_OFFSET:CLUSTER_OFFSET])
    CLUSTER_SIZE = hexToInt(bootSector[CLUSTER_OFFSET])

    # Return the offset of the MFT in bytes. The boot sector holds the MFT
    # offset in terms of clusters, so convert clusters to bytes
    return SECTOR_SIZE*CLUSTER_SIZE*hexToInt(bootSector[MFT_OFFSET:MFT_OFFSET+8])

## TODO: Add way to determine MFT Size

## TODO: Optimize Function
## TODO: Add way to determine MFT Size, Add threading

def findMFTRecord(MFTIndex, filename):
    """
    Purpose: Searches for an MFT record with the given file name
    @param   (long) MFTIndex - starting index for the MFT records
    @param   (str) filename - the name of the file to search for
    @return  (int or long) -1 if the entry was not found. Otherwise, return the
             offset from the beginning of the drive which points to the file
    """
    global MFT_ENTRY_SIZE, MFT_MAGIC, ATTR_HEADER

    # Get the first 1000 entries from the MFT
    # (improves speed over 1 read per entry)
    MFTEntry = read_image(MFTIndex, MFT_ENTRY_SIZE*1000)

    fileIndex = -1

    errorFlag = 0
    MFTCounter = 0
    
    # Loop through all the entries until we find the file or reach the end of
    # the MFT. An MFT entry is identified by the Magic Number "FILE".
    while(MFTEntry[:4] == MFT_MAGIC or MFTEntry[:4] == "\x00\x00\x00\x00"):
        # If this is not a proper MFT Entry, skip it
        if(MFTEntry[:4] != MFT_MAGIC):
            print("Entry with all zeros")
            MFTIndex += MFT_ENTRY_SIZE
            MFTEntry = MFTEntry[MFT_ENTRY_SIZE:]
            MFTCounter += 1
            if(MFTCounter >= 999):
                MFTEntry = read_image(MFTIndex, MFT_ENTRY_SIZE*1000)
                MFTCounter = 0
            continue
        
        # The offset of the first attribute section is 2 bytes long and located
        # at 0x14 from the beginning of the MFT entry
        attrSect = hexToInt(MFTEntry[20:22])

        # The first 4 bytes of an attribute section tell us what kind of
        # attribute section we're dealing with. If we're dealing with the
        # $FILE_NAME section, we want to extract the filename. Otherwise,
        # we want to find the next attribute section
        while(not hexToInt(MFTEntry[attrSect:attrSect+4]) == FILE_SECT):
            attrSize = hexToInt(MFTEntry[attrSect+4:attrSect+8])
            attrSect += attrSize

            # Avoids infinite loop and breaks out of this loop

            if(attrSect < 1):
                break


            # If attrSect > 1024 or if attrSize is zero,
            # there is no filename attribute
            if(attrSect > MFT_ENTRY_SIZE or attrSize == 0 or attrSect < 1):
                errorFlag = 1
                break

        # If there is no filename attribute, we move on to
        # the next MFT entry.
        if errorFlag == 1:
            MFTIndex += MFT_ENTRY_SIZE
            MFTEntry = MFTEntry[MFT_ENTRY_SIZE:]
            MFTCounter += 1
            errorFlag = 0
            if(MFTCounter >= 999):
                MFTEntry = read_image(MFTIndex, MFT_ENTRY_SIZE*1000)
                MFTCounter = 0
            continue

        # Sometimes there are two $FILE_NAME sections - one with a short name
        # such as "PLATFO~1" and another one with a longer name such as
        # "Platform Notifications". Check if there's a longer one
        fnSectionLen = hexToInt(MFTEntry[attrSect+4:attrSect+8])
        if(hexToInt(MFTEntry[attrSect+fnSectionLen+0:attrSect+fnSectionLen+4]) ==
            FILE_SECT):
            attrSize = hexToInt(MFTEntry[attrSect+4:attrSect+8])
            attrSect += attrSize
        
	# Get the length of the file name in unicode
        namelen = hexToInt(MFTEntry[attrSect+ATTR_HEADER+NAME_LEN])*2
	# Get the filename
        nameOffset = attrSect+ATTR_HEADER+NAME_IN_UNI
        MFTFileName = MFTEntry[nameOffset:nameOffset+namelen].replace("\x00", "")

	# TODO: Remove this print. It's here for debugging
        print(MFTFileName)
        if(MFTFileName == filename):
            fileIndex = MFTIndex
            break
        else:
            # Take a look at the next entry
            MFTIndex += MFT_ENTRY_SIZE
            MFTEntry = MFTEntry[MFT_ENTRY_SIZE:]
            MFTCounter += 1

        if(MFTCounter >= 999):
            MFTEntry = read_image(MFTIndex, MFT_ENTRY_SIZE*1000)
            MFTCounter = 0

    # TODO: Remove this print. It's here for debugging
    print(binascii.hexlify(MFTEntry))
    return fileIndex


def main():
    # Get offset of MFT in number of bytes
    MFTIndex = getMFTStartIndex()

    # Get the name of the file to restore from the user
    filename = raw_input("Please enter the name of a file to restore: ")

    # Get the file's MFT record
    fileIndex = findMFTRecord(MFTIndex, filename)

    # fileIndex = -1 means we didn't find any record matching that filename =(
    if(fileIndex == -1):
        print("No such file matching \"" + filename + "\". Exiting...")
        sys.exit()

    # Otherwise, restore the file
    # TODO: Restore the file
    print("Found file")
    return


if(__name__ == '__main__'):
    if(not ctypes.windll.shell32.IsUserAnAdmin()):
        print("Error, you must be an administrator to use this program")
        sys.exit()
    main()
