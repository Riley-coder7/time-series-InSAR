#! /usr/bin/env python
############################################################                                                     
# Program is part of PYSAR   v1.2                          #
# Copyright(c) 2017, Yunmeng Cao                           #
# Author :  Yunmeng Cao                                    #                                                    
############################################################

import os
import sys
import glob
import time
import argparse
import getopt

import h5py
import numpy as np

multi_group_hdf5_file=['interferograms','coherence','wrapped','snaphu_connect_component']
multi_dataset_hdf5_file=['timeseries']
single_dataset_hdf5_file=['dem','mask','rmse','temporal_coherence', 'velocity']

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

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def read_data(inFile, dtype, nWidth, nLength):
    data = np.fromfile(inFile, dtype, int(nLength)*int(nWidth)).reshape(int(nLength),int(nWidth))  
    return data  

def RdcCoord2LTCoord(LTH5, Ra, Az):
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
    Lat_IDX = IDX[0]  
    Lon_IDX = IDX[1]  
    print Lat_IDX
    print Lon_IDX
    return Lat_IDX, Lon_IDX


def geocode(inFile, outFile, UTMTORDC, nWidth, nWidthUTMDEM, nLineUTMDEM):
    if ('.int' in os.path.basename(inFile)) or ('.diff' in  os.path.basename(inFile)): 
        call_str = '$GAMMA_BIN/geocode_back ' + inFile + ' ' + nWidth + ' ' + UTMTORDC + ' ' + outFile + ' ' + nWidthUTMDEM + ' ' + nLineUTMDEM + ' 0 1 > tt'
    else:
        call_str = '$GAMMA_BIN/geocode_back ' + inFile + ' ' + nWidth + ' ' + UTMTORDC + ' ' + outFile + ' ' + nWidthUTMDEM + ' ' + nLineUTMDEM + ' 0 0 > tt'
    os.system(call_str)

    
###################################################################################################

INTRODUCTION = '''
    Geocoding PYSAR files (i.e., h5 files) based on GAMMA lookup table.
    1) Lookup table should be available, like geo2rdc.h5      -f
    2) If no lookup table is found, projectName should be provided to generate a h5 lookup table.   -p
      
'''

EXAMPLE = '''EXAMPLES:
    geocode_pysar.py H5File -f lookup-table -p projectName
    geocode_pysar.py velocity.h5 -f geo2rdc.h5 
    geocode_pysar.py velocity.h5 -p projectName 
'''    
    


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Geocode h5 file based on GAMMA lookup table.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('file',help='h5 file that will be geocoded.')
    parser.add_argument('-f', dest='lt', help='Lookup table ')
    parser.add_argument('-p', dest='projectName', help='project name which is used to search possible GAMMA lookup table.')
    
    parser.add_argument('-o', dest='out', help='Output name of the geocoded file. ')
    
    inps = parser.parse_args()
   
    if not inps.projectName and not inps.lt:
        parser.print_usage()
        sys.exit(os.path.basename(sys.argv[0])+': error: projectName and lookup table File, at least one is needed.')
    return inps


    
