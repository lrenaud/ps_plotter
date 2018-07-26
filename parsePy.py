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
import skrf as rf
from scipy.io import loadmat
from collections import namedtuple
import LPRDefaultPlotting
################################################################################

# Override the defaults for this script
figScaleSize = 1.0 if args.save else 1.6
rcParams['figure.figsize'] = [3.4*figScaleSize,3*figScaleSize]
default_window_position=['+20+80', '+120+80']

################################################################################

SRC_DATA_NAMES	= [\
	'Data_2018-05-15-clean',
	'Data_2018-05-16-clean',
	'Data_2018-05-21-clean',
	'Data_2018-05-25-clean']
SRC_DATA_INDEX	= 2
SRC_DATA_NAME	= SRC_DATA_NAMES[SRC_DATA_INDEX]
SRC_DATA_LOC	= '/media/ramdisk/' + SRC_DATA_NAME + '/';
SRC_DATA_SUMMARY = 'dat_clean/' + SRC_DATA_NAME + '_sum.json';

FILE_PAT = '%s-trunk2.s2p';
figdir = 'figures-measured'

class MeasurementConfig(namedtuple('config', ['r','c','inv','bias'])):
	__slots__ = ()
	@property
	def fn_str(self):
		return "C%02d_R%1d_I%1d_B%0.4f" % (self.c, self.r, self.inv, self.bias)
Measurement = namedtuple('measurement', ['cfg','gain','phase','f','s21'])

def dB20(x):
	return 20*np.log10(np.abs(x))
def ang_deg(x):
	return 180/np.pi*np.angle(x)
def ang(x):
	return np.angle(x)

# 2018-05-21
PolyGain=np.array( [ 4.08875413e-03, -5.13017311e-01,  2.54047949e+01])
PolyPhase=np.array([-1.29541398e-03,  6.74431785e-01, -1.80127388e+02])
# 2018-05-25
#PolyGain=np.array( [ 4.06488853e-03, -5.11527396e-01,  2.53053550e+01])
#PolyPhase=np.array([-1.62202706e-03,  6.94343608e-01, -1.80381551e+02])

source_directory='fromMat/Data_2018-05-21-clean_mat/'
source_data_list=['fromMat/Data_2018-05-21-clean_mat/S02bB_C+01dB_M0.mat']
for filename in os.listdir(source_directory):
	filename=source_directory+filename
	group_filename_string = filename.split('/')[-1][:-4]
	src = loadmat(filename, struct_as_record=False)

	collectedData=[]
	for sample in src['data'][0]:
		tmp = [sample.__getattribute__(key)[0,0] for key in ['r', 'c', 'inv', 'bias_dp_set']]
		pt = MeasurementConfig(r=tmp[0], c=tmp[1], inv=tmp[2], bias=np.float(tmp[3]))
		s2p_file = rf.Network(SRC_DATA_LOC + (FILE_PAT % pt.fn_str) )

		freq = np.squeeze(s2p_file.f*1e-9)
		buffer_gain = np.polyval(PolyGain,freq)
		buffer_phase = np.polyval(PolyPhase,freq)
		buffer_phase = buffer_phase - np.mean(buffer_phase)
		sdat = np.squeeze(s2p_file.s21.s)
		index = np.squeeze(np.argwhere(freq==28))
		collectedData.append(Measurement(pt,
			dB20(sdat[index])-buffer_gain[index],
			ang_deg(sdat[index])-buffer_phase[index],
			freq, sdat))

	h=pp.figure()
	ax=h.add_subplot(1,1,1, projection='polar')
	print("---------------------||------------------------------")
	print("  _C  R  I  _Bias_   ||       Gain          Phase  ")
	print("---------------------||------------------------------")
	for imeas in collectedData:
		ax.plot(ang(imeas.s21)-buffer_phase, dB20(imeas.s21)-buffer_gain)
		print("  %2d  %d  %d  %.4f   ||   %+7.1f dB   %+9.2f deg" % \
			(imeas.cfg.c, imeas.cfg.r, imeas.cfg.inv, imeas.cfg.bias, \
				imeas.gain, imeas.phase))
	print("---------------------||------------------------------")
	ax.set_ylim(-20,-6)
	ax.set_title('Measured Performance')

	old_pos = ax.title.get_position()
	ax.title.set_position((old_pos[0], 1.1))

	h.tight_layout()
	if args.save:
		h.savefig('%s/%s.%s' % (figdir,
			'PolarGain-%s' % group_filename_string, fig_ext))
	if HEADLESS:
		pp.close()
	else:
		h.show()
		break
