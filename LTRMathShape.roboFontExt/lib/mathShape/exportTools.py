import os
from fontTools.pens.basePen import BasePen
#from robofab.world import OpenFont, RFont
from robofab.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

import json
from mathImageSVGPathPen import MathImageSVGPathPen

def makeMaster(filePath, svg):
	docType = """<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">"""
	f = open(filePath, 'w')
	# print filePath
	f.write(docType+svg)
	f.close()

def makeSVGShape(glyph, name=None, width=None, opacity=None):
    attrs = {
        'id': 'mathShape',
        'title': "None",
        'xmlns': "http://www.w3.org/2000/svg",
        'xmlns:xlink' : "http://www.w3.org/1999/xlink",
        'xml:space':'preserve',
        'style': "fill-rule:nonzero;clip-rule:evenodd;stroke-linejoin:round;stroke-miterlimit:1.41421;",
    }
    # try to get the bounds from the bounds layer.
    # if that does not work, get it from the glyph itself.
    bounds = None
    try:
        boundsGlyph = glyph.getLayer('bounds')
        if boundsGlyph is not None:
            bounds = boundsGlyph.box
            # print 'using bounds from bounds layer'
    except:
        pass
        # print 'using bounds from glyph'
    if bounds is None:
        boundsPen = BoundsPen({})
        glyph.draw(boundsPen)
        bounds = boundsPen.bounds

    xOffset = 0
    yOffset = 0
    attrs['id']= name;
    if width is None:
        attrs['width'] = "100%"
    else:
        attrs['width'] = width
    if name is not None:
        attrs['name'] = name
    else:
        attrs['name'] = glyph.name
    if opacity is not None:
        attrs['fill-opacity'] = "%3.3f"%opacity


    t = Transform()
    # print bounds, -(bounds[3]-bounds[1])
    t = t.scale(1,-1)
    t = t.translate(0, -bounds[3])
    vb = (0, 0, glyph.width, bounds[3]-bounds[1])
    attrs['viewBox'] = "%3.3f %3.3f %3.3f %3.3f"%(vb[0],vb[1],vb[2],vb[3])
    attrs['enable-background']  = attrs['viewBox'] 
    sPen = MathImageSVGPathPen({})
    tPen = TransformPen(sPen, t)
    glyph.draw(tPen)
    path = "<path d=\"%s\"/>"%(sPen.getCommands())
    tag = "<svg %s>%s</svg>"%(" ".join(["%s=\"%s\""%(k,v) for k, v in attrs.items()]), path)
    return vb, tag

