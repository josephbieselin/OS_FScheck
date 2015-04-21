#!/usr/bin/env python


# CONSTANTS

MAX_NUM_BLOCKS	= 10000
MAX_FILE_SIZE	= 1638400
BLOCK_SIZE		= 4096
DEV_ID			= 20
FREE_START		= 1
FREE_END		= 25
ROOT			= FREE_END + 1
BLOCKS_IN_FREE	= 400
UID				= 1
GID				= 1
DIR_UID			= 1000
DIR_GID			= 1000

FILES_DIR		= "/fusedata"
LOG_FILE		= "~/Desktop/log.txt"


from time import time



def get_file_content(filepath):
    the_file = open(filepath, 'r+')
    content = the_file.read()
    the_file.close()
    return content

# Returns a boolean based on the check if the device ID that is stored in the superblock, aka fusedata.0, is the correct ID
def check_devId():
    # read the contents of the superblock file into the variable: contents
    superblock_path = FILES_DIR + "/fusedata.0"
    superblock = open(superblock_path, 'r+')
    contents = superblock.read()
    contents = contents.strip() # strip any whitespace
    # break contents into a list separated by commas
    file_list = contents.split(',')
    # break the devId part into a 2 component list with the string devId and devId number
    test_devId_list = file_list[2].split(':')
    # put the stringified devId number into test_devId
    test_devId = test_devId_list[1]
    test_devId_str = test_devId.strip() # strip any whitespace from the devId number
    test_devId_num = int(test_devId_str) # convert it to a variable of type int

    if (DEV_ID != test_devId_num):
        file_list[2] = file_list[2].replace(test_devId_str, str(DEV_ID))
        contents = ','.join(file_list)
        # assume for simplicity that file size of superblock does not pass BLOCK_SIZE
    
    # pad the file's contents with 0's
    contents = contents.ljust(BLOCK_SIZE, '0')
    # write the contents back to the file
    superblock.seek(0)
    superblock.write(contents)
    superblock.close()

# Returns a boolean based on the check if the passed in time 't' is greater than the time denoted in the superblock, aka fusedata.0,
def check_superblock_time(t):
    # read the contents of the superblock file into the variable: contents
    superblock_path = FILES_DIR + "/fusedata.0"
    superblock = open(superblock_path, 'r+')
    contents = superblock.read()
    contents = contents.strip() # strip any whitespace
    # break contents into a list separated by commas
    file_list = contents.split(',')
    # break the creationTime part into a 2 component list
    test_ctime_list = file_list[0].split(':')
    # put the stringified creationTime number into test_ctime
    test_ctime = test_ctime_list[1]
    test_ctime_str = test_ctime.strip() # strip any whitespace from ctime number
    test_ctime_num = int(test_ctime_str) # convert it to a variable of type int
    
    if (t < test_ctime_num):
        file_list[0] = file_list[0].replace(test_ctime_str, str(t))
        contents = ','.join(file_list)
        # assme for simplicity that file size of superblock does not pass BLOCK_SIZE
    
    # pad the file's contents with 0's
    contents = contents.ljust(BLOCK_SIZE, '0')
    superblock.seek(0)
    superblock.write(contents)
    superblock.close()
    
'''
Checks the atime, ctime, mtime for the current entry in the file system, and if any are greater than the passed in time 't', return False.
Recursively checks all entries in filename_to_inode_dict if this entry is a directory.
The recursive calls will return booleans based on each respective entry's atime, ctime, mtime comparison with time 't'.
entry_type will either be 'd' or 'f' corresponding to 'directory' and 'file inode', respectively.
'''
def check_entry_times(t, entry_type):
    
    return True

def check_times():
    time_since_epoch = int(time())
    
    return True
    
def main():
    check_superblock_time(int(time()))
    check_devId()
    
if __name__ == "__main__":
    main()    