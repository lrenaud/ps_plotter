#!/usr/bin/env python3
import os
import argparse
import numpy as np
import matplotlib
################################################################################
args_parser = argparse.ArgumentParser()
args_parser.add_argument('--save','-s', action='store_true',
	help='save to files')
args_parser.add_argument('--raster','-r', action='store_true',
	help='save as raster')
args_parser.add_argument('--debug','-d', action='store_true',
	help='hold for debugging')
args_parser.add_argument('--polar','-p', action='store_true',
	help='do polar plotting (wide bandwidth)')
args_parser.add_argument('--headless','-q', action='store_true',
	help='Remain neadless even if we aren\'t saving files.')
args_parser.add_argument('-n', type=int, default=4,
	help='plot testing number')
args_parser.add_argument('-c', type=int, default=16,
	help='number of phase states [16,32,64]')
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
from tankComputers import *
import re
import json
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
SRC_DATA_INDEX	= args.n-1
SRC_DATA_NAME	= SRC_DATA_NAMES[SRC_DATA_INDEX]
#SRC_DATA_DATESTR = '-'.join(SRC_DATA_NAME.split('_')[1].split('-')[:-1])
SRC_DATA_LOC	= '/media/ramdisk/' + SRC_DATA_NAME + '/';
SRC_DATA_SUMMARY = '/home/luke/Dropbox/Grad School/1801_PS/' \
	'2018-05_Testing/results_plot/dat_clean/' + SRC_DATA_NAME + '_sum.json';

if args.polar:
	FILE_PAT = '%s-trunk2.s2p';
else:
	FILE_PAT = '%s-trunk.s2p';
figdir = 'figures-measured'
if args.c != 16:
	figdir=figdir+('-%d' % args.c)

class MeasurementConfig(namedtuple('config', ['r','c','inv','bias'])):
	__slots__ = ()
	@property
	def fn_str(self):
		return "C%02d_R%1d_I%1d_B%0.4f" % (self.c, self.r, self.inv, self.bias)
Measurement = namedtuple('measurement', ['cfg', 'pwr','gain','phase','f','s21', 'slope'])

plottingBandwidthMax = 2.01
plottingBandwidthFreq = 28+np.array([-1,1])*0.5*plottingBandwidthMax
slopeBandwidthMax = 1
slopeBandwidthFreq = 28+np.array([-1,1])*0.5*slopeBandwidthMax

def dB20(x):
	return 20*np.log10(np.abs(x))
def ang_deg(x):
	return 180/np.pi*np.angle(x)
def ang(x):
	return np.angle(x)

BDE=namedtuple('BufferDeEmbed',['mstr','PolyGain','PolyPhase','PhiFix','test'])
BDE_list=[]

# 2018-05-15
BDE_list.append(BDE(
	'2018-05-15',
	np.array([ 4.06488853e-03, -5.11527396e-01,  2.53053550e+01]),
	np.array([-1.62202706e-03,  6.94343608e-01, -1.80381551e+02]),
	-60,
	'S02bB_C+01dB_M0'
))
# 2018-05-16
BDE_list.append(BDE(
	'2018-05-16',
	np.array([ 4.08875413e-03, -5.13017311e-01,  2.54047949e+01]),
	np.array([-1.29541398e-03,  6.74431785e-01, -1.80127388e+02]),
	-60,
	'S02bB_C+00dB_M0'
))
# 2018-05-21
#PolyGain=np.array( [ 4.08875413e-03, -5.13017311e-01,  2.54047949e+01])
#PolyPhase=np.array([-1.29541398e-03,  6.74431785e-01, -1.80127388e+02])
BDE_list.append(BDE(
	'2018-05-21',
	np.array([ 4.08875413e-03, -5.13017311e-01,  2.54047949e+01]),
	np.array([-1.29541398e-03,  6.74431785e-01, -1.80127388e+02]),
	-60,
	'S02bB_C+00dB_M0'
))
# 2018-05-25
#PolyGain=np.array( [ 4.06488853e-03, -5.11527396e-01,  2.53053550e+01])
#PolyPhase=np.array([-1.62202706e-03,  6.94343608e-01, -1.80381551e+02])
BDE_list.append(BDE(
	'2018-05-25',
	np.array([ 4.06488853e-03, -5.11527396e-01,  2.53053550e+01]),
	np.array([-1.62202706e-03,  6.94343608e-01, -1.80381551e+02]),
	-70,
	'S02bB_C+00dB_M0'
))

