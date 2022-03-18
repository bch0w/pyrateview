"""
The main Pyrateview call script which opens and manipulates VTK files for
simplified plotting. Argparse handles command line arguments to simplify
user defined plotting requirements

.. notes::
    - If you're seeing only white in your screenshots then check that your
        camera position is actually pointed at your model
    - If you're only seeing one color, you may be zoomed in too far
"""
import os
import argparse
import importlib
from glob import glob
from paraview.simple import (GetActiveViewOrCreate, Render, ResetCamera,
                             GetLayout)
from datafile import CartesianDataFile, SurfaceMovie
from actions import screenshot, set_camera, check_render_view
from colorstuff import colormap, colorbar


def parse_args():
    """
    Set user defined input arguments. Perform some sanity checks before passing
    arguments into main
    """
    parser = argparse.ArgumentParser()

    # General requirements
    parser.add_argument("fid", type=str, help="the file to open and plot")
    parser.add_argument("-c", "--cfg_fid", type=str, help="config .yaml file",
                        default="config.py")
    parser.add_argument("-M", "--movie", action="store_true", default=False)
    parser.add_argument("-v", "--verbose", action="store_true", default=False,
                        help="print output messages during the plotting")
    parser.add_argument("-o", "--output", type=str,
                        help="output path to save figures",
                        default=os.path.join(os.getcwd(), "output"))
    parser.add_argument("-f", "--fid_out", type=str, default=None,
                        help="name of the output .png file, if not given will "
                             "default to 'fid' + .png")

    args = check(parser.parse_args())

    return args


def check(args):
    """
    Sanity check arguments passed in to avoid any unwanted crashes
    """
    # Make sure the file to plot actually exists
    if not args.movie:
        assert(os.path.exists(args.fid)), f"{args.fid} does not exist"

    # Make the output directory if it doesn't exist
    if not os.path.exists(args.output):
        os.mkdir(args.output)

    # Determine the output file name
    if args.fid_out is None:
        args.fid_out = args.fid + ".png"

    return args


def setup(cfg_fid="config.py"):
    """
    Run an initialization routine and return the configuration parameters
    """
    # Load in the configuration .py file that contains User defined controls
    assert(os.path.exists(cfg_fid)), \
        f"PyrateView requires a valid .py configuration file: {cfg_fid}"
    # Drop the .py when importing module
    cfg = importlib.import_module(os.path.splitext(cfg_fid)[0])

    # Establish the render view for ParaView
    GetActiveViewOrCreate("RenderView")
    Render()
    layout = GetLayout()
    layout.SetSize(cfg.resolution[0], cfg.resolution[1])

    return cfg

# =============================================================================

def cartesian():
    """
    Main function to plot cartesian data
    :return:
    """
    # Open the data file
    cdf = CartesianDataFile(args.fid,
                            scale_data=cfg.scale_data,
                            scale_coords=cfg.scale_coords,
                            zero_origin=cfg.zero_origin
                            )

    # Determine how we will view the data file
    zslice = cdf.depth_slice(depth=-5)

    # Set up the color bar and the colorscale
    lut = colormap(cdf.data, colormap=cfg.cmap,
                   use_above_range=cfg.use_above_range,
                   use_below_range=cfg.use_below_range,
                   invert=cfg.invert_cmap, num_values=cfg.num_values
                   )

    cbar = colorbar(lut, title=cfg.title, component_title="",
                    orientation=cfg.cbar_orientation,
                    position=cfg.cbar_position,
                    range_label_format=cfg.label_format,
                    label_format=cfg.label_format,
                    thickness=cfg.cbar_thickness, length=cfg.cbar_length,
                    fontsize=cfg.fontsize, fontcolor=cfg.fontcolor,
                    title_justification=cfg.title_justification,
                    text_position=cfg.text_position
                    )

    # Establish the camera position
    xm, ym, _ = cdf.center
    ResetCamera()
    # set_camera(position=[xm, ym, 10], focal_point=[xm, ym, 0],
    #            camera_view=[0, 1, 0], scale=2, interaction_mode="3D")
    # set_camera(position=[xm, ym, 1481E3], focal_point=[xm, ym, -200E3],
    #            camera_view=[0, 1, 0], scale=434E3, interaction_mode="3D")

    screenshot(fid=os.path.join(args.output, args.fid_out),
               resolution=cfg.resolution)


def movie_frame():
    """
    Main function to produce a movie frame from the AVS files of SPECFEM.
    Very simple as the surface movies are just 2D planes so we only need to
    adjust color and elevation to get something usable.
    """
    # Open the data file and show it
    if args.verbose:
        files_ = glob(args.fid)
        print(f"{len(files_)} movie files found")

    for fid in sorted(glob(args.fid)):
        if args.verbose:
            print(fid)
        mov = SurfaceMovie(fid)

        # Rescale the colorbar to get a consistent amplitude
        mov.lut.RescaleTransferFunction(cfg.mov_bounds[0], cfg.mov_bounds[1])
        mov.pwf.RescaleTransferFunction(cfg.mov_bounds[0], cfg.mov_bounds[1])

        # Scale the vertical axis, useful for accentuating topography in movies
        mov.display.Scale = [1., 1., cfg.mov_scale]

        # TO DO: Annotate the frame number or step onto the image

        # TO DO: Add coastline and any other random things here

        ResetCamera()
        screenshot(fid=os.path.join(args.output, fid + ".png"),
                   resolution=cfg.resolution)


if __name__ == "__main__":
    args = parse_args()
    cfg = setup(cfg_fid=args.cfg_fid)
    movie_frame()





