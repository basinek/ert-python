#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
## Decoder for ERT standard. v1.0: August 9, 2015
#  A.G. Klein and N. Conroy and K. Basinet
#  Description:  -Decodes ERT gas meter data from .bin file and displays
#                 meter ID, meter type, physical tamper flag, encoder tamper flag,
#                 consumption value, and the elapsed time since the last loop.
#                 Code is based on similary ERT decoder for MATLAB written by 
#                 A.G. Klein and N. Conroy and K. Basinet
#  Dependencies: -Requires Numpy and custom function polynomialDivision
#  ------------------------------------------------------------------------
import numpy as np
from polynomialDivision import polynomialDivision

#"Macro" for converting binary number as digits in list to decimal integer
def bin2dec(bin_list):
	bin_list = [int(b) for b in bin_list]
	return int(''.join(str(c) for c in bin_list),2)

#Parameters and constants
JMP = 30                            # Number of samples to jump over each iteration 
DataRate = 16384                    # Data rate for determining symbol period
SMPRT = 2392064                     # RTL-SDR Sample Rate
BLOCKSIZE = 18688                   # RTL-SDR Samples per frame
SP = np.int16(SMPRT/DataRate)       # Nominal symbol period (in # samples)
BCH_POLY = [1,0,1,1,0,1,1,1,1,0,1,1,0,0,0,1,1] # BCH generator polynomial coefficients from ERT standard
PREAMBLE = [1,1,1,1,1,0,0,1,0,1,0,1,0,0,1,1,0,0,0,0,0]  #From ERT standard, includes sync bit

#Load file into list
with open('rtlamr_log2015-12-29.bin', 'rb') as fid:
	dat = np.fromfile(fid,np.int8)
fid.close()
dat = dat-127
s = dat[1:(len(dat)-1):2]+1j*dat[2:(len(dat)-1):2]

#Preallocate buffer space
zbuff = np.zeros(BLOCKSIZE)
softbits = np.zeros(96)
bits = np.zeros(96)
cnt = 0 #Decoded message counter
block_index = 0 #Data block counter
while block_index < len(s)-BLOCKSIZE+JMP:
	i=0 # Counter for sample feeding
	zbuff = s[block_index:block_index+(BLOCKSIZE-1)] #Grab block of samples from file, store them in buffer
	buff = np.int32(np.real(zbuff))**2+np.int32(np.imag(zbuff))**2 #Cheap absolute value of buffer
	while i < BLOCKSIZE-(96*SP):
		cu = np.cumsum(buff[i:(i+96*SP)])
		softbits = (2*cu[(SP/2)+1:(95*SP)+(SP/2)+1:SP])-cu[1:(95*SP)+1:SP]-cu[SP+1:(95*SP)+SP+1:SP];
		for n in range(len(softbits)): #List with '1' where corresponding index in softbits is positive
			if softbits[n] > 0:
				bits[n] = 1
			else:
				bits[n] = 0
		#Check if preamble is correct and parse data
		if np.array_equal(bits[0:len(PREAMBLE)],PREAMBLE):
			#BCH processing
			dc = np.concatenate([np.zeros(180),bits[21:96]])
			if polynomialDivision(BCH_POLY,bits[21:96])[0] == 0:
			    #BCH passed
			    i = i+(96*SP)-JMP
			    cnt = cnt+1
			    #Separate BCH decoded blocks
			    dc_id = np.concatenate([dc[180:182],dc[215:239]])
			    SCM_ID = np.concatenate([bits[21:23],bits[55:79]])
			    dc_phy_tmp = dc[183:185]
			    dc_ert_type = dc[185:189]
			    dc_enc_tmp = dc[189:191]
			    dc_consump = dc[191:215]
			    #Convert to decimal
			    dc_id = bin2dec(dc_id)
			    dc_phy_tmp = bin2dec(dc_phy_tmp)
			    dc_ert_type = bin2dec(dc_ert_type)
			    dc_enc_tmp = bin2dec(dc_enc_tmp)
			    dc_consump = bin2dec(dc_consump)
			    #Print decoded output
			    print("Decoded Meter ID: %u" %dc_id)
			    print("Decoded Meter Type: %u" %dc_ert_type)
			    print("Decoded Physical Tamper: %u" %dc_phy_tmp)
			    print("Decoded Encoder Tamper: %u" %dc_enc_tmp)
			    print("Decoded Consumption: %u \n" %dc_consump)
                        else:
                            #Do nothing
		i = i+JMP   #Increment sample feeding counter
	block_index = block_index+(JMP*96) #Increment block counter
print(cnt)
