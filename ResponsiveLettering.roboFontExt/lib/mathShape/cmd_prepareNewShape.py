import vanilla
from mojo.canvas import Canvas
from AppKit import NSNumberFormatter
from defconAppKit.windows.baseWindow import BaseWindowController

"""

    Make a new UFO and give it the appropriate glyphs and layers.
    
"""
import os, time

designSpaceModelLibKey = "com.letterror.mathshape.designspace"

def prepareMathShapeUFO(narrow=500, wide=2500, upm=1000, familyName="MathShape", styleName="New", model="twobytwo"):
    f = NewFont(familyName=familyName, styleName=styleName)
    f.info.note = "This is a template font for a Responsive Lettering project, using a %s designspace. The font names and glyph widths can all tbe changed."%model
    f.info.unitsPerEm = upm
    f.info.ascender = .75*upm
    f.info.descender = -.25*upm
    f.lib[designSpaceModelLibKey] = model
    if model == "twobytwo":
        glyphs = [
            ('narrow-thin', narrow),
            ('wide-thin', wide),
            ('narrow-bold',narrow),
            ('wide-bold', wide),
            ]
    elif model == "twobyone":
        glyphs = [
            ('narrow-thin', narrow),
            ('wide-thin', wide),
            ]
    names = [a for a, b in glyphs]
    f.lib['public.glyphOrder'] = names
    # draw bounds layer
    asc = f.info.ascender
    dsc = f.info.descender
    for name, width in glyphs:
        f.newGlyph(name)
        g = f[name]
        g.width = width
        boundsGlyph = g.getLayer('bounds', clear=True)
        pen = boundsGlyph.getPen()
        pen.moveTo((0,dsc))
        pen.lineTo((g.width,dsc))
        pen.lineTo((g.width,asc))
        pen.lineTo((0,asc))
        pen.closePath()
        g.update()
    # draw some sort of intro / test shape?
    thin = 5
    thick = 100
    for g in f:
        w = g.width
        if g.name.find("thin")!=-1:
            thin = 5
        else:
            thin = 100  
        pen = g.getPen()
        pen.moveTo((0,dsc))
        pen.lineTo((thin, dsc))
        pen.lineTo((w, asc-thin))
        pen.lineTo((w, asc))
        pen.lineTo((w-thin,asc))
        pen.lineTo((0,dsc+thin))
        pen.closePath()
        pen.moveTo((0,asc))
        pen.lineTo((0,asc-thin))
        pen.lineTo((w-thin,dsc))
        pen.lineTo((w,dsc))
        pen.lineTo((w,dsc+thin))
        pen.lineTo((thin,asc))
        pen.closePath()
    return f    # handle the saving in the UI

class NewMathShapePicker(BaseWindowController):
    windowWidth = 250
    windowHeight = 230
    def __init__(self):
        self.fontObject = None
        self.size = 50
        proposedStyleName = time.strftime("%Y%m%d", time.localtime())

        upmFormatter = NSNumberFormatter.alloc().init()
        upmFormatter.setPositiveFormat_("#")
        upmFormatter.setAllowsFloats_(False)
        upmFormatter.setMinimum_(500)
        upmFormatter.setMaximum_(10000)

        narrowFormatter = NSNumberFormatter.alloc().init()
        narrowFormatter.setPositiveFormat_("#")
        narrowFormatter.setAllowsFloats_(False)
        narrowFormatter.setMinimum_(10)
        narrowFormatter.setMaximum_(10000)

        wideFormatter = NSNumberFormatter.alloc().init()
        wideFormatter.setPositiveFormat_("#")
        wideFormatter.setAllowsFloats_(False)
        wideFormatter.setMinimum_(10)
        wideFormatter.setMaximum_(10000)
        
        self.designSpaceOptions = [("Responsive + animation (4 masters)", "twobytwo"), ("Only responsive (2 masters)", "twobyone")]

        self.w = vanilla.Window((self.windowWidth, self.windowHeight), "New MathShape UFO", textured=False)
        self.w.cancel = vanilla.Button((10, -30, 100, 20), "Cancel", callback=self.cancelCallback)
        self.w.ok = vanilla.Button((-110, -30, 101, 20), "Make", callback=self.makeCallback)
        self.w.setDefaultButton(self.w.ok)
        valueColumn = 140
        cpOffset = 4
        self.w.narrowValue = vanilla.EditText((valueColumn, 10, -10, 20), 500, formatter=narrowFormatter, sizeStyle="small")
        self.w.narrowValueCp = vanilla.TextBox((10, 10+cpOffset, 100, 20), "Narrowest width", sizeStyle="small")
        self.w.wideValue = vanilla.EditText((valueColumn, 40, -10, 20), 2500, formatter=wideFormatter, sizeStyle="small")
        self.w.wideValueCp = vanilla.TextBox((10, 40+cpOffset, 100, 20), "Widest width", sizeStyle="small")
        self.w.upmValue = vanilla.EditText((valueColumn, 70, -10, 20), 1000, formatter=upmFormatter, sizeStyle="small")
        self.w.upmValueCp = vanilla.TextBox((10, 70+cpOffset, 100, 20), "Units per Em", sizeStyle="small")
        
        self.w.familyNameString = vanilla.EditText((valueColumn, 100, -10, 20), "Responsive", sizeStyle="small")
        self.w.familyNameStringCp = vanilla.TextBox((10, 100+cpOffset, 100, 20), "Familyname", sizeStyle="small")
        self.w.styleNameString = vanilla.EditText((valueColumn, 130, -10, 20), proposedStyleName, sizeStyle="small")
        self.w.styleNameStringCp = vanilla.TextBox((10, 130+cpOffset, 100, 20), "Stylename", sizeStyle="small")
        self.w.modelPopup = vanilla.PopUpButton((10, 160, -10, 20), [a for a,b in self.designSpaceOptions], sizeStyle="small")
        self.setUpBaseWindowBehavior()
        self.w.open()

    def makeCallback(self, sender):
        upm = int(self.w.upmValue.get())
        narrowWidth = int(self.w.narrowValue.get())
        wideWidth = int(self.w.wideValue.get())
        fName = self.w.familyNameString.get()
        sName = self.w.styleNameString.get()
        designSpaceModel = self.designSpaceOptions[self.w.modelPopup.get()][1]
        self.fontObject = prepareMathShapeUFO(narrow=narrowWidth,
            wide=wideWidth,
            upm=upm,
            familyName=fName,
            styleName=sName,
            model=designSpaceModel)
        preferredName = "%s-%s.ufo"%(self.fontObject.info.familyName, self.fontObject.info.styleName) 
        self.showPutFile(["ufo"], fileName=preferredName, callback=self._saveFile)

    def _saveFile(self, path):
        if self.fontObject is not None:
            for g in self.fontObject:
                g.update()
            self.fontObject.save(path)
        self.w.close()
        
    def cancelCallback(self, sender):
        print 'cancelling'
        self.w.close()
        

nmsp = NewMathShapePicker()

