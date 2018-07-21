#!/usr/bin/env python3

import numpy as np

from matplotlib import rcParams, pyplot as pp
import LPRDefaultPlotting

import sys
sys.path.append("./pySmithPlot")
import smithplot
from smithplot import SmithAxes

################################################################################
# Override the defaults for this script
rcParams['figure.figsize'] = [10,7]
default_window_position=['+20+80', '+120+80']

################################################################################
# Operating Enviornment (i.e. circuit parameters)
import TankGlobals
from FreqClass import FreqClass
from tankComputers import *

S=TankGlobals.ampSystem()
f=FreqClass(501, S.f0, S.bw_plt)

################################################################################
# We want a smooth transition out to alpha. So For now assume a squares
# weighting out to the maximum alpha at the edges.
gain_variation = -8*0	# dB
S.alpha_min = dB2Vlt(gain_variation)

# compute correction factor for g1 that will produce common gain at f0
# this is defined as the class default
g1_swp = S.g1_swp
# and compute how much of a negative gm this requres, and it's relative
# proportion to the gm of the assumed main amplifier gm.
g1_boost = (g1_swp - S.g1)
g1_ratio = -g1_boost / S.gm1

print('    Max G1 boost %.2fmS (%.1f%% of gm1)' % \
	(1e3*np.max(np.abs(g1_boost)), 100*np.max(g1_ratio)))

################################################################################
# Generate a reference implementation
(y_tank, tf) = S.compute_block(f)
(_, tf_ref) = S.compute_ref(f)
# double to describe with perfect inversion stage
tf = np.column_stack((tf,-tf))

# compute the relative transfer function thus giving us flat phase, and
# flat (ideally) gain response if our system perfectly matches the reference
tf_r = tf / (tf_ref*np.ones((tf.shape[1],1))).T

# We will also do a direct angle comparison
tf_r_ang_ideal = wrap_rads(np.concatenate((-S.phase_swp, -np.pi - S.phase_swp)))
tf_r_ang = np.angle(tf_r)
tf_r_ang_rms = np.sqrt(np.mean(np.power(tf_r_ang-tf_r_ang_ideal,2),0))

y_tank = y_tank.T
################################################################################
# Compute RMS phase error relative to ideal reference across plotting bandwidth
(bw_ang, rms_ang_swp)=rms_v_bw(tf_r_ang-tf_r_ang_ideal, S.bw_plt)
(bw_mag, rms_gain_swp)=rms_v_bw(tf_r, S.bw_plt)

################################################################################

h1 = pp.figure()
h2 = pp.figure(figsize=(5,7))
h3 = pp.figure(figsize=(5,7))
mgr = pp.get_current_fig_manager()
################################################################################
ax1 = h1.add_subplot(2,2,1, projection='smith')
ax2 = h1.add_subplot(2,2,3, projection='polar')
ax3 = h1.add_subplot(2,2,2)
ax4 = h1.add_subplot(2,2,4)

ax1.plot(y_tank, datatype=SmithAxes.Y_PARAMETER, marker="None")
ax2.plot(np.angle(tf), dB20(tf))
ax3.plot(f.hz,dB20(tf))
ax4.plot(f.hz,ang_unwrap(tf))

################################################################################
ax6 = h2.add_subplot(2,1,1)
ax7 = h2.add_subplot(2,1,2)
ax6.plot(f.hz,dB20(tf_r))
ax7.plot(f.hz,ang_unwrap(tf_r.T).T)

ax8 = h3.add_subplot(2,1,1)
ax9 = h3.add_subplot(2,1,2)
ax8.plot(bw_mag,dB20(rms_gain_swp))
ax9.plot(bw_ang,rms_ang_swp*180/np.pi)

ax1.set_title('Tank Impedance')
ax2.set_title('Transfer Function')

ax3.set_title('TF Gain')
ax3.set_ylabel('Gain (dB)')
ax4.set_title('TF Phase')
ax4.set_ylabel('Phase (deg)')
ax6.set_title('TF Relative Gain')
ax6.set_ylabel('Relative Gain (dB)')
ax7.set_title('TF Relative Phase')
ax7.set_ylabel('Relative Phase (deg)')
for ax_T in [ax3, ax4, ax6, ax7]:
	ax_T.grid()
	ax_T.set_xlabel('Freq (GHz)')
	ax_T.set_xlim(f.hz_range)

ax8.set_title('RMS Gain Error')
ax8.set_ylabel('RMS Gain Error (dB)')
ax9.set_title('RMS Phase Error')
ax9.set_ylabel('RMS Phase Error (deg)')
for ax_T in [ax8, ax9]:
	ax_T.grid()
	ax_T.set_xlim((0,S.bw_plt))
	ax_T.set_xlabel('Bandwidth (GHz)')


################################################################################
h1.tight_layout()
h2.tight_layout()
h3.tight_layout()
mgr.window.geometry(default_window_position[0])
h1.show()
mgr.window.geometry(default_window_position[1])
h2.show()
h3.show()
