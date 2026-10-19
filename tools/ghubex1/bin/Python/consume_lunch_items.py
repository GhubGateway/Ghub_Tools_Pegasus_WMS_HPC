#--------------------------------------------------------------------------------
# consume_lunch_items.py
# Component of:
#     https://github.com/GhubGateway/Ghub_Pegasus_WMS_Tutorial_and_Templates and
#     https://theghub.org/tools/ghubex1
# Called from: Python_Launch.sh
# Also see Ghub, https://theghub.org/about
#--------------------------------------------------------------------------------

# In the Pegasus WMS YAML file,
# this job is specified to have the f.b input file and the f.c output file

import sys

def main(argv):
    
    # f.b contains the served lunch items

    fp1 = open ('f.b', 'r')
    fp2 = open ('f.c', 'w')

    # Remove trailing "\n" added by fp1
    served_lunch_items = fp1.readline().rstrip()
    fp2.write('%s Thank you for lunch. Yum Yum!!' %served_lunch_items)
    
    fp1.close()
    fp2.close()

    # f.c contains the thank you note

if __name__ == "__main__":

    main(sys.argv)
