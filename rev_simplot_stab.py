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
args_parser.add_argument('--headless','-q', action='store_true',
	help='Remain neadless even if we aren\'t saving files.')
args_parser.add_argument('-n', type=int, default=0,
	help='plot testing number')
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
if not HEADLESS: pp.interactive(True)
import LPRDefaultPlotting
from tankComputers import *
import csv

file_list = [
	['stability_corners',
	'20190727_PS_KF_Simulation_NoBuffer_BiasDP_WorstCase_C9']
]

file_test = file_list[args.n]

fig_dir='figures-revised'
fn='revisedData/clean_%s.csv' % (file_test[1])
fo=file_test[0]

fh=open(fn,'r')
reader=csv.reader(fh)
h1 = None

if args.n in [0,1,2]: # X/Y data
	x_dat=[]
	y_dat=[]
	reader.__next__() # toss the keys

	for row in reader:
		x_dat.append(float(row[0]))
		y_dat.append(float(row[1]))

y_lims = None

if args.n == 0:
	x = 1e-9 * np.array(x_dat)
	lab_x = 'Frequency (GHz)'
	lab_title = 'Noise Figure vs. Frequency'
	h1=pp.figure(figsize=(3.4,1.8))

if args.n == 1:
	x = np.array(x_dat)*1e3
	lab_x = 'Bias (mV)'
	lab_title = 'Noise Figure vs. Q-enhancement bias'

if args.n in [0, 1]:
	y = np.array(y_dat)
	lab_y = 'Noise Figure (dB)'
	y_lims = [9.7, 10.7]
	x_lims = [min(x),max(x)]

if args.n == 2:
	x = np.array(x_dat) * 1e3
	y = np.array(y_dat)
	lab_x = 'Bias (mV)'
	lab_y = '$K_f$ (-)'
	lab_title = 'Stability vs. Bias'
	y_lims = [-2, 50]
	x_lims = [min(x),500]
	h1=pp.figure(figsize=(3.4,2))


if h1 == None: h1 = pp.figure(figsize=(3.4,2))
ax = h1.add_subplot(1,1,1)

ax.plot(x,y)
ax.set_title(lab_title)
ax.set_xlabel(lab_x)
ax.set_ylabel(lab_y)
ax.set_xlim(x_lims)

if y_lims != None: ax.set_ylim(y_lims)
if args.n == 2:
	nl_x = np.ones((2,1))*min(x[y <= 0])
	nl_y = ax.get_ylim()
	nl_1 = matplotlib.lines.Line2D(nl_x, nl_y)
	nl_x = np.ones((2,1))*400
	nl_2 = matplotlib.lines.Line2D(nl_x, nl_y)
	for nl in [nl_1, nl_2]:
		nl.set_color('C1')
	ax.add_line(nl_1)
	LPRDefaultPlotting.annotateArrow(ax, 5, [397, 381], direction='left')
	LPRDefaultPlotting.annotateArrow(ax, 10, [481, 495])

	LPRDefaultPlotting.annotateArrowStr(ax, 
		"Measurement\nBound", 5, 350)
	LPRDefaultPlotting.annotateArrowStr(ax, 
		"Unstable\nRegion", 15, 475)

	ax.add_line(nl_2)

ax.grid(True)
h1.tight_layout()

if args.save:
	h1.savefig('%s/%s.%s' % (fig_dir, fo, fig_ext))
if HEADLESS:
	pp.close()