#!/usr/bin/env python
# encoding: utf-8

'''
De Casteljau Algorythm Live Visualisation
Copyright (c) 2018 Lukas Schneider / Revolver Type Foundry. All rights reserved.
www.revolvertypefoundry.com / info@revolvertypefoundry.com

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

import objc
import sys, os, re, traceback

from GlyphsApp import *
from GlyphsApp.plugins import *
from vanilla import *
from AppKit import NSColor, NSBezierPath

class DeCasteljau:

	defaultColorFill = NSColor.colorWithCalibratedRed_green_blue_alpha_(1,0.6,0.4,1)
	defaultColorPts = NSColor.colorWithCalibratedRed_green_blue_alpha_(1,0.3,0.4,1)
	defaultColorFinalPt = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.1,0.2,0.6,1)

	def __init__(self):
		self.heightOfTool = 95
		self.widthOfTool = 255
		self.w = FloatingWindow((self.widthOfTool, self.heightOfTool), "De Casteljau / revolvertype.com")
		self.w.sliderInterpol = Slider((10, 8, -10, 10), sizeStyle="small", minValue=0, maxValue=1, value=0.5, callback=self.sliderCallback)
		y = 35
		self.w.oneTwoThree = SegmentedButton((10, y-5, 125, 20), [dict(title=" 1 "), dict(title=" 2 "), dict(title=" 3 ")], callback=self.updateFromUI)
		self.w.oneTwoThree.set(2)
		self.w.five = CheckBox((130, y-2, 40, 16), '5', callback=self.checkbox5Callback, value=False, sizeStyle="small")
		self.w.ten = CheckBox((160, y-2, 40, 16), '10', callback=self.checkbox10Callback, value=False, sizeStyle="small")
		self.w.off = CheckBox((-45, y-2, 40, 16), 'off', callback=self.updateFromUI, value=False, sizeStyle="small")
		y = 65
		self.w.colorFill = ColorWell((10, y, 30, 18), color=self.defaultColorFill, callback=self.updateFromUI)
		self.w.colorPts = ColorWell((42, y, 30, 18), color=self.defaultColorPts, callback=self.updateFromUI)
		self.w.colorfinalPt = ColorWell((74, y, 30, 18), color=self.defaultColorFinalPt, callback=self.updateFromUI)
		self.w.Info = TextBox((115,y+3,100,20), text="Stroke / Dots:", sizeStyle="small")
		self.w.strokeThickness = EditText((-60,y,25,19), "1", sizeStyle="small", callback=self.settingStrokeThicknessFromUI) 
		self.w.ptThickness = EditText((-35,y,25,19), "2", sizeStyle="small", callback=self.settingPtThicknessFromUI) 

		
		
		self.interpolatedPoints = []
		

	def checkbox5Callback(self, sender):
		if sender.get() == 1:
			self.w.ten.set(0)
			self.w.sliderInterpol.enable(False)
		if sender.get() == 0:
			if self.w.ten.get() == 0:
				self.w.sliderInterpol.enable(True)
		Glyphs.redraw()

	def checkbox10Callback(self, sender):
		if sender.get() == 1:
			self.w.five.set(0)
			self.w.sliderInterpol.enable(False)
		if sender.get() == 0:
			if self.w.five.get() == 0:
				self.w.sliderInterpol.enable(True)
		Glyphs.redraw()

	def sliderCallback(self, sender):
		Glyphs.redraw()

	def updateFromUI(self, sender):
		Glyphs.redraw()

	def settingPtThicknessFromUI(self, sender):
		try:
			ptThickness = int(sender.get())
		except ValueError:
			self.w.ptThickness.set(str(2))
			
		Glyphs.redraw()

	def settingStrokeThicknessFromUI(self, sender):
		try:
			ptThickness = int(sender.get())
		except ValueError:
			self.w.strokeThickness.set(str(1))
			
		Glyphs.redraw()



	def interpolatePoint(self, pt1, pt2, interpolFactor):
		v = interpolFactor
		
		(xa, ya), (xb, yb) = pt1, pt2
		if not isinstance(v, tuple):
			xv = v
			yv = v
		else:
			xv, yv = v
		calculated = xa + (xb - xa) * xv, ya + (yb - ya) * yv
		
		pt_x_rounded = float("{0:.1f}".format(calculated[0]))
		pt_y_rounded = float("{0:.1f}".format(calculated[1]))
		return (pt_x_rounded, pt_y_rounded)


	
	def getSelectedPoints(self, segmentIndex, segment, contour):
		collectionOfSelectedPoints = []
		tempList = []
		if segment.type == "curve":
			
			
			for pts2 in contour.segments[segmentIndex-1]:
				 tempList.append(pts2)
				 
				 
				 
			collectionOfSelectedPoints.append((tempList[-1].x, tempList[-1].y, tempList[-1].type))
			
			
			for pts in segment.points:
				## print(pts.x, pts.y, pts.type)
				collectionOfSelectedPoints.append((pts.x, pts.y, pts.type))
			
		return collectionOfSelectedPoints


	def drawingCalculation(self, glyph, listOfSelectedPoints, interpolFactor):

		color = self.w.colorFill.get()
		
		if len(listOfSelectedPoints) != 0:
			path = NSBezierPath.bezierPath()
			
			path.setLineWidth_(int(self.w.strokeThickness.get()))
			
			for idx, pts in enumerate(listOfSelectedPoints): 
				
				if idx == 0:
					(startpoint_x, startpoint_y) = (listOfSelectedPoints[0][0], listOfSelectedPoints[0][1])
					path.moveToPoint_((startpoint_x, startpoint_y))
				
				else:				 
					path.lineToPoint_(((pts[0]),(pts[1])))
					color.set()
					path.stroke()

			
			
			
			
			processedPoints = []
			interpolatedPoints = []
			for i, pts in enumerate(listOfSelectedPoints):
				try:
					pt1 = (listOfSelectedPoints[i][0],listOfSelectedPoints[i][1])
					pt2 = (listOfSelectedPoints[i+1][0],listOfSelectedPoints[i+1][1])
					processedPoints.append(pt1)
					processedPoints.append(pt2)
					
					
					interpolatedPt = self.interpolatePoint(pt1, pt2, interpolFactor)
					interpolatedPoints.append(interpolatedPt)
					
					
					if interpolatedPt in processedPoints:
						pass
					else:
						pass
						
						
							#self.drawPointCoordinates(glyph, pt = interpolatedPt)
				except IndexError:
					pass
			
			self.interpolatedPoints = interpolatedPoints


	def getScale( self ):
		"""
		Returns the current scale factor of the Edit View UI.
		Divide any scalable size by this value in order to keep the same pixel size.
		"""
		try:
			return self.controller.graphicView().scale()
		except:
			self.logToConsole( "getScale error: Scale defaulting to 1.0. %s" % str(e) )
			return 1.0

	def drawTangents(self, glyph):
		try:
			# 3 (segmented button) turns off
			if self.w.off.get() != 1:
				try:
					
					
					stepsToDraw = []
					if self.w.five.get() == 1:
						divisor = 10
						for interpolFactor in range(0,100,divisor):
							interpolFactor = interpolFactor * 0.01
							stepsToDraw.append(interpolFactor)
					if self.w.ten.get() == 1:
						divisor = 5
						for interpolFactor in range(0,100,divisor):
							interpolFactor = interpolFactor * 0.01
							stepsToDraw.append(interpolFactor)
					else:
						interpolFactor = float("{0:.2f}".format(self.w.sliderInterpol.get()))
						stepsToDraw.append(interpolFactor)

					print "stepsToDraw", stepsToDraw
					
					for contour in glyph.contours:
						for segmentIndex, segment in enumerate(contour.segments):
							
							allInterpolatedPoints = []
							lastInterpolatedPt = []
							if segment.type == "line":
								pass
							else:
								for interpolFactor in stepsToDraw:
									listOfSelectedPoints = self.getSelectedPoints(segmentIndex, segment, contour)
									self.drawingCalculation(glyph, listOfSelectedPoints, interpolFactor)
									
									
									if self.w.oneTwoThree.get() != 0:
										allInterpolatedPoints.extend(self.interpolatedPoints)
									for a in range(self.w.oneTwoThree.get()):
										self.drawingCalculation(glyph, self.interpolatedPoints, interpolFactor)
										allInterpolatedPoints.extend(self.interpolatedPoints)
										if a == 1:
											try:
												lastInterpolatedPt.append((self.interpolatedPoints[-1]))
											except IndexError:
												pass
							
							
							for point in allInterpolatedPoints:
								if point in lastInterpolatedPt:
									colorDots = self.w.colorfinalPt.get()
									self.drawDot(point, colorDots)
								else:
									colorDots = self.w.colorPts.get()
									self.drawDot(point, colorDots)
				except TypeError:
					pass
		except AttributeError:
			return

	def drawDot(self, point, colorDots):
		widthP = int(self.w.ptThickness.get())	  
		path = NSBezierPath.bezierPath()
		path.moveToPoint_((point[0]-widthP, point[1]+0))
		path.curveToPoint_controlPoint1_controlPoint2_((point[0]+0, point[1]+widthP),(point[0]-widthP, point[1]+widthP), (point[0]+0, point[1]+widthP))
		path.curveToPoint_controlPoint1_controlPoint2_((point[0]+widthP, point[1]+0), (point[0]+widthP, point[1]+widthP), (point[0]+widthP, point[1]+0))
		path.curveToPoint_controlPoint1_controlPoint2_((point[0]+0, point[1]-widthP), (point[0]+widthP, point[1]-widthP), (point[0]+0, point[1]-widthP))
		path.curveToPoint_controlPoint1_controlPoint2_((point[0]-widthP, point[1]+0), (point[0]-widthP, point[1]-widthP), (point[0]-widthP, point[1]+0))
		path.closePath()
		colorDots.set()
		path.fill()
		
		










	
	def interfaceVersion( self ):
		"""
		Distinguishes the API version the plugin was built for. 
		Return 1.
		"""
		try:
			return 1
		except Exception as e:
			self.logToConsole( "interfaceVersion: %s" % str(e) )

	def title( self ):
		"""
		This is the name as it appears in the menu in combination with 'Show'.
		E.g. 'return "Nodes"' will make the menu item read "Show Nodes".
		"""
		try:
			return "LS Cadencer"
		except Exception as e:
			self.logToConsole( "title: %s" % str(e) )

	def keyEquivalent( self ):
		"""
		The key for the keyboard shortcut. Set modifier keys in modifierMask() further below.
		Pretty tricky to find a shortcut that is not taken yet, so be careful.
		If you are not sure, use 'return None'. Users can set their own shortcuts in System Prefs.
		"""
		try:
			return "l"
		except Exception as e:
			self.logToConsole( "keyEquivalent: %s" % str(e) )

	def modifierMask( self ):
		"""
		Use any combination of these to determine the modifier keys for your default shortcut:
			return NSShiftKeyMask | NSControlKeyMask | NSCommandKeyMask | NSAlternateKeyMask
		Or:
			return 0
		... if you do not want to set a shortcut.
		"""
		try:
			return NSCommandKeyMask | NSShiftKeyMask | NSAlternateKeyMask
			#return 0
		except Exception as e:
			self.logToConsole( "modifierMask: %s" % str(e) )

	def drawForegroundForLayer_( self, Layer ):
		"""
		Whatever you draw here will be displayed IN FRONT OF the paths.
		Setting a color:
			NSColor.colorWithCalibratedRed_green_blue_alpha_( 1.0, 1.0, 1.0, 1.0 ).set() # sets RGBA values between 0.0 and 1.0
			NSColor.redColor().set() # predefined colors: blackColor, blueColor, brownColor, clearColor, cyanColor, darkGrayColor, grayColor, greenColor, lightGrayColor, magentaColor, orangeColor, purpleColor, redColor, whiteColor, yellowColor
		Drawing a path:
			myPath = NSBezierPath.alloc().init()  # initialize a path object myPath
			myPath.appendBezierPath_( subpath )   # add subpath to myPath
			myPath.fill()   # fill myPath with the current NSColor
			myPath.stroke() # stroke myPath with the current NSColor
		To get an NSBezierPath from a GSPath, use the bezierPath() method:
			myPath.bezierPath().fill()
		You can apply that to a full layer at once:
			if len( myLayer.paths > 0 ):
				myLayer.bezierPath()	   # all closed paths
				myLayer.openBezierPath()   # all open paths
		See:
		https://developer.apple.com/library/mac/documentation/Cocoa/Reference/ApplicationKit/Classes/NSBezierPath_Class/Reference/Reference.html
		https://developer.apple.com/library/mac/documentation/cocoa/reference/applicationkit/classes/NSColor_Class/Reference/Reference.html
		"""
		try:
			pass
		except Exception as e:
			self.logToConsole( "drawForegroundForLayer_: %s" % str(e) )



	def logToConsole( self, message ):
		"""
		The variable 'message' will be passed to Console.app.
		Use self.logToConsole( "bla bla" ) for debugging.
		"""
		myLog = "Show %s plugin:\n%s" % ( self.title(), message )

		NSLog( myLog )

	def showWindow(self):
		if not self.w.isVisible():
			self.w.open()
			self.w.makeKey()
			self.w.show()