source_directory='fromMat/figures-%d/%s_mat/' % (args.c, SRC_DATA_NAME)
for BDEx in BDE_list:
	if re.search(BDEx.mstr, source_directory) != None:
		PolyGain=BDEx.PolyGain
		PolyPhase=BDEx.PolyPhase
		PhaseFixedRotationFactor=BDEx.PhiFix
		StopTestString=BDEx.test
		FamStr=BDEx.mstr
		break


################################################################################
################################################################################
################################################################################
# FIXME ########################################################################
################################################################################
################################################################################
################################################################################
PolyGain_balun=np.array([0, 0, -7])
PolyPhase_balun=np.array([0, 0, 0])
################################################################################
################################################################################
################################################################################
################################################################################

if args.c == 64:
	StopTestString='S05bB_C+05dB_M0_-64'
elif args.c == 32:
	StopTestString='S03bB_C+00dB_M0_-32'

with open(SRC_DATA_SUMMARY, 'r') as h_sumDat:
	sumDat = json.load(h_sumDat)

def fetchSumDat_pwr(cfg):
	global sumDat
	mR = np.array(sumDat['r']) == cfg.r
	mC = np.array(sumDat['c']) == cfg.c
	mI = np.array(sumDat['inv']) == cfg.inv
	mB = np.abs(np.array(sumDat['bias_dp_set'])-cfg.bias) < 0.0005
	ind = np.squeeze(np.where(np.all((mR,mC,mI,mB),0)))
	if ind.size == 0:
		print("ERROR EVERYTHING IS BROKEN! AND i'M TIRED")
		return -1
	else:
		return sumDat['ivdd'][ind]*sumDat['vdd'][ind]

def sumTuple_avgMinMax(data_list):
	existing_data = []
	for datum in data_list:
		existing_data.extend([np.mean(datum), np.min(datum), np.max(datum)])
	return tuple(existing_data)

