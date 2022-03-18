"""
Utility functions to assist in the package, like unit converters, or trig
calculators for finding angles
"""
import math
from subprocess import call
from paraview.simple import Hide, Show, GetActiveView, ColorBy
from things import programmable_filter


def myround(x, base, choice=None):
    """
    Round values to the nearest base

    :type x: float
    :param x: value to round
    :type base: int
    :param base: nearest number to round to
    :type choice: str
    :param choice: 'up' to round up, 'down' to round down, or None for nearest
    """
    if choice == "up":
        fx = math.ceil
    elif choice == "down":
        fx = math.floor
    else:
        fx = round
    return int(base * fx(float(x) / base))

def normal_to_angle(x, y):
    """
    Take two normal vectors and return the angle that they give.

    :type x: float
    :param x: x normal
    :type y: float
    :param y: y normal
    :rtype: float
    :return: angle created by the two normals
    """
    return math.atan2(y, x) * 180 / math.pi


def translate_point(data, x0=0, y0=0, z0=0, scale=1):
    """
    Translate a point [x, y, z] by some vector [x0, y0, z0], and simulataneously
    allow for conversion. Used in the NZ problem to convert the origin from
    some arbitrary value in UTM60S to [0, 0, 0], and also convert untits from
    m to km
    (171312, 5286950)
    """
    return [(data[0] - x0) * scale,
            (data[1] - y0) * scale,
            (data[2] - z0) * scale]


def remove_whitespace(fid):
    """
    Use Imagemagick to remove any whitespace from a .png file
    Note: Requires Imagemagick!
    """
    call([f"convert {fid} -fuzz 1% -trim +repage {fid}"], shell=True)


def project_point_to_plane(point, origin, normal):
    """
    Project a point onto a plane. Used, e.g. to mark a city on a 2D cross
    section when the city doesn't exactly fall on the plane, need to know its
    relative position on the plane. I don't feel like doing the hard math so
    we assume that the plane has normal z component 0 so its not canted.

    http://www.nabla.hr/CG-LinesPlanesIn3DB5.htm
    """
    pass


def scale_input(data, scale_data=None, scale_coords=None, zero_origin=False):
    """
    Scale the data units and coordinates of an open data file using the
    Programmable Filter

    :param data:
    :param scale:
    :return:
    """
    # Set some default values incase NoneType passed in for scaling
    if scale_data is None:
        scale_data = 1
    if scale_coords is None:
        scale_coords = 1

    script = f"""from paraview import vtk
pdi = self.GetInput()
pdo = self.GetOutput()

numPoints = pdi.GetNumberOfPoints()
newPoints = vtk.vtkPoints()
min_x, _, min_y, _, _, _ = pdi.GetBounds()
for i in range(0, numPoints):
    coords = pdi.GetPoint(i)
    x, y, z = coords[:3]
    if {zero_origin}:
        x -= min_x
        y -= min_y

    # Convert to units of km
    if {scale_coords}:
        x *= {scale_coords}
        y *= {scale_coords}
        z *= {scale_coords}
    newPoints.InsertPoint(i, x, y, z)

# Set the new coordinate system
pdo.SetPoints(newPoints)

# Create a new array that will hold the converted values
ivals = pdi.GetPointData().GetScalars()

ca = vtk.vtkFloatArray()
ca.SetName(ivals.GetName())
ca.SetNumberOfComponents(1)
ca.SetNumberOfTuples(numPoints)

# Copy the values over element by element and convert
for i in range(0, numPoints):
  ca.SetValue(i, ivals.GetValue(i) * {scale_data})

# Set the new values
pdo.GetPointData().AddArray(ca)"""

    return programmable_filter(data, script)
