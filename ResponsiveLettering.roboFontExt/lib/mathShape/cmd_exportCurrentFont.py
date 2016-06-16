# -*- coding: utf-8 -*-

import os
import json
import vanilla

from mojo.UI import *
from AppKit import NSColor

from exportTools import makeSVGShape, makeMaster
import makePage
reload(makePage)
from makePage import PageMaker

import tempfile

class ExportUI(object):
    shapeColorLibKey = "com.letterror.mathshape.preview.shapecolor"
    backgroundColorLibKey = "com.letterror.mathshape.preview.bgcolor"
    preferredFilenameLibKey = "com.letterror.mathshape.filename"
    masterNames = ['narrow-thin', 'wide-thin', 'narrow-bold', 'wide-bold']
    def __init__(self):
        f = CurrentFont()
        if f is None:
            return
        self.shapeColor = None
        self.backgroundColor = None
        self.extrapolateMinValue = 0
        self.extrapolateMaxValue = 1
        self.w = vanilla.Window((500, 600), "Responsive Lettering", minSize=(300,200))
        self.w.preview = HTMLView((0,0,-0, -140))
        self.w.exportButton = vanilla.Button((-150, -30, -10, 20), "Export SVG", callback=self.cbExport)        
        columnDescriptions = [
            dict(title="Glyphname", key="name", width=125),
            dict(title="Width", key="width", width=50),
            dict(title="Height", key="height", width=50),
            dict(title="Bounds?", key="bounds", width=75),
            dict(title="Contours", key="contours", width=50),
            dict(title="Points", key="points", width=50),
        ]
        self.w.l = vanilla.List((0,-140,-0,-40), self.wrapGlyphs(), columnDescriptions=columnDescriptions, doubleClickCallback=self.callbackListClick)
        self.w.t = vanilla.TextBox((70,-27,-160,20), "FontName", sizeStyle="small")
        self.w.backgroundColorWell = vanilla.ColorWell((10,-30, 20, 20), callback=self.backgroundColorWellCallback, color=NSColor.blackColor())
        self.w.shapeColorWell = vanilla.ColorWell((35,-30, 20, 20), callback=self.shapeColorWellCallback, color=NSColor.whiteColor())

        self.w.bind("became main", self.windowBecameMainCallback)
        self.setColorsFromLib()
        self.update()
        self.w.open()
        self.cbMakePreview(None)
    
    def windowBecameMainCallback(self, sender):
        f = CurrentFont()
        if f is not None:
            self.update()
            self.cbMakePreview(None)

    def callbackListClick(self, sender):
        # called after a double click on one of the glyphs in the list.
        # open up a glyph window.
        f = CurrentFont()
        if f is None:
            return
        for i in sender.getSelection():
            OpenGlyphWindow(glyph=f[self.masterNames[i]], newWindow=True)


    def setColorsFromLib(self):
        f = CurrentFont()
        if f is None:
            return
        shapeColor = (1,1,1,0.5)
        backgroundColor = (0,0,0,1)
        if self.shapeColorLibKey in f.lib.keys():
            v = f.lib[self.shapeColorLibKey]
            if v is not None:
                shapeColor = v

        if self.backgroundColorLibKey in f.lib.keys():
            v = f.lib[self.backgroundColorLibKey]
            if v is not None:
                backgroundColor = v

        self.setShapeColor(shapeColor)
        self.setBackgroundColor(backgroundColor)

    def writeColorsToLib(self):
        f = CurrentFont()
        if f is None:
            return
        f.lib[self.shapeColorLibKey] = self.shapeColor
        f.lib[self.backgroundColorLibKey] = self.backgroundColor

    def setShapeColor(self, color):
        r, g, b, a = color
        self.shapeColor = color
        self.w.shapeColorWell.set(NSColor.colorWithDeviceRed_green_blue_alpha_(r, g, b, a))
        
    def setBackgroundColor(self, color):
        r, g, b, a = color
        self.backgroundColor = color
        self.w.backgroundColorWell.set(NSColor.colorWithDeviceRed_green_blue_alpha_(r, g, b, a))
        
    def update(self):
        # when starting, or when there is an update?
        f = CurrentFont()
        if f is None:
            return
        # update color from lib
        glyphs = self.wrapGlyphs()
        self.w.l.set(glyphs)
        folderName = self.proposeFilename(f)
        self.w.t.set(u"📦 %s"%folderName)
    
    def validate(self, font):
        # can we generate this one?
        # test.
        # do we have all the right names:
        for name in self.masterNames:
            if name not in font:
                #print 'missing glyph', name
                self.w.t.set("Glyph %s missing."%name)
                return False
        return True
        
    def wrapGlyphs(self):
        glyphs = []
        f = CurrentFont()
        if f is None:
            return
        names = f.keys()
        names.sort()
        layers = f.layerOrder
        if 'bounds' in layers:
            hasBounds = "yup"
        else:
            hasBounds = "nope"
        for n in names:
            if n in self.masterNames:
                status = True
            else:
                continue
            g = f[n]
            if hasBounds:
                gb = g.getLayer('bounds')
                if gb.box is None:
                    continue
                xMin, yMin, xMax, yMax = gb.box
                width = xMax-xMin
                height = yMax-yMin
            else:
                width = g.width
                height = None
            contours, points = self.countGlyph(g)
            d = dict(name=g.name,
                    width=width,
                    height=height,
                    bounds=hasBounds,
                    status=status,
                    contours=contours,
                    points=points,
                    )
            glyphs.append(d)
        return glyphs
    
    def countGlyph(self, glyph):
        # count the contours and the points
        contours = 0
        points = 0
        for c in glyph.contours:
            contours +=1
            for s in c.segments:
                for p in s.points:
                    points +=1
        return contours, points

    def shapeColorWellCallback(self, sender):
        # update the color from the colorwell
        clr = sender.get()
        red = clr.redComponent()
        grn = clr.greenComponent()
        blu = clr.blueComponent()
        alf = clr.alphaComponent()
        self.setShapeColor((red, grn, blu, alf))        # set the color in the well
        self.cbMakePreview(self)  # update the preview      

    def backgroundColorWellCallback(self, sender):
        # update the color from the colorwell
        clr = sender.get()
        red = clr.redComponent()
        grn = clr.greenComponent()
        blu = clr.blueComponent()
        alf = clr.alphaComponent()
        self.setBackgroundColor((red, grn, blu, alf))        # set the color in the well
        self.cbMakePreview(self)  # update the preview      
    
    def cbMakePreview(self, sender):
        # generate a preview
        self.w.preview.setHTMLPath(self.dump())

    def cbExport(self, sender):
        if not self.validate:
            # show error message
            self.w.t.set("Error, can't export.")
            return
        self.dump()
        self.writeColorsToLib()
        self.w.close()

    def dump(self):
        f = CurrentFont()
        if f is None:
            return
        proposedName = self.proposeFilename(f)
        # export the mathshape
        root, tags, metaData = exportCurrentFont(f, self.masterNames, proposedName, self.extrapolateMinValue, self.extrapolateMaxValue)
        outputPath = os.path.join(root, "preview_%s.html"%proposedName)
        resourcesPath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Resources")
        outputPath = os.path.join(root, "preview_%s.html"%proposedName)
        pm = PageMaker(resourcesPath, os.path.join(root, proposedName),
            outputPath,
            shapeColor= self.shapeColor,
            bgColor = self.backgroundColor
            )
        return outputPath
    
    def proposeFilename(self, exportFont):
        name = "%s%s_ms"%(exportFont.info.familyName, exportFont.info.styleName)
        name = name.lower()
        return name