combined_rms=np.array([])
for filename in os.listdir(source_directory):
	filename=source_directory+filename
	group_filename_string = filename.split('/')[-1][:-4]
	src = loadmat(filename, struct_as_record=False)

	if not HEADLESS and group_filename_string != StopTestString:
		# skip until we hit some aribitrary targets
		continue

	collectedData=[]
	for sample in src['data'][0]:
		tmp = [sample.__getattribute__(key)[0,0] for key in ['r', 'c', 'inv', 'bias_dp_set']]
		pt = MeasurementConfig(r=tmp[0], c=tmp[1], inv=tmp[2], bias=np.float(tmp[3]))
		s2p_file = rf.Network(SRC_DATA_LOC + (FILE_PAT % pt.fn_str) )

		freq = np.squeeze(s2p_file.f*1e-9)
		inds_keep = np.where(np.all((freq >= plottingBandwidthFreq[0],
			freq <= plottingBandwidthFreq[1]),0))

		sdat_raw = np.squeeze(s2p_file.s21.s)
		freq = freq[inds_keep]
		sdat_raw = sdat_raw[inds_keep]

		buffer_gain = np.polyval(PolyGain,freq)
		buffer_phase = np.polyval(PolyPhase,freq)
		buffer_phase = buffer_phase - np.mean(buffer_phase) + \
			PhaseFixedRotationFactor*np.pi/180
		buffer_sdat = np.power(10,buffer_gain/20)*np.exp(1j*buffer_phase)
		
		balun_gain = np.polyval(PolyGain_balun,freq)
		balun_phase = np.polyval(PolyPhase_balun,freq)
		balun_phase = balun_phase - np.mean(balun_phase)
		balun_sdat = np.power(10,balun_gain/20)*np.exp(1j*balun_phase)

		sdat = sdat_raw/buffer_sdat/balun_sdat

		slope_valid_inds = np.where(np.all((freq >= slopeBandwidthFreq[0],
			freq <= slopeBandwidthFreq[1]),0))
		sub_angles = np.unwrap(np.angle(sdat[slope_valid_inds]))*180/np.pi
		sub_freq = freq[slope_valid_inds]-np.mean(freq[slope_valid_inds])
		slope = np.polyfit(sub_freq,sub_angles-np.mean(sub_angles),1)[0]
		index_f0 = np.squeeze(np.argwhere(freq==28))
		collectedData.append(Measurement(cfg=pt, pwr=fetchSumDat_pwr(pt),
			gain=dB20(sdat[index_f0]),
			phase=ang_deg(sdat[index_f0]),
			f=freq, s21=sdat, slope=slope))

	# Find the indicies close to 0 and 180 as my reference curves
	phis = np.array([s.phase for s in collectedData])
	best_slopes = np.argsort(np.abs(np.mod(phis+90,180)-90))[0:6]
	slope_list = np.array([s.slope for s in collectedData])
	slope_avg = np.mean(slope_list[best_slopes])

	ref_index = np.argmin(np.abs(phis))
	unwrapped_ref_phase = 180/np.pi*np.unwrap(ang(collectedData[ref_index].s21))

	if args.polar:
		h=pp.figure()
		ax=h.add_subplot(1,1,1, projection='polar')
	else:
		h=pp.figure(figsize=(3.4*figScaleSize, 3.6*figScaleSize))
		ax=h.subplots(2,1)
		ax = []
		GRIDSPEC_SIZE=7
		GRIDSPEC_LEN_B=4
		GRIDSPEC_LEN_A = GRIDSPEC_SIZE-GRIDSPEC_LEN_B
		ax.append(pp.subplot2grid((GRIDSPEC_SIZE,1),(0,0), rowspan=GRIDSPEC_LEN_A))
		ax.append(pp.subplot2grid((GRIDSPEC_SIZE,1),(GRIDSPEC_LEN_A,0), rowspan=GRIDSPEC_LEN_B))

		h2=pp.figure(figsize=(3.4*figScaleSize, 2.3*figScaleSize))
		ax = np.append(ax, h2.subplots(1,1))
		ax = np.append(ax, ax[1].twinx())
		ax = np.append(ax, ax[2].twinx())
		ax = np.append(ax, ax[0].twinx())
	summary_msg = \
		"/---------------------\/----------------------------------------\\\n"\
		"|  _C  R  I  _Bias_   ||       Gain          Phase       Power  |\n"\
		"|---------------------||----------------------------------------|\n"
	all_sdat = np.column_stack([imeas.s21 for imeas in collectedData])
	ang_rms = delta_rms(np.angle(all_sdat), 2*np.pi/args.c)*180/np.pi
	gain_pm = gain_error(dB20(all_sdat), index_f0)
	gain_rms = rms(dB20(all_sdat), index_f0)
	for imeas in collectedData:
		if args.polar:
			#ax.plot(ang(imeas.s21)-buffer_phase, dB20(imeas.s21)-buffer_gain)
			ax.plot(ang(imeas.s21), dB20(imeas.s21))
		else:
			ax[0].plot(imeas.f, dB20(imeas.s21))
			unwrapped_phase = 180/np.pi*np.unwrap(ang(imeas.s21))
			#ax[1].plot(imeas.f, unwrapped_phase)
			relative_phase_curve = unwrapped_phase-unwrapped_ref_phase
			if np.any(relative_phase_curve < 0):
				relative_phase_curve += 360
			#relative_phase_curve -= 180-22.5/2
			ax[1].plot(imeas.f, relative_phase_curve)
			#slope_relative = (imeas.f-28)*slope_avg
			#ax[2].plot(imeas.f, unwrapped_phase-slope_relative)
			ax[2].plot(imeas.f, relative_phase_curve)
		pwr_overage = int(2*(imeas.pwr*1e3 - 10))
		pwr_string = (int(pwr_overage/2)*"=") + (np.mod(pwr_overage,2)*">")
		summary_msg += "|  %2d  %d  %d  %.4f   || "\
			"  %+7.1f dB   %+9.2f deg   %4.1f mW |%s\n" % \
			(imeas.cfg.c, imeas.cfg.r, imeas.cfg.inv, imeas.cfg.bias, \
				imeas.gain, imeas.phase, imeas.pwr*1e3, pwr_string)
	summary_msg += \
	 	"\_____________________/\________________________________________/\n"
	pwr_list=np.array([imeas.pwr*1e3 for imeas in collectedData])
	gain_list=np.array([imeas.gain for imeas in collectedData])

	summary_msg += \
	 	"/                                                               \\\n" \
	 	"|===>    Power: % 7.1f mW (% 7.1f mW -  % 7.1f mW)           |\n" \
	 	"|===>     Gain: %+7.1f dB (%+7.1f dB -  %+7.1f dB)           | \n" \
	 	"|===>      RMS: %6.1f deg (%6.1f deg -  %6.1f deg)           | \n" \
	 	"\_______________________________________________________________/" % \
		(sumTuple_avgMinMax([pwr_list, gain_list, ang_rms]))
	print(group_filename_string, sumTuple_avgMinMax([ang_rms]))
	if args.polar:
		ax.set_ylim(LPRDefaultPlotting.POLAR_YLIM_CONST_MEAS)

	if args.polar:
		ax.set_title('Measured Performance')
	else:
		# Usually this also has crappy lower ylimits, so we fix that here.
		# get ALL THE LOWER bounds
		np.min([np.min(line.get_ydata()) for line in ax[2].get_lines()])
		ax[0].set_title('Measured Performance')
		ax[0].set_ylabel('Gain (dB)')
		######### FIXME ########################################################
		#ax[0].set_ylim(np.array([-17.5, 2.5]))
		ax[0].set_ylim(np.array([-16, -2]))
		ax[1].set_ylabel('Relative Phase (deg)')
		ax[2].set_ylabel('Relative Phase (deg)')
		ax[2].set_title('Relative Phase')
		ax[1].set_ylim(np.array([-100, 360]))
		ax[2].set_ylim(np.array([-100, 360]))

		marker_freq = 28.1
		LPRDefaultPlotting.annotateArrow(ax[0], -4, \
			[marker_freq+0.05+0.02, marker_freq+0.15+0.02], direction='left')

		for i in [5]:
			aT=ax[i]
			aR=ax[0]
			#aT.plot(imeas.f, gain_pm)
			aT.plot(imeas.f, gain_rms)
			for axTLi,axTL in enumerate(aT.get_lines()):
				axTL.set_linewidth(2.0)
				axTL.set_color('black')
				if axTLi == 0:
					axTL.set_linestyle('-.')
				else:
					axTL.set_linestyle(':')
			aT.set_ylabel('RMS Gain Variation (dB)')

			marker_freq = 27.7
			marker_point = np.argmin(np.abs(imeas.f-marker_freq))
			marker_height = gain_pm[marker_point]
			marker_height = gain_rms[marker_point]
			LPRDefaultPlotting.annotateArrow(aT, marker_height+0.5, \
				[marker_freq+0.05+0.02, marker_freq+0.15+0.02])
			aT.set_ylim((aR.get_ylim()/np.array(1)+16)/1)
			aT.set_yticks([x for x in aT.get_yticks() if x <= 7.5])
			aR.set_yticks([x for x in aR.get_yticks() if x >= -17.5])
			aT.grid()
		######### FIXME ########################################################

		for i in range(3,5):
			aT=ax[i]
			aR=ax[i-2]
			# make the ticks, and the y-axis line up in a tidy manner
			# Recall that the ylimits should be 0-360 basically.
			aT.set_ylabel('RMS Error (deg)')
			aT.plot(imeas.f, ang_rms)
			#marker_freq = 27.5
			#marker_freq = 28.3
			marker_freq = 27.8
			marker_point = np.argmin(np.abs(imeas.f-marker_freq))
			marker_height = ang_rms[marker_point]+2

			# The goal is to take the usual step size of 50,
			# and then equate that with a 1-degree step in RMS Error
			# and to then adjust the y-limit of the twin-axis to align
			# the grid markers
			if False:
				yRscl=np.diff(aR.get_yticks()[-2:])
				yTscl=np.diff(aT.get_yticks()[-2:])
				# Now find the ratio of the ylimits margin verses their
				# extreme tick marks.
				yRmrks = aR.get_yticks()[[0,-1]]
				yTmrks = aT.get_yticks()[[0,-1]]
				tickTotal = max(len(aT.get_yticks()), len(aR.get_yticks()))
				yRover = (aR.get_ylim()-yRmrks)/yRscl
				yTover = (aT.get_ylim()-yTmrks)/yTscl
				yRTover = np.stack((yRover,yTover))
				yXover = np.array([np.min(yRTover[:,0]), np.max(yRTover[:,1])])
				aR.set_ylim(yRscl*yXover + yRmrks)
				aT.set_ylim(yTscl*yXover + yTmrks)
			#aT.set_ylim(aR.get_ylim()/np.array(20)+9)
			aT.set_yticks(np.arange(0,11,5))
			aR.set_yticks(np.arange(0,361,60))
			aT.set_ylim((0,50))
			aR.set_ylim((-90,360))
			aT.grid()
			LPRDefaultPlotting.addHalfTicks(aT)
			LPRDefaultPlotting.addHalfTicks(aR)

			aT.get_lines()[0].set_linewidth(2.0)
			aT.get_lines()[0].set_linestyle('-.')
			aT.get_lines()[0].set_color('black')
			LPRDefaultPlotting.annotateArrow(aT, marker_height-0.5, \
				[marker_freq+0.05, marker_freq+0.15])

		#ax[5].set_ylim(np.array([0, 20]))
		#ax[3].set_ylim(np.array([0, 42]))
		#ax[3].set_ylim(np.array([0, 23]))

		for aT in ax:
			aT.set_xlabel('Frequency (GHz)')
			aT.grid()
			#aT.set_xlim((np.min(imeas.f), np.max(imeas.f)))
			#aT.set_xlim((28-1.0, 28+1.0))
			aT.set_xlim((28-0.5, 28+0.5))

	if args.polar:
		old_pos = ax.title.get_position()
		ax.title.set_position((old_pos[0], 1.1))


	h.tight_layout()
	if not args.polar:
		h2.tight_layout()
	if args.save:
		with open('%s/Summary-%s-%s.txt' % (figdir, FamStr,
			group_filename_string), 'w') as summary_file:
			summary_file.write(summary_msg)
			summary_file.write("\n")
			summary_file.close()
		if args.polar:
			h.savefig('%s/PolarGain-%s-%s.%s' % (figdir, FamStr,
				group_filename_string, fig_ext))
		else:
			h.savefig('%s/StdPlots-%s-%s.%s' % (figdir, FamStr,
				group_filename_string, fig_ext))
			h2.savefig('%s/RelStdPlots-%s-%s.%s' % (figdir, FamStr,
				group_filename_string, fig_ext))
	else:
		print(summary_msg)
	if HEADLESS:
		if not args.polar:
			pp.close()
		pp.close()
	else:
		if not args.polar:
			h2.show()
		h.show()
		break
