#--------------------------------------------------------------------------------
# receive_lunch_items.py
# Component of:
#     https://github.com/GhubGateway/Ghub_Pegasus_WMS_Tutorial_and_Templates and
#     https://theghub.org/tools/ghubex1
# Called from: Python_Launch.sh
# Also see Ghub, https://theghub.org/about
#--------------------------------------------------------------------------------

# In the Pegasus WMS YAML file,
# this job is specified to have the f.a input file and the f.b output file

import sys
 
def main(argv):
    
    username = argv[1]
    
    # f.a contains the received lunch items

    fp1 = open ('f.a', 'r')
    fp2 = open ('f.b', 'w')
    
    # Remove trailing "\n" added by fp1
    lunch_items = fp1.readline().rstrip()
    fp2.write ('Hello %s! Received lunch items: %s.' %(username, lunch_items))
    
    fp1.close()
    fp2.close()
    
    # f.b contains the served lunch items

if __name__ == "__main__":

    main(sys.argv)
