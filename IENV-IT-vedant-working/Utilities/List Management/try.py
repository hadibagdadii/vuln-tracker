### Works with Python 2.7 and above.


import sys, re, os
 
def Help():
    print("Usage: python try.py [Input CSV file] [Output location]")
    exit()
 
if len(sys.argv)-1 != 2:
    Help()
 
if not os.path.exists(sys.argv[1]):
    print("ERROR: Unable to find the file \""+sys.argv[1]+"\"")
    Help()
 
if os.path.exists(sys.argv[2]):
    print("ERROR: The file \""+sys.argv[2]+"\" already exists")
    Help()
 
 
inputCSV = open(sys.argv[1],"r")
outputCSV= open(sys.argv[2],"w+")
for line in inputCSV:
    for word in re.split('([^a-zA-Z0-9])', line):
        if word.isalnum():
            firstChar = re.search("[a-zA-Z]", word)
            word = word[0:firstChar.start()+1].upper() + word[firstChar.start()+1:].lower()
 
    outputCSV.write(word)
 
inputCSV.close()
outputCSV.close()
 
 

