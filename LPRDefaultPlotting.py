#!/usr/bin/env python3
################################################################################
# Define the prefered plotting defaults.
# These generally translate to how I want stuff to show up in IEEE papers.
# Note that when I do my debugging, I override figure.figsize in my testing
# enviornment.
################################################################################

from matplotlib import rcParams, pyplot as pp

rcParams['grid.alpha'] = 0.7
rcParams['grid.linestyle'] = ':'
rcParams['font.family'] = ['serif']
rcParams['font.size'] = 9.0
rcParams['mathtext.fontset'] = 'dejavuserif'
rcParams['mathtext.it'] = 'serif:italic'
rcParams['mathtext.bf'] = 'serif:bold'
rcParams['mathtext.sf'] = 'serif'
rcParams['mathtext.tt'] = 'monospace'

