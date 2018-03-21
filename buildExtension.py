
"""

	This script intends to copy a couple of things to the roboFontExt
	so that all the python code can live in an accessible place.

"""

import os, shutil

root = os.getcwd()
print(root)
extensionPath = os.path.join(root, u"ResponsiveLettering.roboFontExt")
srcLibPath = os.path.join(root, u'lib', u'mathShape')
dstLibPath = os.path.join(root, u"ResponsiveLettering.roboFontExt", u'lib', u'mathShape')

srcMathShapePath = os.path.join(root, u'www', u'mathShape.js')
dstMathShapePath = os.path.join(extensionPath, u'resources')

print("extensionPath", extensionPath)
print("srcLibPath", srcLibPath)
print('dstLibPath', dstLibPath)


# print os.listdir(srcLibPath)
# print os.listdir(dstLibPath)
# print os.listdir(extensionPath)

# copy mathShape.js from www to extension
print(os.path.exists(srcMathShapePath), srcMathShapePath)
print(os.path.exists(dstMathShapePath), dstMathShapePath)
print(os.listdir(dstMathShapePath))
print(shutil.copy(srcMathShapePath, dstMathShapePath))

# copy the lib to the extension
if os.path.exists(dstLibPath):
	shutil.rmtree(dstLibPath)
shutil.copytree(srcLibPath, dstLibPath, )

