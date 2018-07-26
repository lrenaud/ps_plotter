#!/usr/bin/env python3
import os
import argparse
import numpy as np
import matplotlib
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
args_parser.add_argument('--headless','-q', action='store_true',
	help='Remain neadless even if we aren\'t saving files.')
args = args_parser.parse_args()

################################################################################
if args.raster:
	args.save = True
	fig_ext = 'png'
else:
	fig_ext = 'pdf'

################################################################################
HEADLESS = not 'DISPLAY' in os.environ.keys()
if args.headless: HEADLESS = True	# Override Manually if request
if HEADLESS: matplotlib.use('Agg')

from matplotlib import rcParams, pyplot as pp
from collections import namedtuple
import LPRDefaultPlotting
################################################################################

# Override the defaults for this script
figScaleSize = 1.0 if args.save else 1.6
rcParams['figure.figsize'] = [3.4*figScaleSize,3*figScaleSize]
default_window_position=['+20+80', '+120+80']
################################################################################

search_curves = (
	['2018-05-21',3.19],
	['2018-05-25',3.13]
	)

currentBiasTable = np.load('fromCadence/current_bias.npy')
bias_t_mV = currentBiasTable[0,:]*1e3
bias_t_mA = currentBiasTable[1,:]*1e3

bufferPerformanceTable = np.load('fromCadence/buffer_arrays.npz')
[buffer_bias,buffer_freq,buffer_gain,buffer_phase] = \
	[item[1] for item in bufferPerformanceTable.iteritems()]

for curve in search_curves:
	ind = np.argmin(np.abs(bias_t_mA-curve[1]))
	curve.append(ind)
	curve.append(bias_t_mV[ind]*1e-3)

h=[pp.figure() for x in range(2)]
ax=[hT.subplots(1,1) for hT in h]
ax.append(ax[1].twinx())


ax[0].set_xlabel('Gate Bias (mV)')
ax[0].set_ylabel('Current (mA)')
ax[0].plot(bias_t_mV, bias_t_mA)

ax[1].set_xlabel('Frequency (GHz)')
ax[1].set_ylabel('Gain (dB)')
ax[2].set_ylabel('Phase (deg)')
inds = [curve[2] for curve in search_curves]
bw = 28
freq_synthetic = np.linspace(-bw/2,bw/2,201)+28
print(search_curves)
for ind in inds:
	GP=np.polyfit(buffer_freq, buffer_gain[:,ind], 2)
	PP=np.polyfit(buffer_freq, buffer_phase[:,ind], 2)
	#print(" %.2fe-3 x^2 + %.2fe-3 x + %.2fe-3 " % tuple(1e3*P))
	print(ind)
	print(GP)
	print(PP)
	ax[1].plot(freq_synthetic, np.polyval(GP,freq_synthetic))
	ax[2].plot(freq_synthetic, np.polyval(PP,freq_synthetic))

ax[1].plot(buffer_freq, buffer_gain[:,inds])
ax[2].plot(buffer_freq, buffer_phase[:,inds])

[aT.grid() for aT in ax]
[hT.tight_layout() for hT in h]
[hT.show() for hT in h]