####################################################################################################
def main(argv):
    
    inps = cmdLineParse()
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
        
        
    if inps.lt:
        LT = inps.lt
        print 'Lookup table file is %s.' % LT
    else:
        projectName = inps.projectName 
        simDir = scratchDir + '/' + projectName + '/PROCESS/SIM'
        templateFile = templateDir + '/' + projectName + '.template'
        
        SIM = simDir + '/sim_*'
        DEMDIR = glob.glob(SIM)[0]
        
        UTM2RDC = glob.glob(DEMDIR + '/*.UTM_TO_RDC')[0]  # the name of UTM2RDC maybe different with this
        UTMPAR = glob.glob(DEMDIR + '/*.utm.dem.par')[0] 
        
        Dem_Format = UseGamma(UTMPAR, 'read', 'data_format:') 
    
        if Dem_Format=='REAL*4':
            dtype_utmdem='f4'
        else:
            dtype_utmdem='i2'
    
        nWidthUTM = UseGamma(UTMPAR, 'read', 'width:')
        nLineUTM  = UseGamma(UTMPAR, 'read', 'nlines:')
   
        Corner_LAT = UseGamma(UTMPAR, 'read', 'corner_lat:') 
        Corner_LON = UseGamma(UTMPAR, 'read', 'corner_lon:')

        Corner_LAT =Corner_LAT.split(' ')[0]
        Corner_LON =Corner_LON.split(' ')[0]

        post_Lat = UseGamma(UTMPAR, 'read', 'post_lat:')
        post_Lon = UseGamma(UTMPAR, 'read', 'post_lon:')

        post_Lat =post_Lat.split(' ')[0]
        post_Lon =post_Lon.split(' ')[0]
        
        if 'pysar.transFile' in templateContents: TransFile = templateContents['pysar.transFile']
        else:    TransFile = UTM2RDC
            
        if not os.path.isfile(TransFile):
            print 'pysar.transFile is not found.'
            sys.exit(1)
        if 'Byte_order' in  templateContents: byteoder = templateContents['Byte_order']
        else: byteorder = 'big'
            
        UTM2RDC = 'geo2rdc.h5'
            
        if byteorder =='big':
            sign = '>'
        else:
            sign ='<'

        dtype_lt = sign + 'c8'
        
        print 'Start to write GEO2RDC into h5 file >>> ' + TransFile
        data = read_data(UTM2RDC,dtype_lt,nWidthUTM,nLineUTM)   # real: range     imaginary: azimuth
        H5FILE = 'geo2rdc.h5'
        f =h5py.File(H5FILE,'w')
        group=f.create_group('lt')
        dset = group.create_dataset('lt', data=data, compression='gzip')
        group.attrs['WIDTH'] = nWidthUTM
        group.attrs['FILE_LENGTH'] = nLineUTM
        group.attrs['X_FIRST'] = Corner_LON    # X: latitude    Y: longitude
        group.attrs['Y_FIRST'] = Corner_LAT
        group.attrs['X_STEP'] = post_Lon
        group.attrs['Y_STEP'] = post_Lat
        group.attrs['X_UNIT'] = 'degrees'
        group.attrs['Y_UNIT'] = 'degrees'
        group.attrs['X_MIN'] = '0'
        group.attrs['X_MAX'] = str(int(nWidthUTM)-1)
        group.attrs['Y_MIN'] = '0'
        group.attrs['Y_MAX'] = str(int(nLineUTM)-1)
        group.attrs['DATATYPE'] = dtype_lt
        f.close()
        LT = 'geo2rdc.h5'    
        
      
    f_lt = h5py.File(LT,'r')
    kl1 = f_lt.keys()[0]
    kl2 = f_lt[kl1].keys()[0]
    datalt = f_lt[kl1].get(kl2)[()]
    atr_lt = f_lt[kl1].attrs 
    nWidthUTM = f_lt[kl1].attrs['WIDTH']
    nLineUTM = f_lt[kl1].attrs['FILE_LENGTH']
    
    
    LTFile = 'rdc2geo.trans'
    datalt.tofile(LTFile)

