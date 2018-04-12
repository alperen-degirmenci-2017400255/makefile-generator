import os
import sys
import re
import os.path
from collections import deque

#Class which holds the files with .h extension as 
#hClass objects. Class has some fields in it.
class hClass:
    filepath = ""	#File's full path as string.
    filename = ""	#File's full name in the form "addTwoInts.h"
    onlyName = ""	#File's name with ".o" extension, used in generating make file.
    pathWithoutName = "" 	#File's full directory without file's name.
    incInMain = False		#Boolean variable which indicates .h file is included in main file or not.
    usedInMain = False		#Boolean variable which indicates .h file's function is used in main or not.
    							#Actually helps the program to find unused functions.
    
    def __init__(self, name):	#Constructor for the hClass.
        self.filename = name
        self.filepath = ""
        self.onlyName = ""
        self.pathWithoutName = ""
        self.incInMain = False
        self.usedInMain = False
           
#Class which holds the files with .c extension
#cCLass objects. Class has some fields in it.
class cClass:
    filepath = ""	#File's full path as string.
    filename = ""	#File's full name in the form "addTwoInts.c"
    onlyName = ""	#File's name with ".o" extension, used in generating make file.
    pathWithoutName = ""	#File's full directory without file's name.

    def __init__(self,name):	#Constructor for the cClass.
        self.filename = name
        self.filepath = ""
        self.onlyName = ""
        self.pathWithoutName = ""
    

qlist = deque([sys.argv[1]]) #appending the argument given to the program to the list
							 #named qlist. Will be used to store traversing directories.

lH=[]		#List that stores hClass objects which store ".h" extension files' infos.
hCounter = 0	#counter for lH list.
lC=[]		#List that stores cClass objects which store ".c" extension files' infos.
cCounter = 0	#counter for lC list.

incList = []	#String list which stores header files' names included in the main as #include ".h".
#funcList = []	#String list which stores function strings as they used in main.

# This is for holding the main directory's string
# we take as argument to the program.
maindir = qlist[0]

while qlist:	# While part which traverses directories.

    currentdir = qlist.popleft() #As some parts are given by Can Ozturan, I'm not commenting those parts.
    dircontents = os.listdir(currentdir)
    for name in dircontents:
        currentitem = currentdir + "/" + name 	#Creating currentitem string which holds full path to a file.
        
        if os.path.isdir(currentitem): 	#If "currentitem" is a folder, append it to the qlist.
            qlist.append(currentitem)	

        else:			#If the "currentitem" is a file, process it.

            if name.endswith('.c'):		#If file's extension is ".c" go for this if part.

                searchfile = open(currentitem,"r")
                for line in searchfile:
                    if "stdio.h" in line:	#If statement to find out if the file is main.c or not.

                        mainC = cClass(name)  #If main.c file is found create an object named mainC of cClass instance for it.
                        mainC.filepath = currentitem
                        mainC.onlyName = name.replace('.c','.o')
                        mainC.pathWithoutName = currentdir

                        for line in searchfile:		#Iterate through lines in the main.c file.
                        							#to match lines with #include "blabla.h" header files.                           
                            m = re.search(r'"([A-Za-z0-9_\./\\-]*)"', line)
                            	#Regular expression to match with ".h" strings.
                            if m:
                                bb = m.group(0)
                                bb = bb.replace('"', '')
                                #ff = bb.replace('.h', '(')
                                incList.append(bb)	 #Append the "blabla.h" to incList without quotes. 
                                #funcList.append(ff)	 #Appent the "blabla(" to funcList for later use.
                                
                #Part of the program which finds other ".c" extensioned files.
                #Rest of the ".c" files which are not "main.c" file.
                #Create cClass objects with filenames of them as arguments.
                #Add them to the lC list.

                lC.append(cClass(name))
                lC[cCounter].filepath = currentitem
                lC[cCounter].onlyName = name.replace('.c', '.o')
                lC[cCounter].pathWithoutName = currentdir
                cCounter +=1


                #Part of the program which finds ".h" extensioned files.
                #Create hClass objects with filenames of them as arguments.
                #Add them to the lH list.

            elif name.endswith('.h'):
                lH.append(hClass(name))
                lH[hCounter].filepath = currentitem
                lH[hCounter].pathWithoutName = currentdir
                lH[hCounter].onlyName = name.replace('.h', '.o')
                hCounter +=1

