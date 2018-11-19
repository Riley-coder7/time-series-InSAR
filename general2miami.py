#! /usr/bin/env python
############################################################
# Program is part of PySAR v1.0                            #
# Copyright(c) 2013, Heresh Fattahi                        #
# Author:  Heresh Fattahi                                  #
############################################################
#
# Yunjun, Jul 2015: Add check_num/check_file_size to .int/.cor file
# Yunjun, Jan 2017: Add auto_path_miami(), copy_roipac_file()
#                   Add load_roipac2multi_group_h5()
#                   Add r+ mode loading of multi_group hdf5 file


import os
import sys
import glob
import time
import argparse

import h5py
import numpy as np

import pysar
import pysar._readfile as readfile
import pysar._pysar_utilities as ut



##########################  Usage  ###############################

def cmdLineParse():
    parser = argparse.ArgumentParser(description='Load ROI_PAC data.\n'\
                                     'Load ROI_PAC product (from process_dir to timeseries_dir) for PySAR analysis.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=TEMPLATE+'\n'+EXAMPLE)
    parser.add_argument('project_name', help='project name.')
    parser.add_argument('unw_file', help='unwrap file.')
    parser.add_argument('cor_file', help='coherence file.')
    parser.add_argument('dem_rdc', help='radar dem file.')
    parser.add_argument('dem_geo', help='geo dem file.')
    parser.add_argument('rdc2geo', help='lookup table file.')
    parser.add_argument('slcpar', help='slc par file.')
    parser.add_argument('mlipar', help='multilooked par file.')
    parser.add_argument('geopar', help='geocoded dem par file.')

    inps = parser.parse_args()
    return inps


#############################  Main Function  ################################
def main(argv):
    inps = cmdLineParse()
    scratchDir = os.getenv('SCRATCHDIR')
    projectname = inps.project_name
    unw_file = inps.unw_file
    cor_file = inps.cor_file
    dem_rdc = inps.dem_rdc
    dem_geo = inps.dem_geo
    geopar = inps.geopar
    rdc2geo = inps.rdc2geo
    slcpar = inps.slc_par
    
    call_str= 'mkdir ' + projectname
    os.system(call_str)
    
    projectDir = scratchDir + '/' +projectname
    os.chdir(projectDir)
    call_str ='mkdir SLC'
    os.system(call_str)
    
    call_str = 'mkdir RSLC'
    os.system(call_str)
    
    slcdir = projectDir + '/SLC'
    rslcdir = projectDir + '/RSLC'
    
    call_str = 'mkdir PROCESS'
    os.system(call_str)
    
    processDir = projectDir + '/PROCESS'
    os.chdir(processDir)
    
    call_str = 'mkdir DEM'
    os.system(call_str)
    demDir = projectDir + '/PROCESS/DEM'
    
    UNWLIST = glob.glob(unw_file)
    CORLIST = glob.glob(cor_file)
    SLCPARLIST = glob.glob(slcpar)
    
    for i in range(len(UNWLIST)):
        UNW0 = os.path.basename(UNWLIST[i])
        DATE12 = UNW0.split('.')[0]
        if len(DATE12)==17:
            MM = DATE12[0:8]
            SS = DATE12[9:17]              
        else:
            MM = DATE12[0:6]
            SS = DATE12[7:13]
        
        STR = projectname + '_IFG_'+ MM + '-' + SS + '0000_0000'
        if os.path.isdir(STR):
                call_str ='mkdir ' + STR
                os.system(call_str)
        call_str = 'cp ' +   UNWLIST[i] + ' ' + processDir + '/' + STR  
        os.systen(call_str)
        
    for i in range(len(CORLIST)):
        COR0 = os.path.basename(CORLIST[i])
        DATE12 = COR0.split('.')[0]
        if len(DATE12)==17:
            MM = DATE12[0:8]
            SS = DATE12[9:17]              
        else:
            MM = DATE12[0:6]
            SS = DATE12[7:13]
        
        STR = projectname + '_IFG_'+ MM + '-' + SS + '0000_0000'
        if os.path.isdir(STR):
                call_str ='mkdir ' + STR
                os.system(call_str)
        call_str = 'cp ' +   CORLIST[i] + ' ' + processDir + '/' + STR  
        os.systen(call_str)
        
        
    for i in range(len(SLCPARLIST)):
        PAR0 = os.path.basename(SLCPARLIST[i])
        DATE = COR0.split('.')[0]
        if len(DATE)==8:
            DATE = DATE[0:6]
        PAR1 = DATE + '.slc.par'
        RPAR1 = DATE + '.rslc.par'
         
         
        call_str = 'cp ' + PAR0 + ' ' + slcdir + '/' + PAR1
        os.system(call_str)
         
        call_str = 'cp ' + PAR0 + ' ' + rslc + '/' + RPAR1
        os.system(call_str) 
        
        call_str = 'cp ' + dem_rdc + ' ' + demDir
        os.system(call_str)
        
        call_str = 'cp ' + dem_geo + ' ' + demDir
        os.system(call_str)
        
        call_str = 'cp ' + rdc2geo + ' ' + demDir
        os.system(call_str)
        
        call_str = 'cp ' + geopar + ' ' + demDir
        os.system(call_str)
        

##############################################################################
if __name__ == '__main__':
    main(sys.argv[1:])
