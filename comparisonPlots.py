#!/usr/bin/env python3

import numpy as np
import matplotlib
import argparse
import os
import code
import pdb
import copy
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
	help='Remain neadless even if we aren\'t saving fileS1.')
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
rcParams['figure.figsize'] = [3.4*figScaleSize,2*figScaleSize]
default_window_position=['+20+80', '+120+80']

################################################################################
# Operating Enviornment (i.e. circuit parameters)
import TankGlobals
from FreqClass import FreqClass
from tankComputers import *
freq_pts = 501

S1=TankGlobals.ampSystem()
S1.bw_plt=2
f=FreqClass(freq_pts, S1.f0, S1.bw_plt)

S1.q1_L = 15
S2 = copy.deepcopy(S1)
gain_variation = -2 # dB



################################################################################
# We want a smooth transition out to alpha. So For now assume a squares
# weighting out to the maximum alpha at the edgeS1.
# This gain variation function is the default function baked into the method.
#gain_variation = 0 # dB
S2.alpha_min = dB2Vlt(gain_variation)

################################################################################
# Extract the computed tank conductanec, and the transfer functionS1.
(_, tf1) = S1.compute_block(f)
(_, tf_ref1) = S1.compute_ref(f)
(_, tf2) = S2.compute_block(f)
(_, tf_ref2) = S2.compute_ref(f)

# To produce full 360 dgree plots, double the two transfer functions by
# considering inversion.
# double to describe with perfect inversion stage
tf1 = np.column_stack((tf1,-tf1))
tf2 = np.column_stack((tf2,-tf2))

# compute the relative transfer function thus giving us flat phase, and
# flat (ideally) gain response if our system perfectly matches the reference
tf_r1 = tf1 / (tf_ref1*np.ones((tf1.shape[1],1))).T
tf_r2 = tf2 / (tf_ref2*np.ones((tf2.shape[1],1))).T

# We will also do a direct angle comparison
tf_r_ang_ideal1 = wrap_rads(np.concatenate((-S1.phase_swp, -np.pi - S1.phase_swp)))
tf_r_ang_ideal2 = wrap_rads(np.concatenate((-S2.phase_swp, -np.pi - S2.phase_swp)))
tf_r_ang1 = np.angle(tf_r1)
tf_r_ang2 = np.angle(tf_r2)
#tf_r_ang_rms1 = np.sqrt(np.mean(np.power(tf_r_ang1-tf_r_ang_ideal1,2),0))
#tf_r_ang_rms2 = np.sqrt(np.mean(np.power(tf_r_ang2-tf_r_ang_ideal2,2),0))

tf_r_ang_rms1_f=delta_rms(tf_r_ang1, 2*np.pi/16)
tf_r_ang_rms2_f=delta_rms(tf_r_ang2, 2*np.pi/16)

################################################################################
# Compute RMS phase error relative to ideal reference across plotting bandwidth
(bw_ang1, rms_ang_swp1)=rms_v_bw(tf_r_ang1-tf_r_ang_ideal1, S1.bw_plt)
(bw_mag1, rms_gain_swp1)=rms_v_bw(tf_r1, S1.bw_plt)
(bw_ang2, rms_ang_swp2)=rms_v_bw(tf_r_ang2-tf_r_ang_ideal2, S2.bw_plt)
(bw_mag2, rms_gain_swp2)=rms_v_bw(tf_r2, S2.bw_plt)

################################################################################
################################################################################
################################################################################
#mgr = pp.get_current_fig_manager()

