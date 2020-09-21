"""hydrotropism in a middle of a two plants"""
import sys; sys.path.append("../../..")
import plantbox as pb
import vtk_plot as vp

rs = pb.RootSystem()
path = "../../../modelparameter/rootsystem/"
name = ["PS_Pages_mod1bmodA", "PS_Pages_mod1bmodB"]

# Static soil property in a thin layer
maxS = 4  # maximal
minS = 0.1  # minimal
slope = 5  # linear gradient between min and max (cm)
box = pb.SDF_PlantBox(10, 10, 10)  # cm
layer = pb.SDF_RotateTranslate(box, pb.Vector3d(0, 0, -23))
soil_prop = pb.SoilLookUpSDF(layer, maxS, minS, slope)

C = 2  # number of columns
R = 1   # and rows
dist = 20  # distance between the root systems [cm]

# Initializes C*R root systems
allRS = []
for i in range(0, C):
    for j in range(0, R):
        rs = pb.RootSystem()
        rs.readParameters(path + name[i] + ".xml")
        
        # Manually set tropism to hydrotropism for the first six root types
        sigma = [0.4, 0.5, 1.] * 2
        tropN = [0.5, 0.9, 2.] * 2 # strength of tropism
        for p in rs.getRootRandomParameter():
            p.dx = 0.25  # adjust resolution
            p.tropismT = pb.TropismType.hydro
            p.tropismN = tropN[p.subType - 1]  # strength of tropism
            p.tropismS = sigma[p.subType - 1]
        rs.getRootSystemParameter().seedPos = pb.Vector3d(dist * i - (dist / 2), dist * j - (dist / 2), -3.)  # cm
        
        rs.setSoil(soil_prop) # Set the soil properties before calling initialize
        rs.initialize(False)  # verbose = False
        allRS.append(rs)
        
# Simulate dynamically
simtime = 40  # e.g. 30 or 60 days
dt = 1.5
N = round(simtime / dt)
for _ in range(0, N):
    for rs in allRS:
        ## in a dynamic soil setting you would need to update the soil properties (soil_prop)
        rs.simulate(dt, True)
    
# Export results as single vtp files (as polylines)
ana = pb.SegmentAnalyser()  # see example 3b
for i, rs in enumerate(allRS):
      vtpname = "results/example_LAB_multiple_hydrotrop" + str(i) + ".vtp"
#      rs.write(vtpname)
      ana.addSegments(rs)  # collect all
    
vp.plot_roots(ana, 'subType', "Multiple Hydro", True)
