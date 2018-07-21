#!/usr/bin/env python3

import numpy as np

from matplotlib import rcParams, pyplot as pp
import LPRDefaultPlotting

import sys
sys.path.append("./pySmithPlot")
import smithplot
from smithplot import SmithAxes

plot_list = [4]

################################################################################
# Override the defaults for this script
rcParams['figure.figsize'] = [3.4,2.2]
default_window_position=['+20+80', '+120+80']

################################################################################
# Operating Enviornment (i.e. circuit parameters)
import TankGlobals
from FreqClass import FreqClass
from tankComputers import *

S=TankGlobals.ampSystem()
B=TankGlobals.bufferSystem()
f=FreqClass(501, S.f0, S.bw_plt)

################################################################################
# We want a smooth transition out to alpha. So For now assume a squares
# weighting out to the maximum alpha at the edges.
# This gain variation function is the default function baked into the method.
gain_variation = 0 # dB
S.alpha_min = dB2Vlt(gain_variation)

# and compute how much of a negative gm this requres, and it's relative
# proportion to the gm of the assumed main amplifier gm.
g1_boost = (S.g1_swp - S.g1)
g1_ratio = -g1_boost / S.gm1

print('    Max G1 boost %.2fmS (%.1f%% of gm1)' % \
	(1e3*np.max(np.abs(g1_boost)), 100*np.max(g1_ratio)))

################################################################################
# Extract the computed tank conductanec, and the transfer functions.
(y_tank, tf) = S.compute_block(f)
(_, tf_ref) = S.compute_ref(f)

# To produce full 360 dgree plots, double the two transfer functions by
# considering inversion.
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

(y_buf, tf_buf) = B.compute_ref(f)

################################################################################
################################################################################
################################################################################
mgr = pp.get_current_fig_manager()

################################################################################
if 6 in plot_list:
	h6 = pp.figure()
	mgr = pp.get_current_fig_manager()
	ax6 = [h6.subplots(1,1)]
	ax6.append(ax6[0].twinx())

	axT=ax6[0]
	axT.plot(f.hz,dB20(tf_buf))
	axT.set_ylabel('Gain (dB)')
	axT.set_title('Buffer Response')
	setLimitsTicks(axT, dB20(tf_buf), 6)
	axT=ax6[1]
	axT.plot(f.hz,ang_unwrap(tf_buf))
	axT.set_ylabel('Phase (deg)')
	setLimitsTicks(axT, ang_unwrap(tf_buf), 6)


	for i,axT in enumerate(ax6):
		if i==0: axT.grid()
		axT.set_xlim(f.hz_range)
		axT.set_xlabel('Frequency (GHz)')
		c_color = LPRDefaultPlotting.COLOR_CYCLE_LIST[i]
		axT.lines[0].set_color(c_color)
		axT.yaxis.label.set_color(c_color)
		axT.tick_params('y', colors=c_color)
	h6.tight_layout()
	mgr.window.geometry(default_window_position[0])
	h6.show()

################################################################################
if 1 in plot_list:
	h1 = [pp.figure() for x in range(2)]
	ax1 = [hT.add_subplot(1,1,1) for hT in h1]
	ax1[0].plot(f.hz,dB20(tf))
	ax1[1].plot(f.hz,ang_unwrap(tf))

	ax1[0].set_title('TF Gain')
	ax1[0].set_ylabel('Gain (dB)')
	ax1[1].set_title('TF Phase')
	ax1[1].set_ylabel('Phase (deg)')
	
	for axT in ax1:
		axT.grid()
		axT.set_xlabel('Freq (GHz)')
		axT.set_xlim(f.hz_range)
	
	[hT.tight_layout() for hT in h1]
	mgr.window.geometry(default_window_position[0])
	[hT.show() for hT in h1]

if 4 in plot_list:
	h4 = [pp.figure(figsize=(3.4,3.4)) for x in range(2)]
	ax4 = []
	ax4.append(h4[0].add_subplot(1,1,1, projection='smith'))
	ax4.append(h4[1].add_subplot(1,1,1, projection='polar'))

	ax4[0].plot(y_tank, datatype=SmithAxes.Y_PARAMETER, marker="None")
	ax4[1].plot(np.angle(tf), dB20(tf))

	ax4[0].set_title('Tank Impedance')
	ax4[1].set_title('Transfer Function')

	old_pos = ax4[1].title.get_position()
	ax4[1].title.set_position((old_pos[0], 1.1))
	h4[1].tight_layout()
	#[hT.tight_layout() for hT in h4]
	mgr.window.geometry(default_window_position[0])
	[hT.show() for hT in h4]

################################################################################
if 2 in plot_list:
	h2 = [pp.figure() for x in range(2)]
	
	ax2 = [hT.add_subplot(1,1,1) for hT in h2]
	ax2[0].plot(f.hz,dB20(tf_r))
	setLimitsTicks(ax2[0], dB20(tf_r), 6)
	ax2[1].plot(f.hz,ang_unwrap(tf_r.T).T)
	setLimitsTicks(ax2[1], ang_unwrap(tf_r.T), 6)
	
	ax2[0].set_title('Relative Gain')
	ax2[0].set_ylabel('Gain (dB)')
	ax2[1].set_title('Relative Phase')
	ax2[1].set_ylabel('Phase (deg)')

	for axT in ax2:
		axT.grid()
		axT.set_xlabel('Freq (GHz)')
		axT.set_xlim(f.hz_range)
	[hT.tight_layout() for hT in h2]
	mgr.window.geometry(default_window_position[1])
	[hT.show() for hT in h2]

################################################################################
if 3 in plot_list:
	h3 = [pp.figure() for x in range(2)]
	
	ax3 = [hT.add_subplot(1,1,1) for hT in h3]
	ax3[0].plot(bw_mag,dB20(rms_gain_swp))
	ax3[1].plot(bw_ang,rms_ang_swp*180/np.pi)
	
	ax3[0].set_title('RMS Gain Error')
	ax3[0].set_ylabel('RMS Gain Error (dB)')
	ax3[1].set_title('RMS Phase Error')
	ax3[1].set_ylabel('RMS Phase Error (deg)')
	for axT in ax3:
		axT.grid()
		axT.set_xlim((0,S.bw_plt))
		axT.set_xlabel('Bandwidth (GHz)')

	[hT.tight_layout() for hT in h3]
	[hT.show() for hT in h3]

