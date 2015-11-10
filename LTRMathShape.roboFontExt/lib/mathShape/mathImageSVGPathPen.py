from fontTools.pens.basePen import BasePen
from ufo2svg.tools import pointToString, valueToString


"""
    Almost indentical to the pen in ufo2svg, except 
    that this one does not optimise horizontal or 
    vertical line segments. All lines are written with
    x and y components. Otherwise differences in shape
    between the masters could cause incompatibilities.
"""

class MathImageSVGPathPen(BasePen):

    def __init__(self, glyphSet, optimise=False):
        BasePen.__init__(self, glyphSet)
        self._commands = []
        self._lastCommand = None
        self._lastX = None
        self._lastY = None
        self.optimise = optimise

    def _handleAnchor(self):
        """
        >>> pen = MathImageSVGPathPen(None)
        >>> pen.moveTo((0, 0))
        >>> pen.moveTo((10, 10))
        >>> pen._commands
        ['M10 10']
        """
        if self._lastCommand == "M":
            self._commands.pop(-1)

    def _moveTo(self, pt):
        """
        >>> pen = MathImageSVGPathPen(None)
        >>> pen.moveTo((0, 0))
        >>> pen._commands
        ['M0 0']

        >>> pen = MathImageSVGPathPen(None)
        >>> pen.moveTo((10, 0))
        >>> pen._commands
        ['M10 0']

        >>> pen = MathImageSVGPathPen(None)
        >>> pen.moveTo((0, 10))
        >>> pen._commands
        ['M0 10']
        """
        self._handleAnchor()
        t = "M%s" % (pointToString(pt))
        self._commands.append(t)
        self._lastCommand = "M"
        self._lastX, self._lastY = pt

    def _lineTo(self, pt):
        """
        # duplicate point
        >>> pen = MathImageSVGPathPen(None)
        >>> pen.moveTo((10, 10))
        >>> pen.lineTo((10, 10))
        >>> pen._commands
        ['M10 10']

        # vertical line
        >>> pen = MathImageSVGPathPen(None)
        >>> pen.moveTo((10, 10))
        >>> pen.lineTo((10, 0))
        >>> pen._commands
        ['M10 10', 'V0']

        # horizontal line
        >>> pen = MathImageSVGPathPen(None)
        >>> pen.moveTo((10, 10))
        >>> pen.lineTo((0, 10))
        >>> pen._commands
        ['M10 10', 'H0']

        # basic
        >>> pen = MathImageSVGPathPen(None)
        >>> pen.lineTo((70, 80))
        >>> pen._commands
        ['L70 80']

        # basic following a moveto
        >>> pen = MathImageSVGPathPen(None)
        >>> pen.moveTo((0, 0))
        >>> pen.lineTo((10, 10))
        >>> pen._commands
        ['M0 0', ' 10 10']
        """
        x, y = pt
        if not self.optimise:
            cmd = "L"
            pts = pointToString(pt)
        else:
            # duplicate point
            if x == self._lastX and y == self._lastY:
                return
            # vertical line
            elif x == self._lastX:
                cmd = "V"
                pts = valueToString(y)
            # horizontal line
            elif y == self._lastY:
                cmd = "H"
                pts = valueToString(x)
            # previous was a moveto
            elif self._lastCommand == "M":
                cmd = None
                pts = " " + pointToString(pt)
            # basic
            else:
                cmd = "L"
                pts = pointToString(pt)
        # write the string
        t = ""
        if cmd:
            t += cmd
            self._lastCommand = cmd
        t += pts
        self._commands.append(t)
        # store for future reference
        self._lastX, self._lastY = pt

    def _curveToOne(self, pt1, pt2, pt3):
        """
        >>> pen = MathImageSVGPathPen(None)
        >>> pen.curveTo((10, 20), (30, 40), (50, 60))
        >>> pen._commands
        ['C10 20 30 40 50 60']
        """
        t = "C"
        t += pointToString(pt1) + " "
        t += pointToString(pt2) + " "
        t += pointToString(pt3)
        self._commands.append(t)
        self._lastCommand = "C"
        self._lastX, self._lastY = pt3

    def _qCurveToOne(self, pt1, pt2):
        """
        >>> pen = MathImageSVGPathPen(None)
        >>> pen.qCurveTo((10, 20), (30, 40))
        >>> pen._commands
        ['Q10 20 30 40']
        """
        assert pt2 is not None
        t = "Q"
        t += pointToString(pt1) + " "
        t += pointToString(pt2)
        self._commands.append(t)
        self._lastCommand = "Q"
        self._lastX, self._lastY = pt2

    def _closePath(self):
        """
        >>> pen = MathImageSVGPathPen(None)
        >>> pen.closePath()
        >>> pen._commands
        ['Z']
        """
        self._commands.append("Z")
        self._lastCommand = "Z"
        self._lastX = self._lastY = None

    def _endPath(self):
        """
        >>> pen = MathImageSVGPathPen(None)
        >>> pen.endPath()
        >>> pen._commands
        ['Z']
        """
        self._closePath()
        self._lastCommand = None
        self._lastX = self._lastY = None

    def getCommands(self):
        return "".join(self._commands)


if __name__ == "__main__":
    import doctest
    doctest.testmod()