################################# Input file definition  ##################################################

    FILE = inps.file
    f = h5py.File(FILE,'r')
    k1 = f.keys()[0]
    k2 = f[k1].keys()
    
    if k1 in multi_group_hdf5_file:
        if 'WIDTH_ORIG' in f[k1][k2[0]].attrs:
            WIDTH_ORIG = f[k1][k2[0]].attrs['WIDTH_ORIG'] 
            FILE_LENGTH_ORIG = f[k1][k2[0]].attrs['FILE_LENGTH_ORIG']
            X_MIN = f[k1][k2[0]].attrs['X_MIN']  #RANGE
            X_MAX = f[k1][k2[0]].attrs['X_MAX']
            Y_MIN = f[k1][k2[0]].attrs['Y_MIN']  # AZIMUTH
            Y_MAX = f[k1][k2[0]].attrs['Y_MAX']
            dtype = f[k1][k2[0]].attrs['DATATYPE']
        else:
            WIDTH_ORIG = f[k1][k2[0]].attrs['WIDTH'] 
            FILE_LENGTH_ORIG = f[k1][k2[0]].attrs['FILE_LENGTH']
            X_MIN = '0'  #RANGE
            X_MAX = str(int(WIDTH_ORIG)-1)
            Y_MIN = '0'  # AZIMUTH
            Y_MAX =  str(int(FILE_LENGTH_ORIG)-1)
            dtype = f[k1][k2[0]].attrs['DATATYPE']
    elif k1 in multi_dataset_hdf5_file + single_dataset_hdf5_file:
        if 'WIDTH_ORIG' in f[k1].attrs:
            print 'YES'
            WIDTH_ORIG = f[k1].attrs['WIDTH_ORIG'] 
            FILE_LENGTH_ORIG = f[k1].attrs['FILE_LENGTH_ORIG']
            X_MIN = f[k1].attrs['X_MIN']  #RANGE
            X_MAX = f[k1].attrs['X_MAX']
            Y_MIN = f[k1].attrs['Y_MIN']  # AZIMUTH
            Y_MAX = f[k1].attrs['Y_MAX']
            dtype = f[k1].attrs['DATATYPE']  
            print Y_MAX
            print X_MAX
        else:
            WIDTH_ORIG = f[k1].attrs['WIDTH'] 
            FILE_LENGTH_ORIG = f[k1].attrs['FILE_LENGTH']
            X_MIN = '0'  #RANGE
            X_MAX =  str(int(WIDTH_ORIG)-1)
            Y_MIN = '0'  # AZIMUTH
            Y_MAX =  str(int(FILE_LENGTH_ORIG)-1)
            dtype = f[k1].attrs['DATATYPE']  
            
    else:
        print 'Unrecognized h5 file type: '+ FILE
        sys.exit(1)
        
    
    #if X_MIN =='0' and Y_MIN =='0':
    #    Lat_IDX1,Lon_IDX1 = RdcCoord2LTCoord(LT, X_MIN, '1')
    #else:
    #    Lat_IDX1,Lon_IDX1 = RdcCoord2LTCoord(LT, X_MIN, Y_MIN)
    #Lat_IDX2,Lon_IDX2 = RdcCoord2LTCoord(LT, X_MIN, Y_MAX)
    #Lat_IDX3,Lon_IDX3 = RdcCoord2LTCoord(LT, X_MAX, Y_MIN)
    #Lat_IDX4,Lon_IDX4 = RdcCoord2LTCoord(LT, X_MAX, Y_MAX)
    
    #Lat_IDX = [int(Lat_IDX1),int(Lat_IDX2),int(Lat_IDX3),int(Lat_IDX4)]
    
    #if (min(Lat_IDX) - 20) > 0:
    #    Lat_IDX_MIN = min(Lat_IDX) - 20   # extend 20 geo-pixels
    #else:
    #    Lat_IDX_MIN = 0
        
    #if (max(Lat_IDX) + 20) < (int(nLineUTM) -1):  
    #    Lat_IDX_MAX = max(Lat_IDX) + 20
    #else:
    #    Lat_IDX_MAX = (int(nLineUTM) -1)
    
    #Lon_IDX = [int(Lon_IDX1),int(Lon_IDX2),int(Lon_IDX3),int(Lon_IDX4)]
    
    #if (min(Lon_IDX) - 20) > 0:
    #    Lon_IDX_MIN = min(Lon_IDX) - 20   # extend 20 geo-pixels
    #else:
    #    Lon_IDX_MIN = 0
        
    #if  (max(Lon_IDX) + 20) < (int(nWidthUTM) -1):  # extend 20 geo-pixels
    #    Lon_IDX_MAX = max(Lon_IDX) + 20
    #else:
    #    Lon_IDX_MAX = (int(nWidthUTM) -1)
    
    
    print 'Subset in radar coordinates: '
    print 'minimum range  :  ' + X_MIN + '    maximum range  : ' + X_MAX
    print 'minimum azimuth:  ' + Y_MIN + '    maximum azimuth: ' + Y_MAX
    print ''
    
    #print 'Subset in lookup table coordinates: '
    #print 'minimum geo-line : ' + str(Lat_IDX_MIN) + '    maximum geo-line : ' + str(Lat_IDX_MAX)
    #print 'minimum geo-column: ' + str(Lon_IDX_MIN) + '    maximum geo-column: ' + str(Lon_IDX_MAX)
    #print ''
    
    
