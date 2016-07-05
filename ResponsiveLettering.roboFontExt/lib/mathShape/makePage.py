# -*- coding: utf-8 -*-

import os
import json

import codecs

"""

	Because we need a way to preview a mathshape in a single page without having to load a json file locally.
"""


class PageMaker(object):
	# XXXX does not need to be a class.

	htmlPath = "template.html"
	cssPath = "styles.css"
	mathShapePath = "mathShape.js"
	outputPath = "test.html"

	animateBreatheCode = """// make the images breathe.
// entirely optional but definitely entertaining
setInterval(function () { 
	breathShape += 0.04;
	myMathShape.breathe(0.5*Math.sin(breathShape*Math.PI)+0.5)
}, 50);
"""

	def hexColor(self, color):
		return u"#%02x%02x%02x"%(int(round(color[0]*0xff)), int(round(color[1]*0xff)), int(round(color[2]*0xff)))

	def rgbaColor(self, color):
		return u"rgba(%d, %d, %d, %2.2f)"%(int(round(color[0]*255)), int(round(color[1]*255)), int(round(color[2]*255)), color[3])

	def __init__(self, resourcesRoot, shapePath, outputPath, shapeColor=None, bgColor=None, saveFile=True, animate=True):
		self.shapePath = shapePath
		self.root = resourcesRoot
		# acquire the code
		f = codecs.open(os.path.join(self.root, self.htmlPath), 'r', 'utf-8')
		self.html = f.read()
		f.close()
		f = codecs.open(os.path.join(self.root, self.cssPath), 'r', 'utf-8')
		css = f.read()
		f.close()
		f = codecs.open(os.path.join(self.root, self.mathShapePath), 'r', 'utf-8')
		js = f.read()
		f.close()
		# mathshape data
		jsonPath = os.path.join(shapePath, 'files.json');
		# print "jsonPath", jsonPath
		f = codecs.open(jsonPath, 'r', 'utf-8')
		data = f.read()
		f.close()
		jsonData = json.loads(data)
		svgLoaderContainer = []
		for name in jsonData['files']:
			svgPath = os.path.join(shapePath, os.path.basename(name))
			# print svgPath, os.path.exists(svgPath)
			f = codecs.open(svgPath, 'r', 'utf-8')
			svgData = f.read()
			svgLoaderContainer.append(svgData)

		# paste
		self.html = self.html.replace("//mathshape", js)
		self.html = self.html.replace("/*styles*/", css)
		self.html = self.html.replace("//__jsondata", data)
		self.html = self.html.replace("<!--svgobjects-->", "\n".join(svgLoaderContainer))
		
		self.html = self.html.replace(u'/*shapeFillColor*/', u"\""+self.rgbaColor(shapeColor)+u"\"")
		self.html = self.html.replace(u'/*bgColor*/', self.rgbaColor(bgColor))
		if animate:
			# single dimension designspaces do not animate. So there is no need to include the code.
			self.html = self.html.replace(u'// animateBreatheCode', self.animateBreatheCode)
			

		

		# release
		# print self.html]
		if saveFile:
			f = codecs.open(os.path.join(self.root, outputPath), 'w', 'utf-8')
			f.write(self.html)
			f.close()