i = 0
j = 0
for i in range(len(lH)):	#This part compares the filenames of the ".h" objects in lH list
							#with the incList's strings to find out if the ".h" object is
							#included in main or not.
							#Then changes to boolean to true if the header file is included in "main.c".
    for j in range(len(incList)):
        if lH[i].filename == incList[j]:
            lH[i].incInMain = True


i = 0                   	
for i in range(len(lH)):	#This part changes the filenames of the ".h" objects in lH list
							#and searches for the "main.c" file's lines to find out
							#if the function is used in "main.c" or not.
							#Then changes to boolean to true if header file's function is used in "main.c"
    tmpFunc = lH[i].filename.replace('.h', '(')
    searchfile = open(mainC.filepath,"r")
    for line in searchfile:
        m = re.search (re.escape(tmpFunc),line)
        if m:
            lH[i].usedInMain = True

i = 0
j = 0
counter3 = 0
#This part gives the error message and terminates the program if
#an include file is present in main.c but doesn't exist in directories.
for i in range(len(incList)):
	for j in range(len(lH)):
		if incList[i] == lH[j].filename:
			counter3 += 1
	if counter3 != 1:
		print("ERROR: %s header file doesn't exist, can't generate makefile" % incList[i])
		sys.exit()
	counter3 = 0



readyToGenerate = True #Boolean to start generating makefile.

makeHList = []	#List which will store ".h" files which will be included in makefile.

i=0
for i in range(len(lH)):
    if (lH[i].usedInMain == True and lH[i].incInMain == False):	#If a ".h" file's function is used in main 
    															#but it's header is not included in main, give the error
    															#and exit the program.
        readyToGenerate = False
        print("Error, %s is used in main but not included, can't generate makefile." % lH[i].filename)
        sys.exit()

    elif (lH[i].usedInMain == False and lH[i].incInMain == True): #If a ".h" file's header is included in main
    															  #but it's function is not used in main,
    															  #gives warning but still generates the make file.
        print("Warning: %s is included but not used in Main" % lH[i].filename)

    elif(lH[i].usedInMain == False and lH[i].incInMain == False):
    	print("Warning: %s is not included and not used in Main" % lH[i].filename)

    else:
        makeHList.append(lH[i])		#If ".h" file's header is both included in main
        							#and it's function is used in main, append it to this list
        							#and it will be used in makefile.

headerPaths = False
tmpPath = makeHList[0].pathWithoutName	#Part that controls if header files are in the same path or not.
										#If they are not in the same path, extra arguments will be added to makefile.
for i in range(len(makeHList)):
    if makeHList[i].pathWithoutName == tmpPath:
        headerPaths = True
    else:
        headerPaths = False

makefile = "Makefile"
completeName = os.path.join(sys.argv[1], makefile)

if readyToGenerate:
    file = open(completeName, "w")

    # First Lines for creating main#.exe lines.
    file.write("%s:    " % mainC.filename.replace('.c','.exe'))
    file.write("%s " % (mainC.onlyName))
    for i in range(len(makeHList)):
        file.write("%s "% makeHList[i].onlyName)
    file.write("\n\tgcc %s " % mainC.onlyName)
    for i in range(len(makeHList)):
        file.write("%s "% makeHList[i].onlyName)
    file.write("-o %s\n\n"% mainC.filename.replace('.c','.exe'))

    #Second part of makefile, which has the main#.o part.
    file.write("%s:\t%s "% (mainC.onlyName, mainC.filename))
    for i in range(len(makeHList)):
        file.write("%s "% makeHList[i].filepath)
    if headerPaths == True:
        file.write("\n\tgcc -c -I %s " % makeHList[i].pathWithoutName)
    else:
        file.write("\n\tgcc -c ")
        for i in range(len(makeHList)):   
            file.write("-I %s " % makeHList[i].pathWithoutName)
    file.write("%s\n\n" % mainC.filename)

    #Third part, which we write header file's .o parts.
    for i in range(len(makeHList)):
        file.write("%s:\t"% makeHList[i].onlyName)
        for j in range(len(lC)):
            if makeHList[i].onlyName == lC[j].onlyName:
                file.write("%s " % lC[j].filepath)
                break
        file.write("%s\n"%makeHList[i].filepath)
        file.write("\tgcc -c -I %s %s\n\n"% (makeHList[i].pathWithoutName, lC[j].filepath))




    file.close()
print("Makefile generated in: %s"%sys.argv[1])