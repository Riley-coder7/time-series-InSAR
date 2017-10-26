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
import glob
import time
import argparse
import getopt

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

def read_subset(STR):
    
    SUB  = []
    W1 = STR.split('/')[0]
    W2 = STR.split('/')[1]
    
    L1 = STR.split('/')[2]
    L2 = STR.split('/')[3]    
    
    SUB.append(int(W1))
    SUB.append(int(W2))
    SUB.append(int(L1))
    SUB.append(int(L2))
    
    return SUB

def get_remove_number(STR):
    N = len(STR.split(','))
    Num = []
    
    for i in range(N):
        AA = STR.split(',')[i]
        if ':' not in AA:
            Num.append(int(int(AA)-1))
        else:
            x1 = int(AA.split(':')[0])
            x2 = int(AA.split(':')[1])
            rr = range(x2+1)[x1:]
            for k in rr:
                Num.append(k-1)
    return Num            


#########################################################################

INTRODUCTION = '''
#############################################################################
   Copy Right(c): 2017, Yunmeng Cao   @PyMIS v1.0   
   
   Unwrap multi-temporal interferograms based on GAMMA software.
   
'''

EXAMPLE = '''
    Usage:
            unwrap_mtsar.py MTINF.h5 MTCOR.h5 -m maskh5 -s subset -o output
            unwrap_mtsar.py MTINF.h5 MTCOR.h5 -t threshold -s subset -o output
            unwrap_mtsar.py MTINF.h5 MTCOR.h5 -t threshold -r remove_number -s subset -o output
            
    Examples:
            unwrap_mtsar.py MTINF.h5 MTCOR.h5 -t 0.3 -s 100/500/300/400
            unwrap_mtsar.py MTINF.h5 MTCOR.h5 -t 0.3 -s 100/500/300/400 -o unwarp_subset.h5
            unwrap_mtsar.py MTINF.h5 MTCOR.h5 -m mask.h5 -r "1,2,4:5,8" -s 100/500/300/400 -o unwarp_subset.h5

##############################################################################
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Unwrap multi-temporal interferograms.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('file',help='MTINF H5 file that will be unwrapped.')
    parser.add_argument('cor',help='MTCOR H5 file that will be used as weight and used to generate mask file.')
    parser.add_argument('-t',dest = 'threshold', help='Unwrap threshold. [default: 0.3]')
    parser.add_argument('-s',dest = 'subset', help='subset original region, range1/range2/azimuth1/azimuth2.')
    parser.add_argument('-r',dest = 'remove_number', help='interferogram numbers that will be removed during the processing.')
    parser.add_argument('-m',dest = 'mask', help='H5 mask file.')
    parser.add_argument('-o',dest = 'out', help='output file name that will be generated.')
    
    inps = parser.parse_args()
    
    if not inps.file or not inps.cor:
        parser.print_usage()
        sys.exit(os.path.basename(sys.argv[0])+': error: wrapped images and weighted images should be provided.')

    return inps

################################################################################

def main(argv):
     
    total = time.time()
    inps = cmdLineParse()
    
    MTFILE = inps.file
    MTCOR = inps.cor
    
    if inps.threshold: unwThreshold = inps.threshold
    else: unwThreshold = '0.3'
    
    print unwThreshold
     
        
    if inps.out: OUTH5 = inps.out
    else: OUTH5 = 'unwrap_mis.h5'
     
    if inps.subset: 
        STR= inps.subset
        SUB = read_subset(STR)
    
    if inps.remove_number: NUM =get_remove_number(inps.remove_number)
    else: NUM = []
    
    f_inf = h5py.File(MTFILE,'r')
    f_cor = h5py.File(MTCOR,'r')       

    f_unw = h5py.File(OUTH5,'w')
    group = f_unw.create_group('interferograms')
    
    TS_INF = f_inf[f_inf.keys()[0]].keys()
    TS_COR = f_cor[f_cor.keys()[0]].keys()
    
    atr = f_inf[f_inf.keys()[0]][TS_INF[0]].attrs
    projectName = atr['PROJECT']
    nWidth = atr['WIDTH']
    nLine = atr['FILE_LENGTH']
    nWidth0 = nWidth
    nLine0 = nLine
    DATATYPE = atr['DATATYPE']
    sign = DATATYPE[0]
    dtype_unw = sign + 'f4'
    
    fileNum = len(TS_INF) 
    KK = range(fileNum)
    NN = []    
    for i in KK:
        if i not in NUM:
            NN.append(i)
        
    
    if inps.mask:
        MMASK = inps.mask
        f_mask = h5py.File(MMASK,'r') 
        MASK = f_mask[f_mask.keys()[0]].keys()[0]
        datamask =  f_mask[f_mask.keys()[0]].get(MASK)[()]
        datamask = np.float32(datamask)
        datamask[datamask>float(unwThreshold)]=1
        datamask[datamask<float(unwThreshold)]=0
    else:
        datamask = np.ones([int(nLine),int(nWidth)],dtype='float32')
    print datamask.shape
    
    if inps.subset:
        nWidth = str(int(SUB[1]-SUB[0]+1))
        nLine = str(int(SUB[3]-SUB[2]+1))
        datamask = datamask[SUB[2]:(SUB[3]+1),SUB[0]:(SUB[1]+1)]
    
    for i in NN:

        INF = TS_INF[i]
        COR = TS_COR[i]
        MASKNAME = COR.replace('cor','bmp')
        UNWNAME = COR.replace('cor','unw')
        
        print_progress(i+1, fileNum, prefix='Unwrapping ', suffix=os.path.basename(INF))
        atr = f_inf[f_inf.keys()[0]][TS_INF[i]].attrs
        
        gg = group.create_group(UNWNAME)
        for key,value in atr.iteritems():   gg.attrs[key] = value
            
        data_inf = f_inf[f_inf.keys()[0]][INF].get(INF)[()]
        
        data_cor = f_cor[f_cor.keys()[0]][COR].get(COR)[()]
        #datacor.byteswap(True)
        
        
        
        if inps.subset:
            data_cor = data_cor[SUB[2]:(SUB[3]+1),SUB[0]:(SUB[1]+1)]
            data_inf = data_inf[SUB[2]:(SUB[3]+1),SUB[0]:(SUB[1]+1)]
            
        data_cor = data_cor * datamask  
        data_cor.byteswap(True)
        data_inf.tofile(INF)
        data_cor.tofile(COR)
        
        AMP = '/scratch/projects/insarlab/yxc773/PichinchaSMT51TsxD/PYMIS/111008_5rlks.amp' 
        #  no amp image, the threshold value does not work!!  why?
        
        #if inps.mask:
        #    call_str = 'rascc_mask ' + COR + ' ' + AMP  + ' '  + nWidth + ' - - - - - 0.1 - - - - - - ' + MASKNAME + '> tt'
        #    os.system(call_str)
        #else:
        call_str = 'rascc_mask ' + COR + ' ' + AMP  + ' '  + nWidth + ' - - - - - ' + unwThreshold + ' - - - - - - ' + MASKNAME + '> tt'
        os.system(call_str)

        call_str = 'mcf ' + INF + ' ' + COR + ' ' + MASKNAME + ' ' + UNWNAME + ' ' + nWidth + ' 0 - - - - 1 1 > tt'
        os.system(call_str)
        data = read_data(UNWNAME, dtype_unw, nWidth, nLine)
        dset  = gg.create_dataset(UNWNAME, data = data, compression='gzip')
        gg.attrs['DATATYPE'] = dtype_unw
        gg.attrs['WIDTH'] =nWidth
        gg.attrs['FILE_LENGTH'] =nLine
        
        if inps.subset:
            gg.attrs['WIDTH_ORG'] =nWidth0
            gg.attrs['FILE_LENGTH_ORG'] =nLine0
            gg.attrs['X_MIN'] = str(SUB[0])
            gg.attrs['X_MAX'] = str(SUB[1])
            gg.attrs['Y_MIN'] = str(SUB[2])
            gg.attrs['Y_MAX'] = str(SUB[3])
        
        
        
    f_inf.close()
    f_cor.close()
    f_unw.close()
    call_str = 'rm *diff*'
    os.system(call_str)
    
    print ''
    print 'Done.\nUnwrapping subset interferograms spend ' + str(time.time()-total) +' secs'    
    sys.exit(1)

##############################################################################
if __name__ == '__main__':
    main(sys.argv[1:])
