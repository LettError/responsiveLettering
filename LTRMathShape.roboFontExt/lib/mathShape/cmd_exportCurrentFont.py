
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
    masterNames = ['narrow-thin', 'wide-thin', 'narrow-bold', 'wide-bold']
    def __init__(self):
        self.color = "#FFF"
        self.w = vanilla.Window((500, 600), "MathShape Exporter", minSize=(300,200))
        self.w.preview = HTMLView((0,0,-0, -200))
        self.w.exportButton = vanilla.Button((-150, -30, -10, 20), "Export", callback=self.cbExport)
        self.w.previewButton = vanilla.Button((10, -30, -160, 20), "Preview", callback=self.cbMakePreview)
        
        valueWidth = 50
        columnDescriptions = [
            dict(title="Glyphname", key="name", width=100),
            dict(title="Width", key="width"),
            dict(title="Bounds", key="bounds", width=100),
        ]
        self.w.l = vanilla.List((0,-200,-0,-60), self.wrapGlyphs(), columnDescriptions=columnDescriptions)
        self.w.t = vanilla.TextBox((40,-53,-5,20), "FontName", sizeStyle="small")
        self.w.clr = vanilla.ColorWell((10,-55, 20, 20), callback=self.cbColor, color=NSColor.whiteColor())
        self.update()
        self.w.open()
        self.cbMakePreview(None)
    
    def update(self):
        # when starting, or when there is an update?
        f = CurrentFont()
        glyphs = self.wrapGlyphs()
        self.w.l.set(glyphs)
        folderName = self.proposeFilename(f)
        self.w.t.set(folderName)
    
    def validate(self, font):
        # can we generate this one?
        # test.
        # do we have all the right names:
        for name in self.masterNames:
            if name not in font:
                print 'missing glyph', name
                self.w.t.set("Glyph %s missing."%name)
                return False
        return True
        
    def wrapGlyphs(self):
        f = CurrentFont()
        glyphs = []
        names = f.keys()
        names.sort()
        layers = f.layerOrder
        if 'bounds' in layers:
            hasBounds = True
        else:
            hasBounds = False            
        for n in names:
            if n in self.masterNames:
                status = True
            else:
                continue
            g = f[n]
            g.getLayer
            d = dict(name=g.name,width=g.width,bounds=hasBounds,status=status)
            glyphs.append(d)
        return glyphs
    
    def cbColor(self, sender):
        clr = sender.get()
        red = clr.redComponent()*0xff
        grn = clr.greenComponent()*0xff
        blu = clr.blueComponent()*0xff
        self.color = "#%x%x%x"%(red,grn,blu)
        self.cbMakePreview(self)
        
    def cbMakePreview(self, sender):
        # generate a preview
        f = CurrentFont()
        proposedName = self.proposeFilename(f)
        # export the mathshape
        root, tags, metaData = exportCurrentFont(f, self.masterNames, proposedName)
        resourcesPath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Resources")
        outputPath = os.path.join(root, "preview_%s.html"%proposedName)
        pm = PageMaker(resourcesPath, os.path.join(root, proposedName), outputPath, fillColor=self.color)
        self.w.preview.setHTMLPath(outputPath)

    def cbExport(self, sender):
        if not self.validate:
            # show error message
            print 'error'
            return
        f = CurrentFont()
        proposedName = self.proposeFilename(f)
        # export the mathshape
        root, tags, metaData = exportCurrentFont(f, self.masterNames, proposedName)
        resourcesPath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Resources")
        outputPath = os.path.join(root, "test_%s.html"%proposedName)
        pm = PageMaker(resourcesPath, os.path.join(root, proposedName), outputPath, fillColor=self.color)
        self.w.close()
    
    def proposeFilename(self, exportFont):
        name = "%s%s_ms"%(exportFont.info.familyName, exportFont.info.styleName)
        name = name.lower()
        return name


def exportCurrentFont(exportFont, masterNames, folderName, saveFiles=True):
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
    metaData['extrapolatemin']=0
    metaData['extrapolatemax']=1.25
    metaData['designspace']='twobytwo'
    if saveFiles:
        jsonFile = open(jsonPath, 'w')
        jsonFile.write(json.dumps(metaData))
        jsonFile.close()
    return root, tags, metaData

ExportUI()