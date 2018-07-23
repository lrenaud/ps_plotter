#!/usr/bin/env python3
import numpy as np
import sys

################################################################################
# BEWARE, FOR BEYOND THIS POINT THERE BE DRAGONS! THIS IS ONLY FOR EASE OF
# GENERATING ACADEMIC PUBLICATIONS AND FIGURES, NEVER DO THIS SHIT!
################################################################################

def g1_map_default(system):
	# compute correction factor for g1 that will produce common gain at f0
	g1_swp = system.g1 * np.sin(np.pi/2-system.phase_swp) / system.alpha_swp
	return g1_swp
	
def g1_map_flat(system):
	return system.g1*np.ones(system.phase_swp.shape)

# Operating Enviornment
#####
class ampSystem:
	f0		= 28
	bw0		= 8
	bw_plt	= 3
	"""define global (hardware descriptive) variables for use in our system."""
	def __init__(self, quiet=False):
		self.f0		= self.__class__.f0 # design frequency (GHz)
		self.bw0	= self.__class__.bw0 # assumed extreme tuning range (GHz)
		self.bw_plt	= self.__class__.bw_plt # Plotting range (GHz)

		# Configuration Of Hardware
		#####
		self.q1_L	= 25
		self.q1_C	= 8
		self.l1		= 140e-3 # nH
		self.gm1	= 25e-3 # S

		self._gamma_steps=8
		self._gamma_cap_ratio = 0.997
		self.alpha_min=1
		if not quiet:
			## Report System Descrption
			print('  L1 = %.3fpH, C1 = %.3ffF' % (1e3*self.l1, 1e6*self.c1))
			print('    Rp = %.3f Ohm' % (1/self.g1))
			print('    Q  = %.1f' % (self.Q1))
		self._gamma_warn = False
		
		self._g1_map_function = g1_map_default
	
	@property
	def w0(self):
		return self.f0*2*np.pi
	@property
	def fbw(self): # fractional bandwidth
		return self.bw0/self.f0

	# Compute system 
	#####
	@property
	def c1(self):
		return 1/(self.w0*self.w0*self.l1)
	@property
	def g1(self):
		g1_L	= 1 / (self.q1_L*self.w0*self.l1)
		g1_C	= self.w0 * self.c1 / self.q1_C
		return g1_L + g1_C
	@property
	def Q1(self):
		return np.sqrt(self.c1/self.l1)/self.g1

	@property
	def phase_max(self):
		return np.pi/2 * (1 - 1/self.gamma_len)
	@property
	def gamma_len(self):
		return self._gamma_steps

	@property
	def gamma(self):
		gamma = 1 - np.power(self.f0 / (self.f0 + self.bw0/2),2)
		phase_limit_requested = (1-1/self.gamma_len)*np.pi/2

		# Verify gamma is valid
		#####
		gamma_max = 1/(self.alpha_min*self.Q1)
		if gamma > (self._gamma_cap_ratio * gamma_max):
			if not self._gamma_warn:
				self._gamma_warn = True
				print("==> WARN: Gamma to large, reset to %.1f%% (was %.1f%%) <==" % \
					(100*self._gamma_cap_ratio * gamma_max, 100*gamma))
			gamma = self._gamma_cap_ratio * gamma_max
		return gamma

	@property
	def alpha_swp(self):
		range_partial = np.ceil(self.gamma_len/2)
		lhs = np.linspace(np.sqrt(self.alpha_min),1, range_partial)
		rhs = np.flip(lhs,0)
		swp = np.concatenate((lhs,rhs[1:])) if np.mod(self.gamma_len,2) == 1 \
												else np.concatenate((lhs,rhs))
		return np.power(swp,2)

	@property
	def gamma_swp(self):
		return np.cos(np.pi/2-self.phase_swp) / self.Q1 / self.alpha_swp
	@property
	def phase_swp(self):
		#def phaseSweepGenerate(g1, gamma, c, l, phase_extreme, phase_steps):
		# Linear PHASE gamma spacing
		# First compute the most extreme phase given the extreme gamma
		# if gamma is tuned to the limit, and we want to match the gain performance,
		# then this is the required tuned g1 value.
		gamma = self.gamma
		g1_limit = np.sqrt(np.power(self.g1,2) - np.power(gamma,2)*self.c1/self.l1)
		# This implies a Q in that particular setting
		Q_limit = self.Q1*self.g1/g1_limit
		# given this !, I compute the delta phase at that point.
		phase_limit = np.pi/2 - np.arctan(1/(Q_limit*gamma))

		phase_swp = np.linspace(-1,1,self.gamma_len) * self.phase_max

		if phase_limit < self.phase_max:
			print(	"==> ERROR: Phase Beyond bounds. Some states will be ignored")
			print(	"           %.3f requested\n"
					"           %.3f hardware limit" % \
				(180/np.pi*self.phase_max, 180/np.pi*abs(phase_limit)))
			print(	"    To increase tuning range, gamma must rise or native Q must rise")
			phase_swp = np.where(phase_swp > phase_limit, phase_swp, np.NaN)

		# This gives us our equal phase spacing points
		return phase_swp
	
	@property
	def c1_swp(self):
		return self.c1 * (1 + self.gamma_swp)
		
	def set_g1_swp(self, g1_swp_function):
		self._g1_map_function = g1_swp_function
	
	@property
	def g1_swp(self):
		return self._g1_map_function(self)
	
	def compute_block(self, f_dat):
		g1_swp = self.g1_swp
		c1_swp = self.c1_swp
		y_tank	= np.zeros((self.gamma_len,f_dat.steps), dtype=complex)
		tf		= np.zeros((self.gamma_len,f_dat.steps), dtype=complex)
		for itune,gamma_tune in enumerate(self.gamma_swp):
			c1_tune = c1_swp[itune]
			g1_tune = g1_swp[itune]
			y_tank[itune,:] = g1_tune + f_dat.jw*c1_tune + 1/(f_dat.jw * self.l1)
			tf[itune,:] = self.__class__.tf_compute(f_dat.delta, gamma_tune, g1_tune, self.gm1, self.l1, self.c1)

		tf = tf.T
		return (y_tank, tf)

	def compute_ref(self, f_dat):
		y_tank = self.g1 + f_dat.jw*self.c1 + 1/(f_dat.jw * self.l1)
		tf = self.__class__.tf_compute(f_dat.delta, 0, self.g1, self.gm1, self.l1, self.c1)
		return (y_tank, tf)
	
	@classmethod
	def tf_compute(cls, delta, gamma, gx, gm, l, c):
		Q = np.sqrt(c/l)/gx
		return gm / gx \
			* 1j*(1+delta) \
			/ (1j*(1+delta) + Q*(1-np.power(1+delta,2)*(1+gamma)))

