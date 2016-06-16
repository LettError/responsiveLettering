# encoding: utf-8

###########################################################################################################
#
#
#	General Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/General%20Plugin
#
#
###########################################################################################################


from GlyphsApp.plugins import *

from mathShape.cmd_exportCurrentFont import ExportUI

class ResponsiveLettering(GeneralPlugin):
	def settings(self):
		self.name = "Responsive Lettering"
	
	def start(self):
		print 'GeneralPlugin loaded'
		mainMenu = NSApplication.sharedApplication().mainMenu()
		s = objc.selector(self.exportUI, signature='v@:')
		newMenuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(self.name, s, "")
		newMenuItem.setTarget_(self)
		mainMenu.itemWithTag_(5).submenu().addItem_(newMenuItem)
	
	def exportUI(self):
		print "ExportUI()"
		ExportUI()
	
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__