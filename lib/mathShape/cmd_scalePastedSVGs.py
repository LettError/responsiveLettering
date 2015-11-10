

"""
    paste a bunch of SVGs into a UFO and then scale and position the outlines.

"""
f = CurrentFont()


def scaleSVGToBounds(g):
    wantHeight = 750
    box = g.box
    if box is None:
        return
    xMin, yMin, xMax, yMax = g.box
    ratio = (xMax-xMin)/(yMax-yMin)
    g.move((-xMin, -yMin))
    s = wantHeight/(yMax-yMin)
    g.scale((s,s))
    g.round()
    g.rightMargin = 0

for g in f:
    scaleSVGToBounds(g)