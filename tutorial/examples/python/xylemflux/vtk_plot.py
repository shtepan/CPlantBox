import plantbox as pb
from vtk_tools import *

import numpy as np
import vtk

""" 
VTK Tools, by Daniel Leitner (refurbished 12/2019) 

for vtk to numpy, and numpy to vtk conversions
reading: vtp, writing: msh, dgf, vtp, rsml
"""


def segs_to_polydata(rs, zoom_factor = 10., param_names = ["radius", "type", "creationTime"]):
    """ Creates vtkPolydata from a RootSystem or Plant using segments 
    @param rs             A RootSystem, Plant, or SegmentAnalyser
    @param zoom_factor    The radial zoom factor, since root are sometimes too thin for vizualisation
    @param param_names    Parameter names of scalar fields, that are copied to the polydata    
    @return A vtkPolydata object of the root system
    """
    if isinstance(rs, pb.Organism):
        ana = pb.SegmentAnalyser(rs)  # for Organism like Plant or RootSystem
    else:
        ana = rs
    nodes = np_convert(ana.nodes)
    segs = np_convert(ana.segments)
    points = vtk_points(nodes)
    cells = vtk_cells(segs)
    pd = vtk.vtkPolyData()
    pd.SetPoints(points)
    pd.SetLines(cells)  # check SetPolys
    for n in param_names:
        param = np.array(ana.getParameter(n))
        if param.shape[0] == segs.shape[0]:
            if n == "radius":
                param *= zoom_factor
            data = vtk_data(param)
            data.SetName(n)
            pd.GetCellData().AddArray(data)
        else:
            print("segs_to_polydata: Warning parameter " + n + " is sikpped because of wrong size", param.shape[0], "instead of", segs.shape[0])

    c2p = vtk.vtkCellDataToPointData()
    c2p.SetPassCellData(True)
    c2p.SetInputData(pd)
    c2p.Update()
    return c2p.GetPolyDataOutput()


def uniform_grid(min_, max_, res):
    """ Creates an uniform grid
    
    @return The vtkUniformGrid
    """
    grid = vtk.vtkUniformGrid()
    grid.SetDimensions(int(res[0]) + 1, int(res[1]) + 1, int(res[2]) + 1)  # points
    grid.SetOrigin(min_[0], min_[1], min_[2])
    s = (max_ - min_) / res
    grid.SetSpacing(s[0], s[1], s[2])
    return grid


