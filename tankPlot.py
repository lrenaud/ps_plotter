#!/usr/bin/env python3

import numpy as np
import matplotlib
import argparse
import os
import code
import pdb
################################################################################
args_parser = argparse.ArgumentParser()
args_parser.add_argument('-n', type=int, default=1,
	help='plot testing number')
args_parser.add_argument('--save','-s', action='store_true',
	help='save to files')
args_parser.add_argument('--raster','-r', action='store_true',
	help='save as raster')
args_parser.add_argument('--debug','-d', action='store_true',
	help='hold for debugging')
args_parser.add_argument('--subplot', action='store_true',
	help='use subplots when available')
args_parser.add_argument('--headless','-q', action='store_true',
	help='Remain neadless even if we aren\'t saving files.')
args = args_parser.parse_args()

#exit()

HEADLESS = not 'DISPLAY' in os.environ.keys()
if args.headless: HEADLESS = True	# Override Manually if request
if HEADLESS: matplotlib.use('Agg')

################################################################################
from matplotlib import rcParams, pyplot as pp
import LPRDefaultPlotting

figdir = LPRDefaultPlotting.figures_directory
if args.save: os.makedirs(figdir, exist_ok=True)

import sys

sys.path.append("./pySmithPlot")
import smithplot
from smithplot import SmithAxes
SmithAxes.update_scParams(axes_normalize=False,
 	grid_minor_fancy_threshold=50, axes_radius=0.5)

plot_list = [args.n]

if args.raster:
	args.save = True
	fig_ext = 'png'
else:
	fig_ext = 'pdf'

################################################################################
# Override the defaults for this script
figScaleSize = 1.0 if args.save else 1.6
if args.subplot:
	rcParams['figure.figsize'] = [3.4*figScaleSize,4*figScaleSize]
else:
	rcParams['figure.figsize'] = [3.4*figScaleSize,2.25*figScaleSize]
default_window_position=['+20+80', '+120+80']

################################################################################
# Operating Enviornment (i.e. circuit parameters)
import TankGlobals
from FreqClass import FreqClass
from tankComputers import *
freq_pts = 501

S=TankGlobals.ampSystem()
B=TankGlobals.bufferSystem()

S.q1_L = 15
if plot_list[0] in [11, 12, 13, 14]:
	gain_variation = +4 # dB
else:
	gain_variation = 0 # dB

if plot_list[0] in [14, 4, 5]:
	S.bw_plt = 0.5
	B.bw_plt = S.bw_plt
	freq_pts = 51
if plot_list[0] == 5:
	S.set_g1_swp(TankGlobals.g1_map_flat)
	S.set_gamma_swp(TankGlobals.gamma_map_flat)

f=FreqClass(freq_pts, S.f0, S.bw_plt)

################################################################################
# We want a smooth transition out to alpha. So For now assume a squares
# weighting out to the maximum alpha at the edges.
# This gain variation function is the default function baked into the method.
#gain_variation = 0 # dB
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
#mgr = pp.get_current_fig_manager()

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
	if args.save:
			h6.savefig('%s/%s.%s' % (figdir, 'NA-06.0', fig_ext))
	if HEADLESS:
		pp.close()
	else:
		#mgr.window.geometry(default_window_position[0])
		h6.show()

