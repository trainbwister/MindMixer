#!/bin/env python


files = ["1.png","2.png"]


import sys
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-f", "--file", dest="filename",
                  help="write report to FILE", metavar="FILE")
parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")

(options, args) = parser.parse_args()




### Begin Selftests ###
die = None
for f in files:
    try:
        open(f,"r")
    except IOError, e:
        die = e
        print "FATAL:",die
raise die
print "All important data present"
### End Selftests ###


import time
from pygame import Surface