def render_window(actor, title = "", scalarBar = None):
    """ puts a vtk actor on the stage (an interactive window) @name is the window titel 
    
    @param actor         the (single) actor
    @param windowName    optional
    @param scalarBar     an optional vtkScalarBarActor
    @return The vtkRenderWindow (not sure if this is ever needed)
    
    (built in)
    Keypress j / Keypress t: toggle between joystick (position sensitive) and trackball (motion sensitive) styles. In joystick style, motion occurs continuously as long as a mouse button is pressed. In trackball style, motion occurs when the mouse button is pressed and the mouse pointer moves.
    Keypress c / Keypress a: toggle between camera and actor modes. In camera mode, mouse events affect the camera position and focal point. In actor mode, mouse events affect the actor that is under the mouse pointer.
    Button 1: rotate the camera around its focal point (if camera mode) or rotate the actor around its origin (if actor mode). The rotation is in the direction defined from the center of the renderer's viewport towards the mouse position. In joystick mode, the magnitude of the rotation is determined by the distance the mouse is from the center of the render window.
    Button 2: pan the camera (if camera mode) or translate the actor (if actor mode). In joystick mode, the direction of pan or translation is from the center of the viewport towards the mouse position. In trackball mode, the direction of motion is the direction the mouse moves. (Note: with 2-button mice, pan is defined as <Shift>-Button 1.)
    Button 3: zoom the camera (if camera mode) or scale the actor (if actor mode). Zoom in/increase scale if the mouse position is in the top half of the viewport; zoom out/decrease scale if the mouse position is in the bottom half. In joystick mode, the amount of zoom is controlled by the distance of the mouse pointer from the horizontal centerline of the window.
    Keypress 3: toggle the render window into and out of stereo mode. By default, red-blue stereo pairs are created. Some systems support Crystal Eyes LCD stereo glasses; you have to invoke SetStereoTypeToCrystalEyes() on the rendering window.
    Keypress e: exit the application.
    Keypress f: fly to the picked point
    Keypress p: perform a pick operation. The render window interactor has an internal instance of vtkCellPicker that it uses to pick.
    Keypress r: reset the camera view along the current view direction. Centers the actors and moves the camera so that all actors are visible.
    Keypress s: modify the representation of all actors so that they are surfaces.
    Keypress u: invoke the user-defined function. Typically, this keypress will bring up an interactor that you can type commands in. Typing u calls UserCallBack() on the vtkRenderWindowInteractor, which invokes a vtkCommand::UserEvent. In other words, to define a user-defined callback, just add an observer to the vtkCommand::UserEvent on the vtkRenderWindowInteractor object.
    Keypress w: modify the representation of all actors so that they are wireframe.
    
    (additional)
    Keypress g: save as png    
    """
    colors = vtk.vtkNamedColors()  # Set the background color
    bkg = map(lambda x: x / 255.0, [26, 51, 102, 255])
    colors.SetColor("BkgColor", *bkg)
    ren = vtk.vtkRenderer()  # Set up window with interaction
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    iren = vtk.vtkRenderWindowInteractor()
    iren.AddObserver('KeyPressEvent', keypress_callback_, 1.0)
    # iren.SetInteractorStyle(vtk.vtkInteractorStyleUnicam())  # <- better than default, but maybe we find a better one

    if isinstance(actor, list):
        actors = actor  # plural
    else:
        actors = [actor]  # army of one
    for a in actors:
        ren.AddActor(a)  # Add the actors to the renderer, set the background and size
    if scalarBar is not None:
        ren.AddActor2D(scalarBar)
    ren.SetBackground(colors.GetColor3d("BkgColor"))
    renWin.SetSize(1000, 1000)
    renWin.SetWindowName(title)
    ren.ResetCamera()
    ren.GetActiveCamera().Zoom(1.5)

    iren.SetRenderWindow(renWin)
    renWin.Render()

    iren.Initialize()  # This allows the interactor to initalize itself. It has to be called before an event loop.
    iren.Start()  # Start the event loop.

    return renWin


def keypress_callback_(obj, ev):
    key = obj.GetKeySym()
    if key == 'g':
        renWin = obj.GetRenderWindow()
        file_name = renWin.GetWindowName()
        write_png(renWin, file_name)
        print("saved", file_name + ".png")


def write_png(renWin, fileName):
    """" Save the current render window in a png
    @param renWin        the vtkRenderWindow 
    @parma fileName      file name without extension
    """
    windowToImageFilter = vtk.vtkWindowToImageFilter();
    windowToImageFilter.SetInput(renWin)
    windowToImageFilter.SetInputBufferTypeToRGBA()  # also record the alpha (transparency) channel
    windowToImageFilter.ReadFrontBufferOff()  # read from the back buffer
    windowToImageFilter.Update()
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(fileName + ".png")
    writer.SetInputConnection(windowToImageFilter.GetOutputPort())
    writer.Write()


def get_lookup_table():
    """ creates a color lookup table 
    @return A vtkLookupTable
    """
#     # Make the lookup table.
#     lut.SetTableRange(scalarRange) = vtk.vtkColorSeries()
#     # Select a color scheme.
#     # colorSeriesEnum = colorSeries.BREWER_DIVERGING_BROWN_BLUE_GREEN_9
#     # colorSeriesEnum = colorSeries.BREWER_DIVERGING_SPECTRAL_10
#     # colorSeriesEnum = colorSeries.BREWER_DIVERGING_SPECTRAL_3
#     # colorSeriesEnum = colorSeries.BREWER_DIVERGING_PURPLE_ORANGE_9
#     # colorSeriesEnum = colorSeries.BREWER_SEQUENTIAL_BLUE_PURPLE_9
#     # colorSeriesEnum = colorSeries.BREWER_SEQUENTIAL_BLUE_GREEN_9
#     colorSeriesEnum = colorSeries.BREWER_QUALITATIVE_SET3
#     # colorSeriesEnum = colorSeries.CITRUS
#     colorSeries.SetColorScheme(colorSeriesEnum)
#     lut = vtk.vtkLookupTable()
#     lut.SetNumberOfTableValues(16)"radius"
#     colorSeries.BuildLookupTable(lut)
#     # lut.SetNanColor(1, 0, 0, 1)
#     lut.SetTableRange([0, 1])
    lut = vtk.vtkLookupTable()
    lut.SetNumberOfTableValues(16)
    lut.SetHueRange(0.0, 1.0)
    lut.Build()
    return lut


