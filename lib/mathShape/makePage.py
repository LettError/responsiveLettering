import os
import json

"""

	Because we need a way to preview a mathshape in a single page without having to load a json file locally.
"""


class PageMaker(object):
	# XXXX does not need to be a class.

	htmlPath = "template.html"
	cssPath = "styles.css"
	mathShapePath = "mathShape.js"
	outputPath = "test.html"

	def __init__(self, resourcesRoot, shapePath, outputPath, fillColor=None, saveFile=True):
		if fillColor is None:
			fillColor = '#ff3300'
		self.shapePath = shapePath
		self.root = resourcesRoot
		# acquire the code
		f = open(os.path.join(self.root, self.htmlPath), 'rb')
		self.html = f.read()
		f.close()
		f = open(os.path.join(self.root, self.cssPath), 'rb')
		css = f.read()
		f.close()
		f = open(os.path.join(self.root, self.mathShapePath), 'rb')
		js = f.read()
		f.close()
		# mathshape data
		jsonPath = os.path.join(shapePath, 'files.json');
		# print "jsonPath", jsonPath
		f = open(jsonPath, 'rb')
		data = f.read()
		f.close()
		jsonData = json.loads(data)
		svgLoaderContainer = []
		for name in jsonData['files']:
			svgPath = os.path.join(shapePath, os.path.basename(name))
			# print svgPath, os.path.exists(svgPath)
			f = open(svgPath, 'rb')
			svgData = f.read()
			svgLoaderContainer.append(svgData)

		# paste
		self.html = self.html.replace("//mathshape", js)
		self.html = self.html.replace("/*styles*/", css)
		self.html = self.html.replace("//__jsondata", data)
		self.html = self.html.replace("<!--svgobjects-->", "\n".join(svgLoaderContainer))
		self.html = self.html.replace('/*testShapeFillColor*/', "\""+fillColor+"\"")

		

		# release
		# print self.html]
		if saveFile:
			f = open(os.path.join(self.root, outputPath), 'w')
			f.write(self.html)
			f.close()


if __name__ == "__main__":
	root = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), "Resources")
	outputPath = os.path.join(root, "test.html")
	# print os.listdir(root)
	pm = PageMaker(root, os.path.join(root,'placeholder_ms'), outputPath)
	print pm.html

