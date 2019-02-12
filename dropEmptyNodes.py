#!/usr/bin/python

# Ugly hack to drop empty nodes
# Assumes empty nodes are shortest line lengths

import sys

inFileName = sys.argv[1]
outFileName = sys.argv[2]


inFile = open(inFileName, "r") 
outFile = open(outFileName, "w")
for line in inFile: 
   #print line, 
   if ((len(line) > 100) or not line.startswith('<node', 0)):
	  outFile.write(line)

inFile.close()
outFile.close()