# Operating Enviornment
#####
class bufferSystem:
	"""define global (hardware descriptive) variables for use in our system."""
	def __init__(self, quiet=False):
		self.f0		= ampSystem.f0 # design frequency (GHz)
		self.bw0	= ampSystem.bw0 # assumed extreme tuning range (GHz)
		self.bw_plt	= ampSystem.bw_plt # Plotting range (GHz)

		# Configuration Of Hardware
		#####
		self.q2_L	= 25
		self.q2_C	= 50
		self.l2		= 140e-3 # nH
		self.gm2	= 5e-3 # S

		if not quiet:
			## Report System Descrption
			print('  L2 = %.3fpH, C2 = %.3ffF' % (1e3*self.l2, 1e6*self.c2))
			print('    Rp = %.3f Ohm' % (1/self.g2))
			print('    Q  = %.1f' % (self.Q2))

	@property
	def w0(self):
		return self.f0*2*np.pi
	@property
	def fbw(self): # fractional bandwidth
		return self.bw0/self.f0

	# Compute system 
	#####
	@property
	def c2(self):
		return 1/(self.w0*self.w0*self.l2)
	@property
	def g2(self):
		g2_L	= 1 / (self.q2_L*self.w0*self.l2)
		g2_C	= self.w0 * self.c2 / self.q2_C
		return g2_L + g2_C
	@property
	def Q2(self):
		return np.sqrt(self.c2/self.l2)/self.g2

	def compute_ref(self, f_dat):
		y_tank = self.g2 + f_dat.jw*self.c2 + 1/(f_dat.jw * self.l2)
		tf = self.__class__.tf_compute(f_dat.delta, self.g2, self.gm2, self.l2, self.c2)
		return (y_tank, tf)

	@classmethod
	def tf_compute(cls, delta, gx, gm, l, c):
		Q = np.sqrt(c/l)/gx
		return gm / gx \
			* 1j*(1+delta) \
			/ (1j*(1+delta) + Q*(1-np.power(1+delta,2)))