################################################################################
if 1 in plot_list or 11 in plot_list:
	if not args.subplot:
		h1 = [pp.figure() for x in range(2)]
		ax1 = [hT.add_subplot(1,1,1) for hT in h1]
	else:
		h1 = [pp.figure() for x in range(1)]
		ax1 = h1[0].subplots(2,1)

	ax1[0].plot(f.hz,dB20(tf))
	ax1[1].plot(f.hz,ang_unwrap(tf))

	ax1[0].set_title('Stage Gain Response')
	ax1[0].set_ylabel('Gain (dB)')
	ax1[1].set_title('Stage Phase Response')
	ax1[1].set_ylabel('Phase (deg)')

	for axT in ax1:
		axT.grid()
		axT.set_xlabel('Freq (GHz)')
		axT.set_xlim(f.hz_range)

	[hT.tight_layout() for hT in h1]
	if 11 in plot_list:
		for hT in h1:
			LPRDefaultPlotting.figAnnotateCorner(hT,
				'%g dB gain variation' % (gain_variation))

	if args.save:
		if 11 in plot_list:
			if args.subplot:
				h1[0].savefig('%s/%s.%s' % (figdir,
					'01d-ideal-AbsGainPhase-wgv', fig_ext))
			else:
				h1[0].savefig('%s/%s.%s' % (figdir,
					'010-AbsGain-wgv', fig_ext))
				h1[1].savefig('%s/%s.%s' % (figdir,
					'011-AbsPhase-wgv', fig_ext))
		else:
			if args.subplot:
				h1[0].savefig('%s/%s.%s' % (figdir,
					'01d-ideal-AbsGainPhase', fig_ext))
			else:
				h1[0].savefig('%s/%s.%s' % (figdir,
					'010-AbsGain', fig_ext))
				h1[1].savefig('%s/%s.%s' % (figdir,
					'011-AbsPhase', fig_ext))
	if HEADLESS:
		pp.close()
	else:
		#mgr.window.geometry(default_window_position[0])
		[hT.show() for hT in h1]

if 4 in plot_list or 14 in plot_list:
	h4 = [pp.figure(figsize=(3.4,3)) for x in range(2)]
	ax4 = []
	ax4.append(h4[0].add_subplot(1,1,1, projection='smith'))
	ax4.append(h4[1].add_subplot(1,1,1, projection='polar'))

	ax4[0].plot(y_tank, datatype=SmithAxes.Y_PARAMETER, marker="None")
	ax4[1].plot(np.angle(tf), dB20(tf))

	ax4[0].set_title('Tank Impedance')
	ax4[1].set_title('Transfer Function')

	# Adjust placement of smith plot
	old_pos = ax4[0].title.get_position()
	ax4[0].title.set_position((old_pos[0], 1.06))
	p = ax4[0].get_position()
	p.set_points([[0, 0.07],[1, 0.86]])
	ax4[0].set_position(p)

	old_pos = ax4[1].title.get_position()
	ax4[1].title.set_position((old_pos[0], 1.1))
	h4[1].tight_layout()

	if 14 in plot_list:
		for hT in h4:
			LPRDefaultPlotting.figAnnotateCorner(hT,
				'%g dB gain variation' % (gain_variation))
	#[hT.tight_layout() for hT in h4]
	if args.save:
		if 14 in plot_list:
			h4[0].savefig('%s/%s.%s' % (figdir,
				'040-ideal-smith_tank_impedance-wgv', fig_ext))
			h4[1].savefig('%s/%s.%s' % (figdir,
				'041-ideal-polar_gain_plot-wgv', fig_ext))
		else:
			h4[0].savefig('%s/%s.%s' % (figdir,
				'040-ideal-smith_tank_impedance', fig_ext))
			h4[1].savefig('%s/%s.%s' % (figdir,
				'041-ideal-polar_gain_plot', fig_ext))
	if HEADLESS:
		pp.close()
	else:
		#mgr.window.geometry(default_window_position[0])
		[hT.show() for hT in h4]

