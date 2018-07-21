#!/usr/bin/env python3
import numpy as np

class FreqClass:
	def __init__(self, steps, f0, bw):
		self.f0 = f0
		self._bw = bw
		self._steps = steps;
		self._update_delta()
	
	def _update_delta(self):
		self._delta = self._bw/self.f0*np.linspace(-1/2,1/2,self._steps)
	
	def __repr__(self):
		return self.__str__()
	def __str__(self):
		return "%gGHz, %gGHz BW sweep [%d points]" % \
			(self.f0, self._bw, self._steps)
	
	@property
	def hz_range(self):
		return (np.min(self.hz), np.max(self.hz))
	
	@property
	def delta(self):
		return self._delta
	@property
	def bw(self):
		return self._bw
	@bw.setter
	def bw(self, bw):
		self._bw = bw
		self._update_delta()
	
	@property
	def steps(self):
		return self._steps
	@steps.setter
	def steps(self, steps):
		self._steps = steps
		self._update_delta()
	
	@property
	def hz(self):
		return self.f0*(1+self._delta)
	@property
	def f(self):
		return self.hz
	@property
	def rad(self):
		return 2*np.pi*self.f0*(1+self._delta)
	@property
	def w(self):
		return self.rad
	@property
	def jw(self):
		return 2j*np.pi*self.f0*(1+self._delta)
	@property
	def delta(self):
		return self._delta