def exportCurrentFont(exportFont, masterNames, folderName, extrapolateMin=0, extrapolateMax=1, saveFiles=True):
    tags = []       # the svg tags as they are produced
    exportFont.save()
    path = exportFont.path
    checkBoundsLayer = False
    if 'bounds' in exportFont.layerOrder:
        checkBoundsLayer = True
    root = os.path.dirname(exportFont.path)
    if saveFiles:
        # if we want to export to a real folder
        imagesFolder = os.path.join(root, folderName)
        jsonPath = os.path.join(imagesFolder, "files.json")
        if not os.path.exists(imagesFolder):
            os.makedirs(imagesFolder)

    allBounds = []
    for name in masterNames:
        g = exportFont[name]
        undo = False
        if len(g.components)>0:
            exportFont.prepareUndo(undoTitle="decompose_for_svg_export")
            g.decompose()
            undo = True
        # check the bounds layer for the bounds first
        bounds, tag = makeSVGShape(g, name=name)
        tags.append(tag)
        k = [bounds[2],bounds[3]]
        if k not in allBounds: allBounds.append(k)
        if saveFiles:
            filePath = os.path.join(imagesFolder, "%s.svg"%name)
            makeMaster(filePath, tag)
        if undo:
            exportFont.performUndo()

    metaData = dict(sizebounds=allBounds, files=[folderName+"/%s.svg"%n for n in masterNames])
    metaData['extrapolatemin']=extrapolateMin
    metaData['extrapolatemax']=extrapolateMax
    metaData['designspace']='twobytwo'
    if saveFiles:
        jsonFile = open(jsonPath, 'w')
        jsonFile.write(json.dumps(metaData))
        jsonFile.close()
    return root, tags, metaData

ExportUI()