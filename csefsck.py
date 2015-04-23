#!/usr/bin/env python


# CONSTANTS

MAX_NUM_BLOCKS   = 10000
MAX_FILE_SIZE    = 1638400
BLOCK_SIZE       = 4096
DEV_ID		 = 20
FREE_START	 = 1
FREE_END	 = 25
ROOT	         = FREE_END + 1
BLOCKS_IN_FREE	 = 400
UID		 = 1
GID		 = 1
DIR_UID		 = 1000
DIR_GID		 = 1000

FILES_DIR	 = "/fusedata"
LOG_FILE	 = "~/Desktop/log.txt"


from time import time
from sys import exit



def get_file_content(filepath):
    the_file = open(filepath, 'r+')
    content = the_file.read()
    the_file.close()
    return content

# return a list containing all free block numbers in the free block files
def get_freeblock_list():
    freeblock_list = []
    # loop through each file appending to the free block list
    for i in range(FREE_START, FREE_END + 1):
        # open the free block file and store its contents
        block_path = "%s/fusedata.%d" % (FILES_DIR, i)
        block = open(block_path, 'r+')
        contents = block.read()
        contents = contents.strip() # strip any whitespace
        # break contents into a list separted by commas
        file_list = contents.split(',')
        # add each noted free block in the file to freeblock_list
        for num in file_list:
            num = num.strip() # strip any whitespace
            num = int(num) # un-stringify
            freeblock_list.append(num) # append this number to the list
        # close the file
        block.close()
    
    return freeblock_list

# ---------------------------------- 1 ----------------------------------------#
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
        print "Device ID did not match the expected value... awkward\n"
        exit(1)
    
    # pad the file's contents with 0's
    contents = contents.ljust(BLOCK_SIZE, '0')
    # write the contents back to the file
    superblock.seek(0)
    superblock.write(contents)
    superblock.close()
# ---------------------------------- 1 ----------------------------------------#

# ---------------------------------- 2 ----------------------------------------#
# check and possibly update the superblock's creationTime
def check_superblock_time(t, file_list):
    # break the creationTime part into a 2 component list
    test_ctime_list = file_list[0].split(':')
    # put the stringified creationTime number into test_ctime
    test_ctime = test_ctime_list[1]
    test_ctime_str = test_ctime.strip() # strip any whitespace from ctime number
    test_ctime_num = int(test_ctime_str) # convert it to a variable of type int
    
    if (t < test_ctime_num):
        print "Time in the superblock was a future value and is now the current time\n"
        file_list[0] = file_list[0].replace(test_ctime_str, str(t))
        # assme for simplicity that file size of superblock does not pass BLOCK_SIZE

# check and possibly update the superblock's fusedata block info
def check_superblock_block_data(t, file_list):
    # break the block data info part into 4 2 component lists
    test_data_list = []
    # append freeStart, freeEnd, root, and maxBlocks data to the list, in that indexed order
    for i in range(3, 7):
        test_data_list.append(file_list[i].split(':'))
    # for each data value, test for its correctness in reference to global consts
    for j in range(0, 4):
        # put the stringified int value to test into test_data
        test_data = test_data_list[j][1]
        # strip any whitespace, and if it is index 4 (maxBlocks), strip the ending '}' char
        test_data_str = test_data.strip()
        if (j == 3):
            test_data_str = test_data_str.rstrip('0')
            test_data_str = test_data_str.rstrip('}')
        test_data_num = int(test_data_str) # convert it to a variable of type int
        
        # determine which case is being tested and update the appropriate value if needed
        if (j == 0): # freeStart
            if (test_data_num != FREE_START):
                print "freeStart in the superblock was incorrect and has been corrected\n"
                file_list[3] = file_list[3].replace(test_data_str, str(FREE_START))
        elif (j == 1): # freeEnd
            if (test_data_num != FREE_END):
                print "freeEnd in the superblock was incorrect and has been corrected\n"                
                file_list[4] = file_list[4].replace(test_data_str, str(FREE_END))
        elif (j == 2): # root
            if (test_data_num != ROOT):
                print "root in the superblock was incorrect and has been corrected\n"
                file_list[5] = file_list[5].replace(test_data_str, str(ROOT))
        else: # maxBlocks
            if (test_data_num != MAX_NUM_BLOCKS):
                print "maxBlocks in the superblock was incorrect and has been corrected\n"
                file_list[6] = file_list[6].replace(test_data_str, str(MAX_NUM_BLOCKS))
    
