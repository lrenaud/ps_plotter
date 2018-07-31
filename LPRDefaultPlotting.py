#!/usr/bin/env python3
################################################################################
# Define the prefered plotting defaults.
# These generally translate to how I want stuff to show up in IEEE papers.
# Note that when I do my debugging, I override figure.figsize in my testing
# enviornment.
################################################################################

import matplotlib
import matplotlib.font_manager as FM
import re
from matplotlib import rcParams, pyplot as pp
from cycler import cycler

POLAR_YLIM_CONST=(-18,-6)
POLAR_YLIM_CONST_ALT=(-32,-6)

fcFontList = FM.get_fontconfig_fonts()
# Search only for fonts that have name matches similar to this
# note this is ALSO a priority list
fontsDesired = ['Times', 'Helvetica', 'Arial']
fontsDesiredRe = re.compile('|'.join(fontsDesired), flags=re.IGNORECASE)
# Create a unique set of the fonts selected out of all of the system fonts
fontsAvailable = frozenset([FM.FontProperties(fname=fcFont).get_name()\
	for fcFont in fcFontList if fontsDesiredRe.search(fcFont) != None])

fontSelected=None
for fontSearch in fontsDesired:
	for fontFound in fontsAvailable:
		if re.search(fontSearch, fontFound, flags=re.IGNORECASE) != None:
			fontSelected = fontFound
			break
	if fontSelected != None:
		break
if fontSelected == None:
	print("WARN: None of the requested fonts found on this system.")
else:
	print("INFO: Using font '%s'" % (fontSelected))
	newFontPriority = [fontSelected]
	newFontPriority.extend(rcParams['font.serif'])
	rcParams['font.serif'] = newFontPriority

rcParams['grid.alpha'] = 0.5
rcParams['grid.linestyle'] = ':'
rcParams['font.family'] = ['serif']
rcParams['font.size'] = 7
#rcParams['figure.titlesize'] = "medium"
rcParams['axes.titlesize'] = 9
rcParams['figure.titlesize'] = rcParams['axes.titlesize']
#rcParams['mathtext.fontset'] = 'dejavuserif'
#rcParams['mathtext.fontset'] = 'custom'
rcParams['mathtext.it'] = 'serif:italic'
rcParams['mathtext.bf'] = 'serif:bold'
rcParams['mathtext.sf'] = 'serif'
rcParams['mathtext.tt'] = 'monospace'
rcParams['lines.linewidth'] = 1.0

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

def figAnnotateCorner(hfig, msg, corner=1, ratio=0.01, clear=True):
	if clear:
		figAnnotateClear(hfig)
	if corner in [1,2]:
		loc_x = ratio
		algn_h = 'left'
	else:
		loc_x = 1-ratio
		algn_h = 'right'
	if corner in [1,4]:
		loc_y = ratio
		algn_v = 'bottom'
	else:
		loc_y = 1-ratio
		algn_v = 'top'
	ax = hfig.get_axes()[0]
	hfig.text(loc_x, loc_y, msg, transform=ax.transAxes,
		va=algn_v, ha=algn_h)

def axAnnotateCorner(ha, msg, corner=1, ratio=0.01):
	if corner in [1,2]:
		loc_x = ratio
		algn_h = 'left'
	else:
		loc_x = 1-ratio
		algn_h = 'right'
	if corner in [1,4]:
		loc_y = ratio
		algn_v = 'bottom'
	else:
		loc_y = 1-ratio
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