if 5 in plot_list:
	h5 = [pp.figure(figsize=(3.4,3.4)) for x in range(2)]
	ax5 = []
	ax5.append(h5[0].add_subplot(1,1,1, projection='smith'))
	ax5.append(h5[1].add_subplot(1,1,1, projection='polar'))

	ax5[0].plot(y_tank, datatype=SmithAxes.Y_PARAMETER, marker="None")
	ax5[1].plot(np.angle(tf), dB20(tf))

	ax5[0].set_title('Tank Impedance')
	ax5[1].set_title('Transfer Function')

	old_pos = ax5[1].title.get_position()
	ax5[1].title.set_position((old_pos[0], 1.1))
	h5[1].tight_layout()
	#[hT.tight_layout() for hT in h5]
	if args.save:
		h5[0].savefig('%s/%s.%s' % (figdir,
			'050-ideal-flat_g1-smith_tank_impedance', fig_ext))
		h5[1].savefig('%s/%s.%s' % (figdir,
			'050-ideal-flat_g1-polar_gain_plot', fig_ext))
	if HEADLESS:
		pp.close()
	else:
		#mgr.window.geometry(default_window_position[0])
		[hT.show() for hT in h5]

################################################################################
if 2 in plot_list or 12 in plot_list:
	if not args.subplot:
		h2 = [pp.figure() for x in range(2)]
		ax2 = [hT.add_subplot(1,1,1) for hT in h2]
	else:
		h2 = [pp.figure() for x in range(1)]
		ax2 = h2[0].subplots(2,1)

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
	if 12 in plot_list:
		for hT in h2:
			LPRDefaultPlotting.figAnnotateCorner(hT,
				'%g dB gain variation' % (gain_variation))

	if args.save:
		if 12 in plot_list:
			if not args.subplot:
				h2[0].savefig('%s/%s.%s' % (figdir,
					'020-TF_RelativeGainPhase-wgv', fig_ext))
				h2[1].savefig('%s/%s.%s' % (figdir,
					'021-TF_RelativePhase-wgv', fig_ext))
			else:
				h2[0].savefig('%s/%s.%s' % (figdir,
					'02d-TF_RelativeGain-gv', fig_ext))
		else:
			if not args.subplot:
				h2[0].savefig('%s/%s.%s' % (figdir,
					'020-TF_RelativeGainPhase', fig_ext))
				h2[1].savefig('%s/%s.%s' % (figdir,
					'021-TF_RelativePhase', fig_ext))
			else:
				h2[0].savefig('%s/%s.%s' % (figdir,
					'02d-TF_RelativeGain', fig_ext))
	if HEADLESS:
		pp.close()
	else:
		#mgr.window.geometry(default_window_position[0])
		[hT.show() for hT in h2]

################################################################################
if 3 in plot_list or 13 in plot_list:
	if not args.subplot:
		h3 = [pp.figure() for x in range(2)]
		ax3 = [hT.add_subplot(1,1,1) for hT in h3]
	else:
		h3 = [pp.figure() for x in range(1)]
		ax3 = h3[0].subplots(2,1)

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
	[hT.tight_layout() for hT in h3]
	if 13 in plot_list:
		for hT in h3:
			LPRDefaultPlotting.figAnnotateCorner(hT,
				'%g dB gain variation' % (gain_variation))

	if args.save:
		if 13 in plot_list:
			if not args.subplot:
				h3[0].savefig('%s/%s.%s' % (figdir, '030-RMSGain-wgv', fig_ext))
				h3[1].savefig('%s/%s.%s' % (figdir, '031-RMSPhase-wgv', fig_ext))
			else:
				h3[0].savefig('%s/%s.%s' % (figdir, '03d-RMSBoth-wgv', fig_ext))
		else:
			if not args.subplot:
				h3[0].savefig('%s/%s.%s' % (figdir, '030-RMSGain', fig_ext))
				h3[1].savefig('%s/%s.%s' % (figdir, '031-RMSPhase', fig_ext))
			else:
				h3[0].savefig('%s/%s.%s' % (figdir, '03d-RMSBoth', fig_ext))
	if HEADLESS:
		pp.close()
	else:
		#mgr.window.geometry(default_window_position[0])
		[hT.show() for hT in h3]

if args.debug:
	print("")
	print("#"*80)
	print("# Finished execution.")
	print("# Debugging Mode active.")
	print("# Falling back to an interactive prompt.")
	print("#"*80)
	code.interact(local=dict(globals(), **locals()))
