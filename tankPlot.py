#!/usr/bin/env python3

import numpy as np
from matplotlib import rcParams, pyplot as pp

rcParams['figure.figsize'] = [10,7]
default_window_position='+20+80'

import sys
sys.path.append("./pySmithPlot")
import smithplot
from smithplot import SmithAxes
################################################################################
# Operating Enviornment
#####
f0		= 28
bw0		= 6.5 # assumed tuning range (GHz)
bw_plt	= 0.5 # Plotting range (GHz)
fbw		= bw0/f0 # fractional bandwidth

frequency_sweep_steps = 101
gamma_sweep_steps = 11

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

gamma_swp = np.linspace(-gamma,gamma,gamma_sweep_steps);
# compute correction factor for g1 that will produce common gain at f0
g1_swp = np.sqrt( g1*g1 - (gamma_swp*gamma_swp) * c1/l1  )
# and compute how much of a negative gm this requres, and it's relative
# proportion to the gm of the assumed main amplifier gm.
g1_boost = (g1_swp - g1)
g1_ratio = -g1_boost / gm1

c1_swp = c1 * (1 + gamma_swp)

## Report System Descrption
print('  L1 = %.3fpH, C1 = %.3ffF' % (1e3*l1, 1e6*c1))
print('    Rp = %.3f Ohm' % (1/g1))
print('    Max G1 boost %.2fmS (%.1f%% of gm1)' % \
	(1e3*np.max(np.abs(g1_boost)), 100*np.max(g1_ratio)))

def db(volt_tf):
	return 20*np.log10(np.abs(volt_tf))
def ang(volt_tf):
	return 180/np.pi*np.angle(volt_tf)

#y_tank=np.zeros((len(delta),len(gamma_swp)))
h1 = pp.figure()
mgr = pp.get_current_fig_manager()
ax1 = h.add_subplot(2,2,(1,3), projection='smith')
ax3 = h.add_subplot(2,2,2)
ax4 = h.add_subplot(2,2,4)
for itune,gamma_tune in enumerate(gamma_swp):
	c1_tune = c1_swp[itune]
	g1_tune = g1_swp[itune]
	K = np.sqrt(c1/l1)/g1_tune
	y_tank = g1_tune + jw*c1_tune + 1/(jw * l1)
	#print(1/np.mean(np.abs(y_tank)))
	ax1.plot(y_tank, datatype=SmithAxes.Y_PARAMETER, marker="None")
	tf = gm1 / g1_tune * \
		1j*(1+delta) / \
		( 1j*(1+delta) + K*(1 - (1+gamma_tune)*np.power(1+delta,2)) )
	ax3.plot(f,db(tf))
	ax4.plot(f,ang(tf))

################################################################################
ax1.set_title('Tank Impedance')

ax3.set_title('TF Gain')
ax3.set_ylabel('Gain (dB)')
ax4.set_title('TF Phase')
ax3.set_ylabel('Phase (deg)')
for ax_T in [ax3, ax4]:
	ax_T.grid()
	ax_T.set_xlabel('Freq (GHz)')
	ax_T.set_xlim(( np.min(f), np.max(f) ))

h.tight_layout()
mgr.window.geometry(default_window_position)
h.show()
