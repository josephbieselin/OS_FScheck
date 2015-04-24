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
INODE_MODE       = 33261
DIR_UID		 = 1000
DIR_GID		 = 1000
DIR_MODE         = 16877

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
    # freeblock_list will contain ints that are the free blocks in the filesystem
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
        for i in range(0, len(file_list)):
            freeblock_list.append(int(file_list[i].strip()))
        # close the file
        block.close()
    
    return freeblock_list

# return a list containing all possible free blocks that could exist, i.e. ROOT + 1 --> MAX_NUM_BLOCKS    
def get_possible_freeblocks():
    # listy will contain all integers that could be free blocks
    listy = []
    # loop through the possible range of ints
    for i in range(ROOT + 1, MAX_NUM_BLOCKS):
        listy.append(i)
    return listy

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

    superblock.seek(0)
    superblock.write(contents)
    # superblock.truncate(BLOCK_SIZE) # truncate the file, assuming data inside will not exceed 4096 bytes
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
        if (contents.count('{') != 1 and contents.count('}') != 1):
            print "Corrupt data in fusedata.%d: it does not contain inode data. check_entry_times cannot proceed.\n" % num
        file_list_atime_index = 5
        file_list_ctime_index = 6
        file_list_mtime_index = 7
    else:
        if (contents.count('{') != 2 and contents.count('}') != 2):
            print "Corrupt data in fusedata.%d: it does not contain directory data. check_entry_times cannot proceed.\n" % num
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


# update directory/inode uid, gid, and mode if the values are incorrect; file_list is the block data, entry_type is a char representing a directory 'd' or an inode 'f'
def check_permissions(file_list, entry_type):
    if (entry_type == 'd'):
        uid_val = DIR_UID
        gid_val = DIR_GID
        mode_val = DIR_MODE
    else: # entry_type == 'f'
        uid_val = UID
        gid_val = GID
        mode_val = INODE_MODE
        
    # permis_list index:entry_data --> 0:size, 1:uid, 2:gid, 3:mode, 4:atime, etc...
    permis_list = file_list[1].split(',')
    for i in range(1, 4): # check and update (if needed) the uid, gid, and mode
        data = permis_list[i].split(':') # get the number for the uid/gid/mode
        data_str = data[1].strip() # strip any whitespace
        data_num = int(data_str) # get the data as an int
        
        # update the uid, gid, mode values if necessary replacing the old value that used to be there
        if (i == 1): # uid
            if (data_num != uid_val):
                permis_list[i] = permis_list[i].replace(data_str, str(uid_val))
        elif (i == 2): # gid
            if (data_num != gid_val):
                permis_list[i] = permis_list[i].replace(data_str, str(gid_val))
        else: # mode
            if (data_num != mode_val):
                permis_list[i] = permis_list[i].replace(data_str, str(mode_val))
    
    # rejoin the possibly newly updated content back into the passed in file_list list
    file_list[1] = ','.join(permis_list)

# checks if the linkcount is correct, if indirect is set correctly, and if the size is a value that makes sense with respect to blocksize and indirect
def check_file_inode(my_num, blocks_in_use):
    # read the contents of the fusedata block into the variable: contents
    block_path = FILES_DIR + "/fusedata." + str(my_num)
    block = open(block_path, 'r+')
    contents = block.read()
    # print an error message and stop checking the inode if the data in the block does not match the format expected
    if (contents.count('{') != 1 and contents.count('}') != 1):
        print "Inode metadata in fusedata.%d has been corrupted and does match the expected format. Exitting check of this inode.\n"
        return -1
    contents = contents.strip() # strip any whitespace
    file_list = contents.strip(',')
    check_permissions(file_list, 'f')
    
    # get the size
    size_data = file_list[0]
    size_list = size_data.split(':')
    size_str = size_list[1].strip()
    size_num = int(size_str)    
    # get the linkcount
    linkcount_data = file_list[4]
    linkcount_list = linkcount_data.split(':')
    linkcount_str = linkcount_list[1].strip()
    linkcount_num = int(linkcount_str)
    # get the indirect value
    indirect_data = file_list[8]
    indirect_list = indirect_data.split(':')
    indirect_str = indirect_list[1].strip()
    indirect_num = int(indirect_str)    
    # get the location
    location_data = file_list[9]
    location_data = location_data.rstrip('}')
    location_list = location_data.split(':')
    location_str = location_list[1].strip()
    location_num = int(location_str)
    
    
    
        
