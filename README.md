# What is this?
This whole tool is a basic front end for using Python's `matplotlib` in a
moderately interactive and robust manner to do MATLAB-like number crunching and
(more critically) plot generation for papers.

## MATLAB Soapbox Explanation
While MATLAB has routines to save figures, the graphics back-end routinely runs
into issues with NVIDIA GPU based systems, and I'm sick and tired of being tied
to a tool that has a heavy resource footprint and only moderate documentation.
The licensing restrictions (though not fundamentally debilitating) are a
secondary reason I'm moving away from MATLAB. Finally, as I expect to graduate
soon, the $50 (or $130 for my toolboxes) annual cost is going to rise to a
debilitating point for things as mundane as personal projects. So I might as
well kick an expensive habit while it's easy to fall back when needed.

# Resources
There are a few tricks to help configuring `matplotlib`. I'll update this
document to describe the commands and tools to help decipher the information
required to produce plots in a repeatable and tidy way.

## 1. Plot Defaults
Plot defaults are managed by the `matplotlib`

## 2. Font Selection
```python
import `matplotlib`.font_manager
print(matplotlib.font_manager.fontManager.afmlist)
print(matplotlib.font_manager.fontManager.ttflist)
```

I search for fonts using the following method:
```
import matplotlib.font_manager as FM
import re

fcFontList = FM.get_fontconfig_fonts()
# Search only for fonts that have name matches similar to this
fontsDesired = ['Helvetica', 'Times', 'Arial']
fontsDesiredRe = re.compile('|'.join(fontsDesired), flags=re.IGNORECASE)
# Create a unique set of the fonts selected out of all of the system fonts
fontsAvailable = set([FM.FontProperties(fname=fcFont).get_name()\
	for fcFont in fcFontList if fontsDesiredRe.search(fcFont) != None])

```

[matplotlib docs](https://matplotlib.org/api/font_manager_api.html)

## 3. 

# TODO
* make pySmithPlot a git sub-module
* think of a smarter way to refactor things (this is an ever evolving goal)
