#!/usr/bin/env python3
import numpy as np

################################################################################
# Define my helper functions.
def dB20(volt_tf):
	"""Describe signal gain of a transfer function in dB (i.e. 20log(x))"""
	return 20*np.log10(np.abs(volt_tf))
def ang(volt_tf):
	"""Describe phase of a transfer function in degrees. Not unwrapped."""
	return 180/np.pi*np.angle(volt_tf)
def ang_unwrap(volt_tf):
	"""Describe phase of a transfer function in degrees. With unwrapping."""
	return 180/np.pi*np.unwrap(np.angle(volt_tf))
def dB10(pwr_tf):
	"""Describe power gain of a transfer function in dB (i.e. 10log(x))"""
	return 10*np.log10(np.abs(pwr_tf))
	
def dB2Vlt(dB20_value):
	return np.power(10,dB20_value/20)
	
def wrap_rads(angles):
	return np.mod(angles+np.pi,2*np.pi)-np.pi
def atand(x):
	return 180/np.pi*np.arctan(x)

def rms_v_bw(err_sig, bandwidth_scale=1):
	"""compute the rms vs bandwidth assuming a fixed center frequency"""
	# First compute the error power
	err_pwr = np.power(np.abs(err_sig),2)
	steps = len(err_pwr)
	isodd = True if steps%2 != 0 else False

	# We want to generate the midpoint to the left, and midpoint to the right
	# as two distinct sets.
	pt_rhs_start = int(np.floor(steps/2))
	pt_lhs_stop = int(np.ceil(steps/2))

	folded = err_pwr[pt_rhs_start:] + np.flip(err_pwr[:pt_lhs_stop],0)
	# Now, we MIGHT have double counted the mid point
	# if the length is odd, correct for that
	if isodd: folded[0]*=0.5

	# Now we need an array that describes the number of points used to get here.
	# this one turns out to be pretty easy.
	frac_step = np.arange(int(not isodd),steps,2)/(steps-1)
	ind = 2*np.arange(0,frac_step.shape[0])+1+int(not isodd)

	# Now actually compute the RMS values. First do the running sum
	rms = np.sqrt(np.cumsum(folded,0) / (ind*np.ones((folded.shape[1],1))).T )
	return (frac_step*bandwidth_scale, rms)

