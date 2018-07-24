#!/usr/bin/env python3
################################################################################
# Define the prefered plotting defaults.
# These generally translate to how I want stuff to show up in IEEE papers.
# Note that when I do my debugging, I override figure.figsize in my testing
# enviornment.
################################################################################

import matplotlib
from matplotlib import rcParams, pyplot as pp
from cycler import cycler

rcParams['grid.alpha'] = 0.7
rcParams['grid.linestyle'] = ':'
rcParams['font.family'] = ['serif']
rcParams['font.size'] = 8.0
rcParams['mathtext.fontset'] = 'dejavuserif'
rcParams['mathtext.it'] = 'serif:italic'
rcParams['mathtext.bf'] = 'serif:bold'
rcParams['mathtext.sf'] = 'serif'
rcParams['mathtext.tt'] = 'monospace'

# axes.prop_cycle
COLOR_CYCLE_LIST =  [
		[0,      0.4470, 0.7410],
		[0.8500, 0.3250, 0.0980],
		[0.4940, 0.1840, 0.5560],
		[0.4660, 0.6740, 0.1880],
		[0.3010, 0.7450, 0.9330],
		[0.6350, 0.0780, 0.1840],
		[0.9290, 0.6940, 0.1250],
		[1,      0,      1]]#,
#		[0,      1,      1],
#		[1,      0,      0],
#		[0,      1,      0]]

rcParams['axes.prop_cycle'] = (cycler('linestyle',['-','--'])*cycler(color=COLOR_CYCLE_LIST))

for tri in COLOR_CYCLE_LIST:
	color = '0x' + ''.join([ "%02x" % int(255*x) for x in tri])

figures_directory='figures'

def figAnnotateCorner(hfig, msg, corner=1, clear=True):
	if clear:
		figAnnotateClear(hfig)
	if corner in [1,2]:
		loc_x = 0.01
		algn_h = 'left'
	else:
		loc_x = 0.99
		algn_h = 'right'
	if corner in [1,4]:
		loc_y = 0.01
		algn_v = 'bottom'
	else:
		loc_y = 0.99
		algn_v = 'top'
	ax = hfig.get_axes()[0]
	hfig.text(loc_x, loc_y, msg, transform=ax.transAxes,
		va=algn_v, ha=algn_h)

def axAnnotateCorner(ha, msg, corner=1):
	if corner in [1,2]:
		loc_x = 0.01
		algn_h = 'left'
	else:
		loc_x = 0.99
		algn_h = 'right'
	if corner in [1,4]:
		loc_y = 0.01
		algn_v = 'bottom'
	else:
		loc_y = 0.99
		algn_v = 'top'
	#ax = ha.get_axes()[0]
	ha.text(loc_x, loc_y, msg, transform=ha.transAxes,
		va=algn_v, ha=algn_h)

def figAnnotateClear(hobj):
	if type(hobj == matplotlib.figure.Figure):
		hfig = hobj
	children = hfig.get_children()
	for child in children:
		if type(child) == matplotlib.text.Text:
			child.remove()
