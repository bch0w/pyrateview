"""
Wrappers for commonly used ParaView objects
"""
from paraview.simple import (Ruler, GetActiveView, Hide3DWidgets, Show, Text,
                             PointSource, Glyph, OpenDataFile, ColorBy, Hide,
                             ProgrammableFilter, GetActiveViewOrCreate)
from matplotlib.colors import to_rgb


def ruler(start, end, label="", graduation=None, ticknum=None,
          axis_color="k", font_color="k", justification="Left",
          reg_name="ruler", line_width=3., fontsize=12):
    """
    Generate a ruler to be used as a scalebar

    :type start: list of float
    :param start: [x0, y0, z0] starting point of the ruler
    :type end: list of float
    :param end: [x, y, z] ending point of the ruler
    :type label: str
    :param label: text label that will be annotated at the midpoint of the ruler
    :type ticknum: int
    :param ticknum: number of individual ticks to place on the ruler
    :type axis_color: str
    :param axis_color: color to make the ruler, in python color values, e.g. 'k'
    :type font_color: str
    :param axis_color: color to make the label, in python color values, e.g. 'k'
    :type reg_name: str
    :param reg_name: Name to register the ruler, useful for deleting the
        ruler afterwards using e.g. FindSource
    :type justification: str
    :param justification: text justification for 'label'
    :rtype: Ruler
    :return: the created ruler object
    """
    ruler = Ruler(registrationName=reg_name)
    ruler.Point1 = start
    ruler.Point2 = end
    rulerDisplay = Show(ruler, GetActiveView(), "RulerSourceRepresentation")
    rulerDisplay.LabelFormat = label

    assert(graduation is not None or ticknum is not None), \
        "Ruler requires graduation or ticknum"

    # Tick number can either be set by an integer
    if ticknum:
        rulerDisplay.NumberOfTicks = ticknum
    # Or by the graduation between each tick
    else:
        rulerDisplay.RulerMode = 1
        rulerDisplay.Graduation = graduation
    rulerDisplay.AxisColor = axis_color
    rulerDisplay.Color = to_rgb(font_color)
    rulerDisplay.FontSize = fontsize
    rulerDisplay.AxisLineWidth = line_width
    rulerDisplay.Justification = justification.title()

    Hide3DWidgets(proxy=ruler)

    return ruler, rulerDisplay


def text(s, position, fontsize=12, color="k", bold=False,
         justification="center", reg_name="text"):
    """
    Create and show a text object at a given position

    :type position: list of float
    :param position: [x, y] where x and y are in percentage of the viewing
        window, e.g. [0.5, 0.5] places text in the middle of the screen
    :type fontsize: float
    :param fontsize: fontsize of the text to create, defaults to the fontsize
        constant defined at the top of the script
    :type color: list of float
    :param color: RGB color of the text, defaults to the constant color defined
        at top of the file
    :type bold: bool
    :param bold: if True, boldfaces the text
    :type reg_name: str
    :param reg_name: Name to register the ruler, useful for deleting the
        ruler afterwards using e.g. FindSource
    :type justification: str
    :param justification: text justification, 'left', 'right', 'center'
    :rtype: tuple
    :return: (text object created, rendered view of the text object)
    """
    text = Text(registrationName=reg_name)
    text.Text = s
    textDisplay = Show(text, GetActiveView())
    textDisplay.Position = position
    textDisplay.Bold = int(bold)
    textDisplay.FontSize = fontsize
    textDisplay.Color = to_rgb(color)
    textDisplay.Justification = justification.title()

    return text, textDisplay


def point_source(origin, reg_name="point"):
    """
    Create a point source at a given origin. Used mainly for deriving glyphs

    :type origin: list of float
    :param origin: origin point in [x, y, z]
    :type reg_name: str
    :param reg_name: name of the created object
    """
    point = PointSource(registrationName=reg_name)
    point.Center = origin

    return point


def glyphs(origin, type, twod=None, size=3., linewidth=2., rotate=[0., 0., 0.,],
          show="All Points", filled=1, opacity=1, position=[0., 0., 0.,],
          color="k", representation_type="Surface With Edges",
          reg_name="glyph"):
    """
    Create a glyph (marker) at a given origin point

    :type origin: list of float
    :param origin: origin point in [x, y, z]
    :type type: str
    :param type: type of glyph to make, available are:
        Arrow, Cone, Box, Cylinder, Line, Sphere, 2D Glyph
    :type twod: str
    :param twod; if type=='2D Glyph', choose the 2D marker, available are:
        Vertex, Dash, Cross, ThickCross, Triangle, Square, Circle, Diamond,
        Arrow, ThickArrow, HookedArrow, EdgeArrow

    :type reg_name: str
    :param reg_name: name of the created object
    """
    # Make a Glyph from a single point
    if isinstance(origin ,list):
        input = point_source(origin)
    # Or open from a data file
    elif isinstance(origin, str):
        input = OpenDataFile(origin)

    # Generate the underlying glyph
    glyph = Glyph(Input=input, GlyphType=type, registrationName=reg_name)
    if type == "2D Glyph":
        glyph.GlyphType.GlyphType = twod
    glyph.ScaleArray = ["POINTS", "No scale array"]
    glyph.ScaleFactor = size
    glyph.GlyphMode = show
    glyph.GlyphTransform.Rotate = rotate
    glyph.GlyphType.Filled = filled

    # Now display the glyph we just made
    glyphDisplay = Show(glyph, GetActiveView(), "GeometryRepresentation")
    glyphDisplay.PointSize = size
    glyphDisplay.SetRepresentationType(representation_type)
    glyphDisplay.LineWidth = linewidth
    glyphDisplay.Opacity = opacity
    glyphDisplay.Position = position
    glyphDisplay.AmbientColor = to_rgb(color)
    glyphDisplay.DiffuseColor = to_rgb(color)


def programmable_filter(data, script, reg_name="ProgrammableFilter"):
    """
    Create a programmable filter, which allows you to input Python script and
    e.g. scale coordinates or units of an open data file

    :type data: ParaView datatype
    :param data: An open VTK file or slice or whatever
    :type script: str
    :param script: python script to input into programmable filter
    :return:
    """
    # Need to make sure data is showing otherwise prog filter throws a fit
    renderView = GetActiveViewOrCreate("RenderView")
    Show(data)

    prog_filter = ProgrammableFilter(registrationName=reg_name, Input=data)
    prog_filter.Script = script
    qty = prog_filter.PointData.GetArray(0).Name
    progfiltDisplay = Show(prog_filter, GetActiveView(),
                           "UnstructuredGridRepresentation")
    ColorBy(progfiltDisplay, qty)
    Hide(data)
    Hide(prog_filter)

    return prog_filter


def point_cloud(fid, point_size=2., color=None, opacity=1., xmin=None,
                xmax=None, ymin=None, ymax=None):
    """
    Plot a point cloud from a .vtk file. Use for plotting earthquake sources,
    receivers, or things like coastline files that are not meshes but
    just collections of points.

    :param fid:
    :param point_size:
    :param color:
    :param opacity:
    :param xmin:
    :param xmax:
    :param ymin:
    :param ymax:
    :return:
    """