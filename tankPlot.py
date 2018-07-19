#!/usr/bin/env python3

import numpy as np

from matplotlib import rcParams, pyplot as pp
import LPRDefaultPlotting

import sys
sys.path.append("./pySmithPlot")
import smithplot
from smithplot import SmithAxes

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
	
def atan(x):
	return 180/np.pi*np.arctan(x)


################################################################################
# Override the defaults for this script
rcParams['figure.figsize'] = [10,7]
default_window_position='+20+80'

################################################################################
# Operating Enviornment (i.e. circuit parameters)
from TankGlobals import *

################################################################################
# Now generate the sweep of resonance tuning (gamma, and capacitance)

# Linear based gamma spacing
#gamma_swp = np.linspace(-gamma,gamma,gamma_sweep_steps)

# Linear PHASE gamma spacing
# First compute the most extreme phase given the extreme gamma
g1_limit = np.sqrt( g1*g1 - (gamma*gamma) * c1/l1  )
K_limit = np.sqrt(c1/l1)*1/g1_limit
phase_limit = np.mod(np.pi/2 - np.arctan( -1/K_limit * 1/gamma ),np.pi) - np.pi

# This gives us our equal phase spacing points
phase_swp = np.linspace(-1,1,gamma_sweep_steps) * phase_limit
# Then use this to compute the gamma steps to produce arbitrary phase given
# our perfect gain constraint.
gamma_swp = np.sign(phase_swp)/np.sqrt(np.power(np.tan(np.pi/2 - phase_swp),2)+1) * g1 / np.sqrt(c1/l1)

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

y_tank = np.zeros((len(gamma_swp),len(f)), dtype=complex)
tf = np.zeros((len(gamma_swp),len(f)), dtype=complex)
for itune,gamma_tune in enumerate(gamma_swp):
	c1_tune = c1_swp[itune]
	g1_tune = g1_swp[itune]
	K = np.sqrt(c1/l1)/g1_tune
	y_tank_tmp = g1_tune + jw*c1_tune + 1/(jw * l1)
	y_tank[itune,:] = y_tank_tmp
	tf_tmp = gm1 / g1_tune * \
		1j*(1+delta) / \
		( 1j*(1+delta) + K*(1 - (1+gamma_tune)*np.power(1+delta,2)) )
	tf[itune,:] = tf_tmp

tf = tf.T
tf_d = tf[:,1:]-tf[:,:-1]
tf_r = tf / (tf[:,int(tf.shape[1]/2)]*np.ones((tf.shape[1],1))).T
y_tank = y_tank.T
################################################################################

h1 = pp.figure()
h2 = pp.figure(figsize=(5,7))
mgr = pp.get_current_fig_manager()
################################################################################
ax1 = h1.add_subplot(2,2,1, projection='smith')
ax2 = h1.add_subplot(2,2,3, projection='polar')
ax3 = h1.add_subplot(2,2,2)
ax4 = h1.add_subplot(2,2,4)

ax1.plot(y_tank, datatype=SmithAxes.Y_PARAMETER, marker="None")
ax2.plot(np.angle(tf), dB20(tf))
ax3.plot(f,dB20(tf))
ax4.plot(f,ang(tf))

################################################################################
ax8 = h2.add_subplot(2,1,1)
ax9 = h2.add_subplot(2,1,2)
ax8.plot(f,dB20(tf_r))
ax9.plot(f,ang_unwrap(tf_r.T).T)

ax1.set_title('Tank Impedance')
ax2.set_title('Transfer Function')

ax3.set_title('TF Gain')
ax3.set_ylabel('Gain (dB)')
ax4.set_title('TF Phase')
ax4.set_ylabel('Phase (deg)')
ax8.set_title('TF Relative Gain')
ax8.set_ylabel('Relative Gain (dB)')
ax9.set_title('TF Relative Phase')
ax9.set_ylabel('Relative Phase (deg)')
for ax_T in [ax3, ax4, ax8, ax9]:
	ax_T.grid()
	ax_T.set_xlabel('Freq (GHz)')
	ax_T.set_xlim(( np.min(f), np.max(f) ))


################################################################################
h1.tight_layout()
h2.tight_layout()
mgr.window.geometry(default_window_position)
h1.show()
mgr.window.geometry(default_window_position)
h2.show()
