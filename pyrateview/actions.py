"""
Perform actions using Paraview interface, for example taking screenshots,
deleting objects etc.
"""
from paraview.simple import (SaveScreenshot, GetActiveView, GetSources, Delete,
                             FindSource, ResetCamera, GetActiveCamera, Render)


def screenshot(fid, resolution, transparent_bg=True):
    """
    Save a screenshot of the current model setup

    :type fid: str
    :param fid: file id to save the screenshot
    :type resolution: list of float
    :param resolution: image resolution of the output screenshot
    :type transparent_bg:bool
    :param transparent_bg: if .png file, set the background to alpha
    """
    SaveScreenshot(fid, GetActiveView(), ImageResolution=resolution,
                   TransparentBackground=transparent_bg)


def delete_objects(names=None):
    """
    Delete temporary objects that were required for a given screenshot, e.g.
    glyphs representing source locations, or rulers used for
    distance measurements.

    Works on the assumption that the registration names of temporary objects
    match the object type. For example if you create a ruler, it should be named
    something like 'ruler_1'

    :type names: list of str
    :param names: identifiers of the objects that should be deleted, e.g.
        'ruler', 'point', 'glyph', etc.
    """
    # Defaults to deleting common names
    if names is None:
        names = ["ruler", "point", "glyph"]

    for src in [_[0] for _ in GetSources().keys]:
        for name in names:
            if name in src:
                src = FindSource(src)
                Delete(src)
                break

def set_camera(position, focal_point, camera_view, scale,
               interaction_mode="2D"):
    """
    Set the position and direction of the camera

    :type position: list of float
    :param position: [x,y,z] position of the camera
    :type focal_point: list of float
    :param focal_point: [x,y,z] position that the camera looks towards
    :type camera_view: list of int
    :param camera_view: [x,y,z] to set the rotation of the camera
    :type scale: float
    :param scale: the zoom factor on the camera
    :type interaction_mode: str
    :param interaction_mode: '2D' or '3D'. '2D' will distort the visualization
        somewhat to make planar features look better, and is recommended for
        any 2D projections (e.g. depth slices, cross sections).
    """
    ResetCamera()

    renderView = GetActiveView()
    renderView.InteractionMode = interaction_mode
    renderView.CameraPosition = position
    renderView.CameraFocalPoint = focal_point
    renderView.CameraViewUp = camera_view
    renderView.CameraParallelScale = scale

    Render()

def check_render_view():
    """
    Figure out what the current camera position is if e.g. you want to
    recreate at a later point
    :return:
    """
    renderView = GetActiveView()
    print(f"Position: {renderView.CameraPosition}")
    print(f"FocalPoint: {renderView.CameraFocalPoint}")
    print(f"ParallelScale: {renderView.CameraParallelScale}")
    print(f"ViewUp: {renderView.CameraViewUp}")
    print(f"InteractionMode: {renderView.InteractionMode}")