# checks and updates (if needed) the superblock's creationTime, freeStart, freeEnd, root, and maxBlocks entries
def check_superblock(t):
    # read the contents of the superblock file into the variable: contents
    superblock_path = FILES_DIR + "/fusedata.0"
    superblock = open(superblock_path, 'r+')
    contents = superblock.read()
    contents = contents.strip() # strip any whitespace
    # break contents into a list separated by commas
    file_list = contents.split(',')
    
    # check the superblock's data (file_list is a container and can be used by reference in functions)
    check_superblock_time(t, file_list)
    check_superblock_block_data(t, file_list)
    # get the superblock content back into string format
    contents = ','.join(file_list)
    
    # pad the file's contents with 0's
    contents = contents.ljust(BLOCK_SIZE, '0')
    superblock.seek(0)
    superblock.write(contents)
    superblock.truncate(BLOCK_SIZE) # truncate the file, assuming data inside will not exceed 4096 bytes
    superblock.close()

'''
Checks the atime, ctime, mtime for the current entry in the file system, and if any are greater than the passed in time 't', return False.
Recursively checks all entries in filename_to_inode_dict if this entry is a directory.
The recursive calls will return booleans based on each respective entry's atime, ctime, mtime comparison with time 't'.
entry_type will either be 'd' or 'f' corresponding to 'directory' and 'file inode', respectively.
'''
def check_entry_times(t, entry_type, num):
    # read the contents of the fusedata block into the variable: contents
    block_path = FILES_DIR + "/fusedata." + str(num)
    block = open(block_path, 'r+')
    contents = block.read()
    contents = contents.strip() # strip any whitespace
    # break contents into a list separated by commas
    file_list = contents.split(',')
    
    if (entry_type == 'f'):
        file_list_atime_index = 5
        file_list_ctime_index = 6
        file_list_mtime_index = 7
    else:
        file_list_atime_index = 4
        file_list_ctime_index = 5
        file_list_mtime_index = 6

    # break the times into 2 component lists
    test_atime_list = file_list[file_list_atime_index].split(':')
    test_ctime_list = file_list[file_list_ctime_index].split(':')
    test_mtime_list = file_list[file_list_mtime_index].split(':')
    
    # atime
    test_atime = test_atime_list[1]
    test_atime_str = test_atime.strip() # strip any whitespace from atime number
    test_atime_num = int(test_atime_str) # convert it to a variable of type int
    # ctime
    test_ctime = test_ctime_list[1]
    test_ctime_str = test_ctime.strip() # strip any whitespace from ctime number
    test_ctime_num = int(test_ctime_str) # convert it to a variable of type int
    # mtime
    test_mtime = test_mtime_list[1]
    test_mtime_str = test_mtime.strip() # strip any whitespace from mtime number
    test_mtime_num = int(test_mtime_str) # convert it to a variable of type int
    
    changed = False
    # update atime if it is a value in the future
    if (t < test_atime_num):
        changed = True
        print "atime in fusedata.%d was a future value and is now the current time\n" % num
        file_list[file_list_atime_index] = file_list[file_list_atime_index].replace(test_atime_str, str(t))
        # contents = ','.join(file_list)
        # assme for simplicity that file size of superblock does not pass BLOCK_SIZE

    # update ctime if it is a value in the future                
    if (t < test_ctime_num):
        changed = True
        print "ctime in fusedata.%d was a future value and is now the current time\n" % num
        file_list[file_list_ctime_index] = file_list[file_list_atime_index].replace(test_ctime_str, str(t))
        # contents = ','.join(file_list)
        # assme for simplicity that file size of superblock does not pass BLOCK_SIZE

    # update mtime if it is a value in the future
    if (t < test_mtime_num):
        changed = True
        print "mtime in fusedata.%d was a future value and is now the current time\n" % num
        file_list[file_list_mtime_index] = file_list[file_list_mtime_index].replace(test_mtime_str, str(t))
        # contents = ','.join(file_list)
        # assme for simplicity that file size of superblock does not pass BLOCK_SIZE
    
    # if we changed any of the time values, update the contents variable
    if (changed):
        contents = ','.join(file_list)
    
    # pad the file's contents with 0's
    contents = contents.ljust(BLOCK_SIZE, '0')
    block.seek(0)
    block.write(contents)
    block.close()
    
    # if this fusedata block is a directory, recursively call this function on all directory entries (except '.' and '..')   
    if (entry_type == 'd'):
        # split the file contents by '{' to separate some of the filename to inode dict
        file_list = contents.split('{')
        # split again by '}' to get the inode_list as the first index of the created list
        inode_list = file_list[2].split('}')
        # now the inode_list is actually a list with each directory entry
        inode_list = inode_list[0].split(',')
        for entry in inode_list:
            entry = entry.strip()
            # inode_content is a list: 0 --> type; 1 --> name; 2 --> block number
            inode_content = entry.split(':')
            if (inode_content[1] != '.' and inode_content[1] != '..'):
                # recursive call to check the directory's next entry's time data
                check_entry_times(t, inode_content[0], inode_content[2])
        

def check_times():
    time_since_epoch = int(time())
    check_entry_times(time_since_epoch, 'd', ROOT)
# ---------------------------------- 2 ----------------------------------------#

# ---------------------------------- 3 ----------------------------------------#




def main():
    check_devId()
    check_superblock(int(time()))
    check_times()
    
if __name__ == "__main__":
    main()