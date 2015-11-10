
"""

    Make a new UFO and give it the appropriate glyphs and layers.
    
"""
import os, time

def prepareMathShapeUFO(narrow=500, wide=2500):
    styleName = time.strftime("%Y%m%d", time.localtime())
    f = NewFont(familyName="MathShape", styleName=styleName)
    f.info.note = "This is a template font for a MathShape. The font names and glyph widths can all tbe changed."
    glyphs = [
        ('narrow-thin', narrow),
        ('wide-thin', wide),
        ('narrow-bold',narrow),
        ('wide-bold', wide),
        ]
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
        
    
prepareMathShapeUFO()