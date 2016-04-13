#!/usr/bin/env python
## Unsigned polynomial division function
#  August 10 2015 by Kirsten Basinet
#  Parameters:   -divisor: Row vector containing descending polynomial
#                 coefficients
#                -dividend: Row vector containing descending codeword
#                 coefficients
#  Returns:      -quotient: Row vector containing descending quotient
#                 coefficients, or NaN if an error occurred
#                -remainder: Row vector contianing remainder
#  Dependencies: -Requires Numpy
#                 user has the communications systems toolbox.
#  Notes:        -The function may need more debugging for cases where
#                 divisor>dividend, negative numbers are included, and
#                 other possible inputs. Works for CRC applications.
#--------------------------------------------------------------------------
import numpy as np

def polynomialDivision(divisor, dividend):
    #Initialize variables
    quotient = []
    remainder = []
    temp_dividend = []
    dividing = True
    #Convert divisor and dividend to integers
    divisor = [int(x) for x in divisor]
    dividend = [int(x) for x in dividend]

    #Remove leading zeros, return NaN if dividend or divisor are invalid
    try:
        dividend = dividend[np.nonzero(dividend)[0][0]:len(dividend)]
        divisor = divisor[np.nonzero(divisor)[0][0]:len(divisor)]
    except:
        quotient = np.nan
        remainder = np.nan
        dividing = False
    
    #Return NaN if divisor is bigger than dividend
    if len(divisor)>len(dividend):
        quotient = np.nan
        remainder = np.nan
        dividing = False   
    
    #Perform division
    place_count = len(divisor)
    temp_dividend = dividend[0:place_count]
    while dividing:
        if temp_dividend[0] == 1: #Use XOR method of polynomial division
            quotient.extend([1])
            for i in range(len(divisor)):
                temp_dividend[i] = temp_dividend[i]^divisor[i]
        elif temp_dividend[0] == 0:
            quotient.extend([0])
        else: #Non-binary number or NaN
            remainder = np.nan
            quotient = np.nan
            dividing = False #Done
        place_count = place_count+1
        if place_count > len(dividend):
            #Remove leading zeros and set remainder
            try:
                remainder = temp_dividend[np.nonzero(temp_dividend)[0][0]:len(temp_dividend)]
            except:
                remainder = 0
            dividing = False
        else:
            temp_dividend.pop(0)
            temp_dividend.extend([dividend[place_count-1]])
    return remainder, quotient
#Done
