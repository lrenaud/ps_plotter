#!/usr/bin/env python3
import numpy as np

################################################################################
# Operating Enviornment
#####
f0		= 28
bw0		= 6.5 # assumed tuning range (GHz)
bw_plt	= 2 # Plotting range (GHz)
fbw		= bw0/f0 # fractional bandwidth

frequency_sweep_steps = 101
gamma_sweep_steps = 15

gamma = 1 - np.power(f0 / (f0 + bw0/2),2)
gamma_limit_ratio = 0.99 # how close gamma can get to theoretical extreme

# Configuration Of Hardware
#####
q1_L	= 10
q1_C	= 10
l1		= 100e-3 # nH
gm1		= 25e-3 # S

# Compute frequency sweep
#####
w0		= f0*2*np.pi
fbw_plt	= bw_plt/f0
delta	= np.linspace(-fbw_plt/2,fbw_plt/2,frequency_sweep_steps)
w		= w0*(1+delta)
f		= f0*(1+delta)
jw		= 1j*w

##################
# Compute system 
#####
c1		= 1/(w0*w0*l1)
g1_L	= 1 / (q1_L*w0*l1)
g1_C	= w0 * c1 / q1_C
g1		= g1_L + g1_C

# Verify gamma is valid
#####
gamma_max = g1 * np.sqrt(l1/c1)
if gamma > (gamma_limit_ratio * gamma_max):
	print("==> WARN: Gamma to large, reset to %.3f (was %.3f) <==" % \
		(gamma_max_cap*gamma_max, gamma))
	gamma = gamma_max_cap*gamma_max

