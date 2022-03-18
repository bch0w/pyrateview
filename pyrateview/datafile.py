"""
Class to control an open data file, e.g. a model .vtk file that needs to be
plotted. The idea is that only one main file should be open at a time with
PirateView, with which you can make depth slices, cross sections, etc.
"""
from paraview.simple import (OpenDataFile, servermanager, Slice, Hide3DWidgets,
                             Hide, Show, GetActiveView,
                             AVSUCDReader, GetColorTransferFunction,
                             GetOpacityTransferFunction)
from utils import scale_input


class CartesianDataFile():
    """
    An opened data file
    """
    def __init__(self, fid, scale_data=None, scale_coords=None,
                 zero_origin=False):
        """
        Open the data file and get some initial information
        """
        self.fid = fid
        self.data = OpenDataFile(fid)

        if scale_data or scale_coords:
            self.data = scale_input(data=self.data, scale_data=scale_data,
                                    scale_coords=scale_coords,
                                    zero_origin=zero_origin)

        self.data_coords = self._get_coordinates()
        self.data_bounds = self._get_data_minmax()
        self.display = Show(self.data, GetActiveView(),
                            "UnstructuredGridRepresentation")

    def _get_coordinates(self, input=None):
        """
        Retrieve the X, Y, Z coordinates from the data file, always useful
        to know the bounds of the data file, e.g. to plot mins and maxes
        """
        if input is None:
            input = self.data
        data_plane = servermanager.Fetch(input)
        x, y, z = [], [], []
        for i in range(data_plane.GetNumberOfPoints()):
            x_, y_, z_ = data_plane.GetPoint(i)
            x.append(x_)
            y.append(y_)
            z.append(z_)

        return x, y, z

    def _get_data_minmax(self, input=None):
        """
        Get the min and max range of the data

        :rtype: tuple
        :return: (data_min, data_max)
        """
        if input is None:
            input = self.data
        vmin, vmax = input.PointData.GetArray(0).GetRange(0)
        return vmin, vmax

    @property
    def stats(self):
        """
        Print stats about the current data file
        """
        for i, coord in enumerate(self.data_coords):
            print(f"{i} [min, max, n]: "
                  f"{min(coord)}, {max(coord)}, {len(coord)}")
        print(f"vals: {self.data_bounds} ")

    @property
    def center(self):
        """
        Return the center point of the model, useful for setting the camera
        :return:
        """
        mids = []
        for coord in self.data_coords:
            mids.append((max(coord) + min(coord)) / 2)
        return mids

    def depth_slice(self, depth, hide_original=True):
        """
        Create a depth slice, looking in the Z direction at a plane in XY.

        :type depth: float
        :param depth: depth to make the cut of the cartesian model at
        """
        sliced_plane = Slice(self.data)
        sliced_plane.SliceType = "Plane"
        sliced_plane.SliceType.Normal = [0., 0., 1.]

        # Grabbing original origin information to manipulate the Z value
        _origin = sliced_plane.SliceType.Origin
        _origin = [_origin[0], _origin[1], depth]
        sliced_plane.SliceType.Origin = _origin

        # Remove the plane that shows the outline of the cut
        Hide3DWidgets(proxy=sliced_plane)
        Show(sliced_plane)

        if hide_original:
            Hide(self.data)

        return sliced_plane


class SurfaceMovie():
    """
    Reader for .inp AVS UCD files that are output by SPECFEM3D for movies
    related to surface displacement during a simulation
    """
    def __init__(self, fid, quantity="a"):
        """
        Open the data file. SPECFEM names the movie quantitiy "a" so we don't
        have to search for it, just name it
        """
        self.data = AVSUCDReader(FileNames=[fid])
        self.display = Show(self.data, GetActiveView(),
                            "UnstructuredGridRepresentation")
        # Going to assign the color functions here because it's simplest, rather
        # than separating these calls into the colorstuff functions
        self.lut = GetColorTransferFunction(quantity)
        self.pwf = GetOpacityTransferFunction(quantity)




