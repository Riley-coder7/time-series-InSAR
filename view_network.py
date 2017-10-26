#! /usr/bin/env python
############################################################                                                     
# Program is part of PYMIS   v1.0                          #
# Copyright(c) 2017, Yunmeng Cao                           #
# Author :  Yunmeng Cao                                    # 
# Company:  Central South University                       #                                                       
############################################################


import os
import sys
import glob
import time
import argparse

import h5py
import numpy as np

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    
def add_zero(s):
    if len(s)==1:
        s="000"+s
    elif len(s)==2:
        s="00"+s
    elif len(s)==3:
        s="0"+s
    return s

#########################################################################

INTRODUCTION = '''
#############################################################################
   Copy Right(c): 2017, Yunmeng Cao   @PyMIS v1.0   
   
  View SBAS network of interferograms based on different maximum baseline parameters.
   
'''

EXAMPLE = '''
    Usage:
            view_network.py projectName 
            view_network.py projectName --TB maxmum_temporal_baseline --SB maximum_spatial_baseline
            
    Examples:
            view_network.py PichinchaSMT51TsxD 
            view_network.py PichinchaSMT51TsxD --TB 300 
            view_network.py PichinchaSMT51TsxD --TB 300 --SB 150

##############################################################################
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='View SBAS network of interferograms.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName',help='Name of project.')
    parser.add_argument('--TB',dest = 'TB', help='Maximum temporal baseline. [default: 500]')
    parser.add_argument('--SB',dest = 'SB', help='Maximum spatial baseline. [default: 300]')
    
    inps = parser.parse_args()

    return inps

################################################################################

def main(argv):

    inps = cmdLineParse()
    projectName = inps.projectName   
    scratchDir = os.getenv('SCRATCHDIR')
    processDir = scratchDir + '/' + projectName +  '/PROCESS'
    slcDir     = scratchDir + '/' + projectName + "/SLC"
    TB_TXT = processDir + '/TS_Berp_all'
    BL_list = processDir + '/bl_list.txt'
    if os.path.isfile(BL_list):
        os.remove(BL_list)
        
    Datelist = []
    ListSLC = os.listdir(slcDir)
    

    for kk in range(len(ListSLC)):
        if ( is_number(ListSLC[kk]) and len(ListSLC[kk])==6 ):    #  if SAR date number is 8, 6 should change to 8.
            DD=ListSLC[kk]
            Year=int(DD[0:2])
            Month = int(DD[2:4])
            Day = int(DD[4:6])
            if  ( 0 < Year < 20 and 0 < Month < 13 and 0 < Day < 32 ):            
                Datelist.append(ListSLC[kk])
                
    N_SAR = len(Datelist)            
    call_str = 'Calc_Base_All.py ' + projectName + ' >ttt'
    os.system(call_str)
    
    TB_NP = np.loadtxt(TB_TXT) 
    Master = TB_NP[:,1]
    Slave = TB_NP[:,2]
    BERP =TB_NP[:,3]
    Mdate = Master[0]
    
    Master =np.asarray(Master)
    Slave =np.asarray(Slave)
    BERP =np.asarray(BERP)
    
    
    Slave1 = Slave[0:N_SAR-1]    
    BERP1 = BERP[0:N_SAR-1]
    #print BERP1
    
    call_str ='echo ' + str(int(Mdate))[2:8] + '   ' + ' 0  0  0  0  0  0  0 >>' + BL_list
    os.system(call_str)
    
    for kk in range(len(Slave1)):
        call_str ='echo ' + str(int(Slave1[kk]))[2:8] + '   ' + str(BERP1[kk]) + '   0  0  0  0  0  0  0 >>' + BL_list
        os.system(call_str)
    
    if inps.TB: 
        TSTR = ' --TB ' + inps.TB
        TB ='_' + inps.TB
    else: 
        TSTR = ' '
        TB='_all'
        
    if inps.SB: 
        BSTR = ' --SB ' + inps.SB
        SB = '_' +inps.SB
    else: 
        BSTR = ''
        SB = '_all'
 
    
    SLC_Tab = processDir + "/SLC_Tab" + TB + SB
    TS_Berp = processDir + "/TS_Berp" + TB + SB
    TS_Itab = processDir + "/TS_Itab" + TB + SB
      
    if not inps.TB and not inps.SB:
        SLC_Tab = processDir + "/SLC_Tab_all"
        TS_Berp = processDir + "/TS_Berp_all"
        TS_Itab = processDir + "/TS_Itab_all"
        
    #if not os.path.isfile(TS_Berp):
    call_str = 'Generate_SBAS_list.py ' + projectName + TSTR + BSTR + ' >ttt'
    os.system(call_str)
    
    SBAS = np.loadtxt(TS_Berp)
    Master = SBAS[:,1]
    Slave = SBAS[:,2]

    Master =Master.tolist()
    Slave =Slave.tolist()
    
    IFG_LIST = processDir + '/ifg_list' + os.path.basename(TS_Berp).split('TS_Berp')[1] + '.txt'
    if os.path.isfile(IFG_LIST):
        os.remove(IFG_LIST)
    
    for kk in range(len(Master)):
        STR = str(int(Master[kk]))[2:8] + '-' + str(int(Slave[kk]))[2:8]
        call_str ='echo ' + STR + ' >>' + IFG_LIST
        os.system(call_str)

    call_str = 'plot_network.py ' + IFG_LIST  + ' -b ' + BL_list
    os.system(call_str)
    
    
    sys.exit(1)
    
    

##############################################################################
if __name__ == '__main__':
    main(sys.argv[1:])
