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
import csv

file_test = ['stability_contour',
		'20190727_PS_KFMin_MatrixFine_Value']

fig_dir='figures-revised'
fn='revisedData/%s.csv' % (file_test[1])
fo=file_test[0]

fh=open(fn,'r')
reader=csv.reader(fh)
h1 = None

d=[]
for row in reader:
	d.append([float(x) for x in row])

d=np.array(d)
bias = d[0,1:]
code = d[1:,0]
kf = d[1:,1:]
kf[kf > 20]

h1 = pp.figure(figsize=(3.4,3.4))
ax = h1.add_subplot(1,1,1)
bias_m,code_m = np.meshgrid(bias,code)

cs = ax.contour(bias_m, code_m, kf)
cl = ax.clabel(cs, inline=1)

if False:

	ax.plot(x,y)
	ax.set_title(lab_title)
	ax.set_xlabel(lab_x)
	ax.set_ylabel(lab_y)
	ax.set_xlim(x_lims)
	if y_lims != None: ax.set_ylim(y_lims)
	ax.grid(True)
	h1.tight_layout()

	if args.save:
		h1.savefig('%s/%s.%s' % (fig_dir, fo, fig_ext))
	if HEADLESS:
		pp.close()