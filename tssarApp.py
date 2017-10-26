#! /usr/bin/env python
############################################################                                                     
# Program is part of TSSAR   v1.0                          #
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

def print_progress(iteration, total, prefix='calculating:', suffix='complete', decimals=1, barLength=50, elapsed_time=None):
    """Print iterations progress - Greenstick from Stack Overflow
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : number of decimals in percent complete (Int) 
        barLength   - Optional  : character length of bar (Int) 
        elapsed_time- Optional  : elapsed time in seconds (Int/Float)
    
    Reference: http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
    """
    filledLength    = int(round(barLength * iteration / float(total)))
    percents        = round(100.00 * (iteration / float(total)), decimals)
    bar             = '#' * filledLength + '-' * (barLength - filledLength)
    if elapsed_time:
        sys.stdout.write('%s [%s] %s%s    %s    %s secs\r' % (prefix, bar, percents, '%', suffix, int(elapsed_time)))
    else:
        sys.stdout.write('%s [%s] %s%s    %s\r' % (prefix, bar, percents, '%', suffix))
    sys.stdout.flush()
    if iteration == total:
        print("\n")

    '''
    Sample Useage:
    for i in range(len(dateList)):
        print_progress(i+1,len(dateList))
    '''
    return


def GetSubset(Subset):
    Dx = Subset.split('[')[1].split(']')[0].split(',')[0]
    Dy = Subset.split('[')[1].split(']')[0].split(',')[1]
    
    x1 = Dx.split(':')[0]
    x2 = Dx.split(':')[1]
    
    y1 = Dy.split(':')[0]
    y2 = Dy.split(':')[1]
    
    return x1,x2,y1,y2

def check_variable_name(path):
    s=path.split("/")[0]
    if len(s)>0 and s[0]=="$":
        p0=os.getenv(s[1:])
        path=path.replace(path.split("/")[0],p0)
    return path

def read_template(File, delimiter='='):
    '''Reads the template file into a python dictionary structure.
    Input : string, full path to the template file
    Output: dictionary, pysar template content
    Example:
        tmpl = read_template(KyushuT424F610_640AlosA.template)
        tmpl = read_template(R1_54014_ST5_L0_F898.000.pi, ':')
    '''
    template_dict = {}
    for line in open(File):
        line = line.strip()
        c = [i.strip() for i in line.split(delimiter, 1)]  #split on the 1st occurrence of delimiter
        if len(c) < 2 or line.startswith('%') or line.startswith('#'):
            next #ignore commented lines or those without variables
        else:
            atrName  = c[0]
            atrValue = str.replace(c[1],'\n','').split("#")[0].strip()
            atrValue = check_variable_name(atrValue)
            template_dict[atrName] = atrValue
    return template_dict

def read_data(inFile, dtype, nWidth, nLength):
    data = np.fromfile(inFile, dtype, int(nLength)*int(nWidth)).reshape(int(nLength),int(nWidth))  
    return data

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


def GeoCoord2RdcCoord(LTH5, LAT, LON):
    f = h5py.File(LTH5, 'r')
    LT = f['lt'].get('lt')[()]
    Corner_LAT = f['lt'].attrs['Y_FIRST']
    Corner_LON = f['lt'].attrs['X_FIRST']
    post_Lat = f['lt'].attrs['Y_STEP']
    post_Lon = f['lt'].attrs['X_STEP']
    f.close()
    
    XX = int (( float(LAT) - float(Corner_LAT) ) / float(post_Lat))  # latitude   width   range
    YY = int (( float(LON) - float(Corner_LON) ) / float(post_Lon))  # longitude   nline  azimuth
     
    CPX_OUT = LT[XX][YY]    
    Range = str(int(CPX_OUT.real))
    Azimuth = str(int(CPX_OUT.imag))
      
    return Range, Azimuth
    
def RdcCoord2GeoCoord(LTH5, Ra, Az):
    f = h5py.File(LTH5, 'r')
    LT = f['lt'].get('lt')[()]
    Corner_LAT = f['lt'].attrs['Y_FIRST']
    Corner_LON = f['lt'].attrs['X_FIRST']
    post_Lat = f['lt'].attrs['Y_STEP']
    post_Lon = f['lt'].attrs['X_STEP']
    f.close()
    
    Range_LT = LT.real
    Azimuth_LT = LT.imag
    
    CPX_input =complex(Ra + '+' + Az+'j')   
    DD = abs(CPX_input - LT)   
    LL= abs(DD)
    IDX= np.where(LL == LL.min())
    Lat_out = float(Corner_LAT) + IDX[0]*float(post_Lat)       
    Lon_out = float(Corner_LON) + IDX[1]*float(post_Lon)
    
    return Lat_out, Lon_out
    