################################################################################
if 3 in plot_list:
	h3 = [pp.figure() for x in range(2)]
	ax3a = h3[0].subplots(1,2)
	ax3b = h3[1].subplots(1,2)
	ax3 = np.concatenate((ax3a, ax3b))

	ax3[0].plot(bw_mag1,dB20(rms_gain_swp1))
	ax3[1].plot(bw_mag2,dB20(rms_gain_swp2))
	ax3[2].plot(bw_ang1,rms_ang_swp1*180/np.pi)
	ax3[3].plot(bw_ang2,rms_ang_swp2*180/np.pi)

	h3[0].suptitle('RMS Gain Error')
	h3[1].suptitle('RMS Phase Error')
	#ax3[0].set_title('RMS Gain Error')
	ax3[0].set_ylabel('Gain Error (dB)')
	#ax3[2].set_title('RMS Phase Error')
	ax3[2].set_ylabel('Phase Error (deg)')

	#ax3[1].set_title('RMS Gain Error w/GV')
	ax3[1].set_ylabel('Gain Error (dB)')
	#ax3[3].set_title('RMS Phase Error w/GV')
	ax3[3].set_ylabel('Phase Error (deg)')

	# Match Axes
	limSetGain = [axT.get_ylim() for axT in ax3[:2]]
	limSetPhase = [axT.get_ylim() for axT in ax3[2:]]
	limSetGain = (np.min(limSetGain), np.max(limSetGain))
	limSetPhase = (np.min(limSetPhase), np.max(limSetPhase))

	for axT in ax3[:2]:
		axT.set_ylim(limSetGain)
	for axT in ax3[2:]:
		axT.set_ylim(limSetPhase)
	for axT in ax3[[1,3]]:
		LPRDefaultPlotting.axAnnotateCorner(axT,
			'%g dB gain variation' % (gain_variation), corner=2, ratio=0.04)
		axT.yaxis.tick_right()
		axT.yaxis.label_position='right'
		axT.yaxis.labelpad = axT.yaxis.labelpad + axT.yaxis.label.get_size()

	for axT in ax3[[0,2]]:
		LPRDefaultPlotting.axAnnotateCorner(axT,
			'%g dB gain variation' % (0), corner=2, ratio=0.04)

	for axT in ax3:
		axT.grid()
		axT.set_xlim((0,S1.bw_plt))
		axT.set_xlabel('Bandwidth (GHz)')

	[hT.tight_layout() for hT in h3]
	[hT.tight_layout() for hT in h3]
	# Make XY mirror positions
	for i in [0,2]:
		p0 = ax3[i].get_position()
		p1 = ax3[i+1].get_position()
		p1.x1 = 1 - p0.x0
		p1.x0 = 1 - p0.x1
		ax3[i+1].set_position(p1)

	for axT in ax3:
		p=axT.get_position()
		p.y1=0.88
		axT.set_position(p)

	if args.save:
		h3[0].savefig('%s/%s.%s' % (figdir, 'dual_030-RMSGain', fig_ext))
		h3[1].savefig('%s/%s.%s' % (figdir, 'dual_031-RMSPhase', fig_ext))
	if HEADLESS:
		pp.close()
	else:
		#mgr.window.geometry(default_window_position[0])
		[hT.show() for hT in h3]

if 4 in plot_list:
	h4 = [pp.figure() for x in range(2)]
	ax4a = h4[0].subplots(1,2)
	ax4b = h4[1].subplots(1,2)
	ax4 = np.concatenate((ax4a, ax4b))

	#ax4[0].plot(bw_mag1,dB20(rms_gain_swp1))
	#ax4[1].plot(bw_mag2,dB20(rms_gain_swp2))
	ax4[2].plot(f.hz,tf_r_ang_rms1_f*180/np.pi)
	ax4[3].plot(f.hz,tf_r_ang_rms2_f*180/np.pi)

	h4[0].suptitle('RMS Gain Error')
	h4[1].suptitle('RMS Phase Error')
	#ax4[0].set_title('RMS Gain Error')
	ax4[0].set_ylabel('Gain Error (dB)')
	#ax4[2].set_title('RMS Phase Error')
	ax4[2].set_ylabel('Phase Error (deg)')

	#ax4[1].set_title('RMS Gain Error w/GV')
	ax4[1].set_ylabel('Gain Error (dB)')
	#ax4[3].set_title('RMS Phase Error w/GV')
	ax4[3].set_ylabel('Phase Error (deg)')

	# Match Axes
	limSetGain = [axT.get_ylim() for axT in ax4[:2]]
	limSetPhase = [axT.get_ylim() for axT in ax4[2:]]
	limSetGain = (np.min(limSetGain), np.max(limSetGain))
	limSetPhase = (np.min(limSetPhase), np.max(limSetPhase))

	for axT in ax4[:2]:
		axT.set_ylim(limSetGain)
	for axT in ax4[2:]:
		axT.set_ylim(limSetPhase)
	for axT in ax4[[1,3]]:
		LPRDefaultPlotting.axAnnotateCorner(axT,
			'%g dB gain variation' % (gain_variation), corner=2, ratio=0.04)
		axT.yaxis.tick_right()
		axT.yaxis.label_position='right'
		axT.yaxis.labelpad = axT.yaxis.labelpad + axT.yaxis.label.get_size()

	for axT in ax4[[0,2]]:
		LPRDefaultPlotting.axAnnotateCorner(axT,
			'%g dB gain variation' % (0), corner=2, ratio=0.04)

	for axT in ax4:
		axT.grid()
		axT.set_xlim((np.min(f.hz),np.max(f.hz)))
		axT.set_xlabel('Frequency (GHz)')

	[hT.tight_layout() for hT in h4]
	[hT.tight_layout() for hT in h4]
	# Make XY mirror positions
	for i in [0,2]:
		p0 = ax4[i].get_position()
		p1 = ax4[i+1].get_position()
		p1.x1 = 1 - p0.x0
		p1.x0 = 1 - p0.x1
		ax4[i+1].set_position(p1)

	for axT in ax4:
		p=axT.get_position()
		p.y1=0.88
		axT.set_position(p)

	if args.save:
		h4[0].savefig('%s/%s.%s' % (figdir, 'dual_040-RMSGain', fig_ext))
		h4[1].savefig('%s/%s.%s' % (figdir, 'dual_041-RMSPhase', fig_ext))
	if HEADLESS:
		pp.close()
	else:
		#mgr.window.geometry(default_window_position[0])
		[hT.show() for hT in h4]
