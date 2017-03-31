import os
from designSpaceDocument import DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor

class VariableFontExporter(object):
    designSpaceModelLibKey = "com.letterror.mathshape.designspace"
    shapeColorLibKey = "com.letterror.mathshape.preview.shapecolor"
    backgroundColorLibKey = "com.letterror.mathshape.preview.bgcolor"
    preferredFilenameLibKey = "com.letterror.mathshape.filename"
    animatingModels = ["twobytwo"]

    def __init__(self, font):
        self.font = font
        self.designSpaceModel = self.font.lib.get(self.designSpaceModelLibKey, "twobytwo")
        #if self.designSpaceModel is None:
        #    print("This font is probably not a Responsive Lettering project?")
        #    return
        if self.designSpaceModel == "twobytwo":
            self.masterNames = ['narrow-thin', 'wide-thin', 'narrow-bold', 'wide-bold']
            self.fontNames = {'narrow-thin':'NarrowThin', 'wide-thin':'WideThin', 'narrow-bold':'NarrowBold', 'wide-bold':'WideBold'}
            self.axes = ['width', 'weight']
            self.locations = {'narrow-thin': dict(weight=0, width=0), 'wide-thin': dict(width=1000, weight=0), 'narrow-bold': dict(width=0, weight=1000), 'wide-bold': dict(width=1000, weight=1000)}
        elif self.designSpaceModel == "twobyone":
            self.masterNames = ['narrow-thin', 'wide-thin']
            self.fontNames = {'narrow-thin':'NarrowThin', 'wide-thin':'WideThin'}
            self.axes = ['width']
            self.locations = {'narrow-thin': dict(weight=0), 'wide-thin': dict(weight=1000)}
        elif self.designSpaceModel == "threebyone":
            self.masterNames = ['narrow-thin', 'wide-thin', 'medium-thin']
            self.fontNames = {'narrow-thin':'NarrowThin', 'wide-thin':'WideThin', 'medium-thin':'MediumThin'}
            self.axes = ['width']
            self.locations = {'narrow-thin': dict(weight=0), 'medium-thin': dict(weight=500), 'wide-thin': dict(weight=1000)}
        
        projectRoot = os.path.join(os.path.dirname(self.font.path), "%s_variableFont"%self.font.info.styleName)
        docPath = os.path.join(projectRoot, "%s_variableFont.designspace"%self.font.info.styleName)
        if not os.path.exists(projectRoot):
            os.makedirs(projectRoot)

        widthMinimum = self.font['narrow-thin'].width
        widthMaximum = self.font['wide-thin'].width
        for k, v in self.locations.items():
            new = {}
            for axisName, axisValue in v.items():
                if axisName == "width":
                    if axisValue == 1000:
                        new[axisName] = widthMaximum
                    elif axisValue == 0:
                        new[axisName] = widthMinimum
                else:
                    new[axisName] = axisValue
            self.locations[k] = new

        doc = DesignSpaceDocument()
        for name in self.axes:
            if name == "width":
                a = AxisDescriptor()
                a.minimum = widthMinimum
                a.maximum = widthMaximum
                a.default = widthMinimum
                a.name = "width"
                a.tag = "wdth"
                #a.labelNames['en'] = "Width"
                doc.addAxis(a)
            elif name == "weight":
                a = AxisDescriptor()
                a.minimum = 0
                a.maximum = 1000
                a.default = 0
                a.name = "weight"
                a.tag = "wght"
                #a.labelNames['en'] = "Weight"
                doc.addAxis(a)
                
        
        print "projectRoot", projectRoot
        
        masterCount = 0
        for name in self.masterNames:
            if name in self.font:
                masterCount += 1
        if masterCount != len(self.masterNames):
            print "missing glyphs, can't generate"
            return
        closers = []
        for name in self.masterNames:
            print "processing", name, self.locations[name]
            m = RFont()
            m.info.unitsPerEm = self.font.info.unitsPerEm
            m.info.ascender = self.font.info.ascender
            m.info.descender = self.font.info.descender
            if self.font.info.familyName in ["MathShape", "Responsive"]:
                m.info.familyName = self.font.info.styleName
            else:
                m.info.familyName = "ResponsiveLettering"
            m.info.styleName = self.fontNames[name]
            m.info.copyright = "Generated from Responsive Lettering project %s"%(os.path.basename(self.font.path))
            m.info.openTypeNameSampleText = "A"            
            fontPath = os.path.join(projectRoot, "master_%s.ufo"%(m.info.styleName))
            instancePath = os.path.join(projectRoot, "instance_%s%s.ufo"%(m.info.familyName, m.info.styleName))
            m.save(fontPath)

            m.newGlyph("A")
            g = m['A']
            pen = g.getPointPen()
            self.font[name].drawPoints(pen)
            #g.appendGlyph(self.font[name])
            g.width = self.font[name].width
            g.clearImage()
            g.update()
            m.save()
            
            m.newGlyph("space")
            g = m['space']
            g.clearImage()
            g.width = self.font[name].width
            #g.note = "test"
            #g.appendGlyph(self.font[name])
            m.newGlyph(".notdef")
            g = m['.notdef']
            g.clearImage()
            g.width = self.font[name].width
            #g.note = "test"
            g.update()
            m.save()

            s = SourceDescriptor()
            s.path = fontPath
            s.location = self.locations[name]
            if name == 'narrow-thin':
                s.copyLib = True
                s.copyInfo = True
                
            doc.addSource(s)
            # add some instances
            i = InstanceDescriptor()
            i.path = instancePath
            i.location = self.locations[name]
            i.copyLib = True
            i.copyInfo = True
            i.copyFeatures = True
            i.familyName = "ResponsiveLetteringVariable"
            i.styleName = m.info.styleName
            #i.kerning = True
            doc.addInstance(i)
            closers.append(m)
        doc.write(docPath)
        for m in closers:
            m.save()
            m.close()

f = CurrentFont()
d = VariableFontExporter(f)