def GeoSub2RdcSub(LTH5,GeoSubStr):
    LL = GetSubset(GeoSubStr)
    Lat1 = LL[0]
    Lat2 = LL[1]
    Lon1 = LL[2]
    Lon2 = LL[3]
    
    Ra = np.zeros([1,4])
    Az = np.zeros([1,4])
    
    Ra[0][0],Az[0][0] = GeoCoord2RdcCoord(LTH5,Lat1,Lon1)
    Ra[0][1],Az[0][1] = GeoCoord2RdcCoord(LTH5,Lat1,Lon2)
    Ra[0][2],Az[0][2] = GeoCoord2RdcCoord(LTH5,Lat2,Lon1)
    Ra[0][3],Az[0][3] = GeoCoord2RdcCoord(LTH5,Lat2,Lon2)
    
    Range_Min = str(int(min(Ra[0][:])))
    Range_Max = str(int(max(Ra[0][:])))
    
    Azimuth_Min = str(int(min(Az[0][:])))
    Azimuth_Max = str(int(max(Az[0][:])))
    
    return Range_Min, Range_Max, Azimuth_Min, Azimuth_Max

def RdcSub2GeoSub(LTH5,RdcSubStr):
    LL = GetSubset(RdcSubStr)
    Ra1 = LL[0]
    Ra2 = LL[1]
    Az1 = LL[2]
    Az2 = LL[3]
    
    La = np.zeros([1,4])
    Lo = np.zeros([1,4])
    
    La[0][0],Lo[0][0] = RdcCoord2GeoCoord(LTH5,Ra1,Az1)
    La[0][1],Lo[0][1] = RdcCoord2GeoCoord(LTH5,Ra1,Az2)
    La[0][2],Lo[0][2] = RdcCoord2GeoCoord(LTH5,Ra2,Az1)
    La[0][3],Lo[0][3] = RdcCoord2GeoCoord(LTH5,Ra2,Az2)
    
    Lat_Min = str(min(La[0][:]))
    Lat_Max = str(max(La[0][:]))
    
    Lon_Min = str(min(Lo[0][:]))
    Lon_Max = str(max(Lo[0][:]))
    
    return Lat_Min, Lat_Max, Lon_Min, Lon_Max
    
def UseGamma(inFile, task, keyword):
    if task == "read":
        f = open(inFile, "r")
        while 1:
            line = f.readline()
            if not line: break
            if line.count(keyword) == 1:
                strtemp = line.split(":")
                value = strtemp[1].strip()
                return value
        print "Keyword " + keyword + " doesn't exist in " + inFile
        f.close()
        
def UseGamma2(inFile, task, keyword):
    if task == "read":
        f = open(inFile, "r")
        while 1:
            line = f.readline()
            if not line: break
            if line.count(keyword) == 1:
                strtemp = line.split(":")
                value = strtemp[2].strip()
                return value
        print "Keyword " + keyword + " doesn't exist in " + inFile
        f.close()
        
def usage():
    print '''
******************************************************************************************************
 
           time series processing based on TSSAR

           usage:
   
                 tssarApp.py projectName
                 tssarApp.py projectName DirName
      
           e.g.  tssarApp.py PacayaT163TsxHhA
           e.g.  tssarApp.py PacayaT163TsxHhA ProcArea
          
            
*******************************************************************************************************
    '''   

