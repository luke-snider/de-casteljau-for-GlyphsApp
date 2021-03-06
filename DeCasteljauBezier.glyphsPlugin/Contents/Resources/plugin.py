# encoding: utf-8
'''
De Casteljau
Copyright (c) 2018 Lukas Schneider / Revolver Type Foundry. All rights reserved.
www.revolvertypefoundry.com / info@revolvertype.com

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

from __future__ import division, print_function, unicode_literals
from DeCasteljau import DeCasteljau

import objc
from GlyphsApp import *
from GlyphsApp.plugins import *
import traceback

hasAllModules = True

try:
	from vanilla import *
except:
	hasAllModules = False
	print("Exception in De Casteljau Bezier:")
	print('-'*60)
	traceback.print_exc(file=sys.stdout)
	print('-'*60)
warned = False

class DeCasteljauTool(GeneralPlugin):

	@objc.python_method
	def settings(self):
		self.name = "DeCasteljau"

	@objc.python_method
	def start(self):
		newMenuItem = NSMenuItem(self.name, self.showWindow_)
		Glyphs.menu[EDIT_MENU].append(newMenuItem)
		self.DeCasteljau = DeCasteljau()
		self.isDrawing = False
		self.DeCasteljau.w.bind("close", self.stopDrawing_)

	@objc.python_method
	def startDrawing(self):
		if not self.isDrawing:
			self.isDrawing = True
			GSCallbackHandler.addCallback_forOperation_(self, DRAWBACKGROUND)
		self.DeCasteljau.updateView()

	def stopDrawing_(self, sender):
		if self.isDrawing:
			self.isDrawing = False
			GSCallbackHandler.removeCallback_forOperation_(self, DRAWBACKGROUND)
		self.DeCasteljau.updateView()

	def drawBackgroundForLayer_options_(self, layer, options):
		"""
		Whatever you draw here will be displayed BEHIND the paths.
		"""
		try:
			self.DeCasteljau.scale = options["Scale"]
			self.DeCasteljau.drawTangents(layer)
		except Exception as e:
			print(traceback.format_exc())

	def showWindow_(self, sender):
		""" Do something like show a window"""
		
		if not hasAllModules and not warned:
			warned = True
			ErrorString = "This plugin needs the vanilla, robofab and fontTools module to be installed for python %d.%d." % (sys.version_info[0], sys.version_info[1])
			Message(ErrorString, title="Problem with some modules")
			return
		if not self.DeCasteljau.w._window: # after closing the window, the NSWindow, might go away. so we need to recreate it. TODO: find a better solution
			self.DeCasteljau.DeCasteljauInit()
		self.DeCasteljau.showWindow()
		self.startDrawing()

	def setController_(self, controller):
		pass

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
