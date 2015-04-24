def change_list(listy):
    listy.append('bieselin')
    
    #j = 0
    #for j in range(len(listy)):
    #    listy[j] += "%d" % j
    '''    
    for i in listy:
        print i + '\n'
        i = '0'
        j += 1
    '''
    
def main():
    listy = ['I', 'am', 'joe']
    change_list(listy)
    for i in listy:
        print i + '\n'
        
if __name__ == "__main__":
    main()