# return the number of entries in the directory, resolve any issues with '.' and '..', and check all dir and inode entries in the directory
def check_inode_dict(file_list, my_num, parent_num, blocks_in_use):
    org_entry_list = file_list[2].split('}')
    # now the entry_list is actually a list with each directory entry
    entry_list = org_entry_list[0].split(',')
    temp_list = []
    for i in range(0, len(entry_list)):
        # listy contains a string of format: "type:name:block_number"
        listy = entry_list[i].strip()
        # listy is now a list with 3 strings in 3 indexes
        listy = listy.split(':')
        temp_list.append(listy)
    # temp_list's indexes each contain a list that has 3 index values: 0 --> type, 1 --> name, 2 --> block_number
    found_dot = False # boolean to indicate whether the inode_dict contains '.' or not
    found_dotdot = False # boolean to indicate whether the inode_dict contains '..' or not
    for entry in temp_list:
        if (entry[0] == 'd'):
            # if the '.' or '..' numbers don't match the passed in values, assume the passed in block numbers from the parent directory are the correct values
            if (entry[1] == '.'):
                found_dot = True
                if (int(entry[2]) != my_num):
                    entry[2] = my_num
            elif (entry[1] == '..'):
                found_dotdot = True
                if (int(entry[2]) != my_num):
                    entry[2] = my_num
            else:
                # the entry is a sub-directory, so we must check its inode_dict; its number is the entry's number, its parent number is the current directory's number
                check_dir(entry[2], my_num, blocks_in_use)
                # since this is a sub-directory, we must add its block number to the list of block numbers in use
                blocks_in_use.append(my_num)
        else: # entry[0] == 'f'
            # add the file inode to the list of used blocks
            blocks_in_use.append(entry[2])
            check_file_inode(entry[2], blocks_in_use)

    # if '.' or '..' weren't found in the inode_dict, add them to temp_list which will be converted back into the block's file
    if (not found_dot):
        temp_list.append(['d', '.', str(my_num)])
    if (not found_dotdot):
        temp_list.append(['d', '..', str(parent_num)])
    
    listy = []
    for entry in temp_list:
        # temp holds a string that is the format of an entry in a directory
        temp = ':'.join(entry)
        # listy will hold all the entries as indexes
        listy.append(temp)
    # rejoin all the entries separated by a comma and space
    org_entry_list[0] = ', '.join(listy)
    # rejoin the file's contents to include a curly brace
    file_list[2] = '}'.join(org_entry_list)
    
    # return the number of entries in the inode_dict for this directory
    return len(listy)


# checks the data inside the directory stored at fusedata block number referenced by my_num
def check_dir(my_num, parent_num, blocks_in_use):
    # read the contents of the fusedata block into the variable: contents
    block_path = FILES_DIR + "/fusedata." + str(my_num)
    block = open(block_path, 'r+')
    contents = block.read()
    # print an error message and stop checking the directory if the data in the block does not match the format expected
    if (contents.count('{') != 2 and contents.count('}') != 2):
        print "Directory metadata in fusedata.%d has been corrupted and does match the expected format. Exitting check of this directory.\n"
        return -1
    contents = contents.strip() # strip any whitespace
    # break contents into a list separated by curly braces '{' and '}'
    file_list = contents.split('{') # index zero will contain an empty string because directory data starts with a '{'
    check_permissions(file_list, 'd') # update directory id's and mode if necessary
    linkcount = check_inode_dict(file_list, my_num, parent_num, blocks_in_use)
    # file_meta_data holds size, uid, ..., linkcount, filename_to_inode_dict
    file_meta_data = file_list[1].split(',') # linkcount is index 7
    linkcount_data = file_meta_data[7]
    linkcount_list = linkcount_data.split(':')
    linkcount_str = linkcount_list[1].strip()
    # replace the old link count with a possibly updated new one
    file_meta_data[7] = file_meta_data[7].replace(linkcount_str, str(linkcount))
    file_list[1] = ','.join(file_meta_data)
    contents = '{'.join(file_list)
    
    
    


def main():
    check_devId()
    check_superblock(int(time()))
    blocks_in_use = []
    check_dir(ROOT, ROOT, blocks_in_use)
    check_times()

    
    
if __name__ == "__main__":
    main()