def plot_roots(pd, p_name, render = True):
    """ renders the root system in an interactive window 
    @param pd         the polydata representing the root system
    @param p_name      parameter name of the data to be visualized
    @param render     render in a new interactive window (default = True)
    @return The vtkActor object
    """
    pd.GetPointData().SetActiveScalars("radius")  # for the the filter
    tubeFilter = vtk.vtkTubeFilter()
    tubeFilter.SetInputData(pd)
    tubeFilter.SetNumberOfSides(9)
    tubeFilter.SetVaryRadiusToVaryRadiusByAbsoluteScalar()
    tubeFilter.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(tubeFilter.GetOutputPort())
    mapper.Update()
    mapper.ScalarVisibilityOn();
    mapper.SetScalarModeToUseCellFieldData()  # Cell is not working
    mapper.SetArrayName(p_name)
    mapper.SelectColorArray(p_name)
    mapper.UseLookupTableScalarRangeOn()

    plantActor = vtk.vtkActor()
    plantActor.SetMapper(mapper)

    lut = get_lookup_table()
    lut.SetTableRange(pd.GetPointData().GetScalars(p_name).GetRange())
    mapper.SetLookupTable(lut)

    scalarBar = vtk.vtkScalarBarActor()
    scalarBar.SetLookupTable(lut)
    scalarBar.SetTitle(p_name)
#    textProperty = vtk.vtkTextProperty()
#    scalarBar.SetTitleTextProperty(textProperty)
#    scalarBar.SetLabelTextProperty(textProperty)
#    scalarBar.SetAnnotationTextProperty(textProperty)
#    scalarBar = None

    if render:
        render_window(plantActor, pname, scalarBar)
    return plantActor, scalarBar


def plot_mesh(grid, p_name, win_title = "", render = True):
    """ Plots the grid as wireframe
    @param grid         some vtk grid (structured or unstructured)
    @param p_name       parameter to visualize
        
    """
#     bounds = grid.GetBounds()
#     print("mesh bounds", bounds, "[m]")
    if win_title == "":
        win_title = p_name

    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputData(grid)
    mapper.Update()
    mapper.SetArrayName(p_name)
    mapper.SelectColorArray(p_name)
    mapper.UseLookupTableScalarRangeOn()

    meshActor = vtk.vtkActor()
    meshActor.SetMapper(mapper)
    meshActor.GetProperty().SetRepresentationToWireframe();

    lut = get_lookup_table()
    if p_name != "":
        lut.SetTableRange(grid.GetPointData().GetScalars(p_name).GetRange())
    mapper.SetLookupTable(lut)

    scalarBar = vtk.vtkScalarBarActor()
    scalarBar.SetLookupTable(lut)
    scalarBar.SetTitle(p_name)

    if render:
        render_window(meshActor, win_title, scalarBar)  # todo scalarBar (and plot a thing or two)
    return meshActor, scalarBar


def plot_mesh_cuts(ug, p_name, nz = 7):
    """ """
    bounds = ug.GetBounds()
    print(bounds)
    print("z-axis", bounds[4], bounds[5])
    # z-slices (implicit fucntions)
    planes = []
    for i in range(0, nz):
        p = vtk.vtkPlane()
        z = ((bounds[5] - bounds[4]) / (nz + 1)) * (i + 1)
        print(bounds[4] + z)
        p.SetOrigin(bounds[4] + z, 0, 0)
        p.SetNormal(0, 0, 1)
        planes.append(p)

    # create cutter, mappers, and actors
    actors = []
    for i in range(0, nz):
        cutter = vtk.vtkCutter()
        cutter.SetCutFunction(planes[i])
        cutter.SetInputData(ug)
        # cutter.SetInputConnection(cube.GetOutputPort())
        cutter.Update()
        m = vtk.vtkPolyDataMapper()
        m.SetInputConnection(cutter.GetOutputPort())
        m.Update()
        # create plane actor
        a = vtk.vtkActor()
#         planeActor.GetProperty().SetColor(1.0, 1, 0)
#         planeActor.GetProperty().SetLineWidth(2)
        a.SetMapper(m)
        actors.append(a)
    if render:
        render_window_(actors, "Cuts")
    return actors