##############################   Outfile Definition  ########################################################    
    
    if inps.out:
        GEOFILE = inps.out
    else:
        GEOFILE = 'geo_' + os.path.basename(FILE)
        
    print 'Output geocoded h5 file %s.' % GEOFILE

################################## Geocoding for h5 file ####################################################

    
    f_out = h5py.File(GEOFILE,'w')
    group = f_out.create_group(k1)
    
    
    if k1 in multi_group_hdf5_file:    
        fileNum = len(k2)
        for i in range(len(k2)):
            gg = group.create_group(k2[i])
            data = f[k1][k2[i]].get(k2[i])[()]
            data0 = np.zeros([int(FILE_LENGTH_ORIG),int(WIDTH_ORIG)])
            data0 = np.float32(data0)
            data0[int(Y_MIN):int(Y_MAX)+1,int(X_MIN):int(X_MAX)+1] = data
            data0.byteswap(True)
            data0.tofile(k2[i])
            outFile = 'geo_' + k2[i]
            print_progress(i+1, fileNum, prefix='Geocoding ', suffix=k2[i])
            geocode(k2[i], outFile, LTFile, WIDTH_ORIG, nWidthUTM, nLineUTM)
            data1 = read_data(outFile, dtype, nWidthUTM, nLineUTM)
            #data = data1[int(Lat_IDX_MIN):int(Lat_IDX_MAX)+1,int(Lon_IDX_MIN):int(Lon_IDX_MAX)+1]
            dset  = gg.create_dataset(k2[i], data = data1, compression='gzip')     
      
            atr = f[k1].attrs
            for key,value in atr.iteritems():   gg.attrs[key] = value    
            for key,value in atr_lt.iteritems():   gg.attrs[key] = value          
            #gg.attrs['FILE_LENGTH'] = str(int(Lat_IDX_MAX)-int(Lat_IDX_MIN))
            #gg.attrs['WIDTH'] = str(int(Lon_IDX_MAX)-int(Lon_IDX_MIN))
            #gg.attrs['X_MIN'] = str(Lon_IDX_MIN)   # width -- range / longitude
            #gg.attrs['X_MAX'] = str(Lon_IDX_MAX) 
            #gg.attrs['Y_MIN'] = str(Lat_IDX_MIN)   # line -- azimuth / latitude
            #gg.attrs['Y_MAX'] = str(Lat_IDX_MAX)
            #gg.attrs['WIDTH_ORIG'] = nWidthUTM
            #gg.attrs['FILE_LENGTH_ORIG'] = nLineUTM
        
            #call_str = 'rm ' + k2[i]
            #os.system(call_str)
        
            #call_str = 'rm ' + outFile
            #os.system(call_str)
            
    elif k1 in multi_dataset_hdf5_file:
        gg = group
        atr = f[k1].attrs
        for key,value in atr.iteritems():   gg.attrs[key] = value    
        for key,value in atr_lt.iteritems():   gg.attrs[key] = value
        #gg.attrs['FILE_LENGTH'] = str(int(Lat_IDX_MAX)-int(Lat_IDX_MIN))
        #gg.attrs['WIDTH'] = str(int(Lon_IDX_MAX)-int(Lon_IDX_MIN))
        #gg.attrs['X_MIN'] = str(Lon_IDX_MIN)   # width -- range / longitude
        #gg.attrs['X_MAX'] = str(Lon_IDX_MAX) 
        #gg.attrs['Y_MIN'] = str(Lat_IDX_MIN)   # line -- azimuth / latitude
        #gg.attrs['Y_MAX'] = str(Lat_IDX_MAX)
        #gg.attrs['WIDTH_ORIG'] = nWidthUTM
        #gg.attrs['FILE_LENGTH_ORIG'] = nLineUTM
        fileNum = len(k2)
        for i in range(len(k2)):
            data = f[k1].get(k2[i])[()]
            data0 = np.zeros([int(FILE_LENGTH_ORIG),int(WIDTH_ORIG)])
            data0 = np.float32(data0)
            data0[int(Y_MIN):int(Y_MAX)+1,int(X_MIN):int(X_MAX)+1] = data
            data0.byteswap(True)
            data0.tofile(k2[i])
            outFile = 'geo_' + k2[i]
            print_progress(i+1, fileNum, prefix='Geocoding ', suffix=k2[i])
            geocode(k2[i], outFile, LTFile, WIDTH_ORIG, nWidthUTM, nLineUTM)
            data1 = read_data(outFile, dtype, nWidthUTM, nLineUTM)
            #data = data1[int(Lat_IDX_MIN):int(Lat_IDX_MAX)+1,int(Lon_IDX_MIN):int(Lon_IDX_MAX)+1]
            dset  = gg.create_dataset(k2[i], data = data1, compression='gzip')  
    
            #call_str = 'rm ' + k2[i]
            #os.system(call_str)
        
            #call_str = 'rm ' + outFile
            #os.system(call_str)
            
    elif k1 in single_dataset_hdf5_file:
        gg = group
        
        atr = f[k1].attrs
        for key,value in atr.iteritems():   gg.attrs[key] = value    
        for key,value in atr_lt.iteritems():   gg.attrs[key] = value
        
        #gg.attrs['FILE_LENGTH'] = str(int(Lat_IDX_MAX)-int(Lat_IDX_MIN))
        #gg.attrs['WIDTH'] = str(int(Lon_IDX_MAX)-int(Lon_IDX_MIN))
        #gg.attrs['X_MIN'] = str(Lon_IDX_MIN)   # width -- range / longitude
        #gg.attrs['X_MAX'] = str(Lon_IDX_MAX) 
        #gg.attrs['Y_MIN'] = str(Lat_IDX_MIN)   # line -- azimuth / latitude
        #gg.attrs['Y_MAX'] = str(Lat_IDX_MAX)
        #gg.attrs['WIDTH_ORIG'] = nWidthUTM
        #gg.attrs['FILE_LENGTH_ORIG'] = nLineUTM

        data = f[k1].get(k2[0])[()]
        #print data[1100:1200,400:500]
        data0 = np.zeros([int(FILE_LENGTH_ORIG),int(WIDTH_ORIG)])
        data0= np.float32(data0)
        data0[int(Y_MIN):int(Y_MAX)+1,int(X_MIN):int(X_MAX)+1] = data
        #print data0[1100:1200,400:500]
        data0.byteswap(True)  #big-endian for gamma
        data0.tofile(k2[0])     
        outFile = 'geo_' + k2[0]
#        print_progress(i+1, fileNum, prefix='Geocoding ', suffix=k2[0])
        geocode(k2[0], outFile, LTFile, WIDTH_ORIG, nWidthUTM, nLineUTM)
        data1 = read_data(outFile, dtype, nWidthUTM, nLineUTM)
        #data = data1[int(Lat_IDX_MIN):int(Lat_IDX_MAX)+1,int(Lon_IDX_MIN):int(Lon_IDX_MAX)+1]
        dset  = gg.create_dataset(k2[0], data = data1, compression='gzip')  
    
        #call_str = 'rm ' + k2[0]
        #os.system(call_str)
        
        #call_str = 'rm ' + outFile
        #os.system(call_str)
    
    else:
        print 'Unrecognized h5 file type: '+ FILE
        sys.exit(1)
        
           
    f_out.close()
    f_lt.close()
    f.close()
    
    print ''
    print 'Done.'  
    sys.exit(1)


if __name__ == '__main__':
    main(sys.argv[1:])