def main(argv):
    
    total = time.time()
    DirName = 'PROCESS'
    if len(sys.argv)==2:
        if argv[0] in ['-h','--help']: usage(); sys.exit(1)
        else: projectName=sys.argv[1]        
    if len(sys.argv)==3:
        projectName = sys.argv[1]   
        DirName = sys.argv[2]  
    else:
        usage();sys.exit(1)
         
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    templateContents=read_template(templateFile)
    
    processDir = scratchDir + '/' + projectName + "/PROCESS"    
    masterDate = templateContents['masterDate']
    rlks = templateContents['Range_Looks']
    azlks = templateContents['Azimuth_Looks']
    tsDir    = processDir + '/TSSAR/TSH5'          # all data loaded into TSH5
       
    UNWH5 = tsDir + '/unwrapIfgram.h5'
    INFH5 = tsDir + '/wrapIfgram.h5'
    CORH5 = tsDir + '/coherence.h5'
    MASKH5 = tsDir + '/unwrapIfgram.h5'
    RDCDEM = tsDir + '/demRdc.h5'
    GEODEM = tsDir + '/demGeo.h5'
    GEOTRANS = tsDir + '/geo2rdc.h5'
    

    f =h5py.File(GEODEM)
    k1 = f.keys()[0]
    nWidthUTM = f[k1].attrs['WIDTH']
    nLineUTM = f[k1].attrs['FILE_LENGTH']
    Corner_LAT = f[k1].attrs['Y_FIRST']
    Corner_LON = f[k1].attrs['X_FIRST']
    post_Lat = f[k1].attrs['Y_STEP']
    post_Lon = f[k1].attrs['X_STEP']   
    f.close()
    

    
    f =h5py.File(UNWH5)
    k1 = f.keys()[0]
    k2 = f[k1].keys()[0]
    N_Inf0 = len(f[k1].keys())
    nWidth = f[k1][k2].attrs['WIDTH']
    nLine = f[k1][k2].attrs['FILE_LENGTH']
    f.close()

    SubRdc=''
    SubGeo=''
    
    if 'Subset_Rdc' in templateContents: SubRdc = templateContents['Subset_Rdc']
    if 'Subset_Geo' in templateContents: SubGeo = templateContents['Subset_Geo']
   
    if len(SubGeo) > 0:
        DirName = 'GEO_' + DirName      
    workDir = processDir + '/TSSAR' + '/' + DirName
    
    
    if len(SubGeo) > 0:
        TSDEM = workDir + '/demGeo_proc.h5'
    else:
        TSDEM = workDir + '/demRdc_proc.h5'
    
    TSUNW = workDir + '/unwrapIfgram_proc.h5'
    TSINF = workDir + '/wrapIfgram_proc.h5'
    TSCOR = workDir + '/coherence_proc.h5'
    TSMASK = workDir + '/mask.h5'

    TSDEM = workDir + '/demRdc_proc.h5'
    
    SEEDUNW = workDir + '/seed_unwrapIfgram_proc.h5'
    PLANESEEDUNW = workDir + '/plane_seed_unwrapIfgram_proc.h5'
    
    TSFILE = workDir + '/timeseries.h5'
    TEMCOR = workDir + '/temporal_coherence.h5'
    
    TS_DEMCOR = workDir + '/timeseries_DemCor.h5'
    TS_DEMCOR_TROPCOR = workDir + '/timeseries_DemCor_TropCor.h5'   

    
    
    TSRDCDEM0 = workDir + '/demRdc.h5'
    TSGEODEM0 = workDir + '/demGeo.h5'
    TSGEOTRANS = workDir + '/geo2rdc.h5'
    
    
    print ''
    print 'Change process Dir to :' + workDir
    os.chdir(workDir)
    
    VELOCITY = workDir  + '/velocity.h5'
    TEMCOR = workDir + '/temporal_coherence.h5'
    
    seed_x = templateContents['Seed_X']
    seed_y = templateContents['Seed_Y']
    
    
    if 'UNWRAP_SUB_TSSAR' in templateContents: UNWRAP_SUB_TSSAR = templateContents['UNWRAP_SUB_TSSAR']                
    else: UNWRAP_SUB_TSSAR = '1'
    
    if UNWRAP_SUB_TSSAR == '1':
        call_str = 'unwrap_sub_tssar.py -f' + TSINF + ' -w ' + TSCOR
        os.system(call_str)    
        TSUNW = workDir + '/unwrapIfgram_mcf_proc.h5'
    else:
        TSUNW = workDir + '/unwrapIfgram_proc.h5'
    
    print ''
    print 'Seeding unwrapped images to reference point (%s, %s) >>>' % (seed_y,seed_x)
    call_str = 'seed_data.py ' + TSUNW +' -y ' + seed_y + ' -x ' + seed_x + ' -o ' + SEEDUNW
    os.system(call_str)
    
    print ''
    print 'Remove plane in unwrap image >>>'
    call_str = 'remove_plane.py '  + SEEDUNW  + ' -m ' + TSMASK + ' -o ' + PLANESEEDUNW
    os.system(call_str)
    
    print ''
    print 'Time series inversion based on timeseries unwrapped images >>>'
    call_str = 'igram_inversion.py ' + '-f ' + PLANESEEDUNW + ' -o ' + TSFILE
    os.system(call_str)
    
    print ''
    print 'Temporal coherence estimation >>>'
    call_str = 'temporal_coherence.py ' + PLANESEEDUNW + ' ' + TSFILE + ' ' + TEMCOR
    os.system(call_str)
    
    call_str = 'view.py ' + TEMCOR
    os.system(call_str)
    
    print ' '
    print 'DEM error correction >>>'
    call_str = 'dem_error.py ' + TSFILE + ' -o ' + TS_DEMCOR
    os.system(call_str)
    
    print ' '
    print 'Velocity estimation >>>'
    call_str = 'timeseries2velocity.py '  + TS_DEMCOR 
    os.system(call_str)
    
    print "Time series processing is done!"
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[1:])