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

def setLimitsTicks(ax, data, steps):
	targs = np.array([1, 2, 4, 5, 10, 20, 30, 50, 60, 100, 250, 1000])
	lo = np.min(data)
	hi = np.max(data)
	rg = hi-lo
	step_size = rg / steps
	step_size = np.select(targs >= step_size, targs)
	lo = np.floor(lo / step_size)*step_size
	hi = np.ceil(hi / step_size)*step_size
	marks = np.arange(0,steps+1)*step_size + lo
	ax.set_ylim((lo,hi))
	ax.set_yticks(marks)

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

def delta_rms(signal, reference_delta, wrap_point=2*np.pi):
	"""compute the rms difference between various states and a reference"""
	# First compute the matrix difference including folding
	signal_delta = np.column_stack((
		signal[:,1:]-signal[:,:-1],
		signal[:,0]-signal[:,-1]
		))
	signal_delta = np.where(signal_delta>wrap_point/2, \
		signal_delta-wrap_point, signal_delta)
	signal_delta = np.where(signal_delta<-wrap_point/2, \
		signal_delta+wrap_point, signal_delta)
	signal_error = np.abs(signal_delta)-reference_delta

	signal_rms = np.sqrt(np.mean(np.power(signal_error,2),1))

	return signal_rms

def gain_error(signal, ref_freq_ind):
	"""compute the gain variation relative to a mean computed at ref_freq_ind"""
	# First compute the matrix difference including folding
	inband_gain = np.mean(signal[ref_freq_ind,:])
	signal_off = signal-inband_gain
	range = np.max(signal_off,1)-np.min(signal_off,1)

	return range

def rms(signal, ref_freq_ind=None):
	"""compute raw RMS"""
	if ref_freq_ind == None:
		offset_signal = signal-np.transpose(\
			np.ones((signal.shape[1],1))*np.mean(signal,1)\
			)
	else:
		offset_signal = signal-np.mean(signal[ref_freq_ind,:])
	return np.sqrt(np.mean(np.power(offset_signal,2),1))
