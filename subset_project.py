#! /usr/bin/env python
#################################################################
###  This program is part of PyMIS  v1.0                      ### 
###  Copy Right (c): 2017, Yunmeng Cao                        ###  
###  Author: Yunmeng Cao                                      ###                                                          
###  Email : ymcmrs@gmail.com                                 ###
###  Univ. : Central South University & University of Miami   ###   
#################################################################




import os
import sys
import getopt
import time
import argparse
import h5py
from numpy import std

import pysar._datetime as ptime
import pysar._readfile as readfile



    
#########################################################################

INTRODUCTION = '''
#############################################################################
   Copy Right(c): 2017, Yunmeng Cao   @PyMIS v1.0   
   
   Extractting subset files from exited files. 
   
'''

EXAMPLE = '''
    Usage:
            subset_project.py projectname az_numb rg_numb   
    Examples:
            subset_project.py Hunan_SW 2 2     
##############################################################################
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Extractting subset files from exited files. ',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectname',help='Subset region.')
    parser.add_argument('az_numb',help='number of patch in azimuth.')
    parser.add_argument('rg_numb',help='number of patch in range')

    
    inps = parser.parse_args()

    return inps

################################################################################

def main(argv):

    inps = cmdLineParse()
    projectName = inps.projectname
    az_numb = inps.az_numb
    rg_numb = inps.rg_numb
    
    scratchDir = os.getenv('SCRATCHDIR')
    scratchDir='/Volumes/Yunmeng_Seagate/Hunan_all'
    projectDir = scratchDir + '/' + projectName
    pysarDir = projectDir + '/PYSAR'
    UNW  = pysarDir + '/unwrapIfgram.h5'
    COR = pysarDir + '/coherence.h5'
    demRdc = pysarDir + '/demRadar.h5'
    demGeo = pysarDir + '/demGeo.h5'
    rdc2geo =  pysarDir + '/geometryGeo.h5'
    
    atr = readfile.read_attribute(UNW)
    WIDTH = atr['WIDTH']
    LENGTH = atr['FILE_LENGTH']
    
    
    dx = int(int(WIDTH)/int(rg_numb))
    dy = int(int(LENGTH)/int(az_numb))
    
    for i in range(int(rg_numb)):
        for j in range(int(az_numb)):
            STR = 'SUBSET'+ str(i) + str(j)
            call_str = 'mkdir ' + STR
            os.system(call_str)
            os.chdir(pysarDir+'/' + STR)
            X0 = str(int(int(i)*dx-1))
            X1 = str(int(int(i)*dx + dx))
            
            Y0 = str(int(int(j)*dy-1))
            Y1 = str(int(int(j)*dy+dy))
            
            call_str ='subset.py ' + UNW + ' ' + COR + ' ' + demRdc + ' -y ' + Y0 + ' ' + Y1 + ' -x ' + X0 + ' ' + X1
            os.system(call_str)  
             
            call_str = 'cp ' + rdc2geo + ' .'
            os.system(call_str)  
    
        
    print ''
    print 'Done.'

    
if __name__ == '__main__':
    main(sys.argv[1:])    
    
    
    
    
    
    
    
    
    
    
    
    
    
    





