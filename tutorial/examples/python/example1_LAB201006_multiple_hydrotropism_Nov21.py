"""hydrotropism in a middle of a two plants"""
import sys; sys.path.append("../../..")
import plantbox as pb
import vtk_plot as vp

rs = pb.RootSystem()
path = "../../../modelparameter/rootsystem/"
name = ["Triticum_aestivum_a_Bingham_2011", "PS_Pages_mod1bmodB", "PS_Pages_mod1bmodB", "PS_Pages_mod1bmodB"]

# Static soil property in a thin layer
maxS = 5  # maximal
minS = 0.5  # minimal
slope = 12  # linear gradient between min and max (cm), half length of linear interpolation between fmax and fmin
box = pb.SDF_PlantBox(30, 60, 40)  # cm
layer = pb.SDF_RotateTranslate(box, pb.Vector3d(0, 0, -3))
soil_prop = pb.SoilLookUpSDF(layer, maxS, minS, slope)

C = 2  # number of columns
R = 1   # and rows
dist = 35  # distance between the root systems [cm]

# Initializes C*R root systems
allRS = []
for i in range(0, C):
    for j in range(0, R):
        rs = pb.RootSystem()
        rs.readParameters(path + name[i] + ".xml")
        
#        # Manually set tropism to hydrotropism for the first six root types
#        sigma = [0.4, 0.4, 0.5] *2
#        tropN = [0.7, 0.8, 1.0] *2 # strength of tropism
#        #RootLif3Time = [50, 40, 40, 30]
#        for p in rs.getRootRandomParameter():
#            p.dx = 0.5  # adjust resolution
#            p.tropismT = pb.TropismType.hydro
#            p.tropismN = tropN[p.subType - 1]  # strength of tropism
#            p.tropismS = sigma[p.subType - 1]
#            #p.rlt = RootLifeTime[i]
        rs.getRootSystemParameter().seedPos = pb.Vector3d(dist * i - (dist/2), dist * j, -3.)  # cm
        
        rs.setSoil(soil_prop) # Set the soil properties before calling initialize
        rs.initialize(False)  # verbose = False
        allRS.append(rs)
        
# Simulate dynamically
#simtime = 35  # e.g. 30 or 60 days
dt = 1
N = round(simtime / dt)
for _ in range(0, N):
    for rs in allRS:
        ## in a dynamic soil setting you would need to update the soil properties (soil_prop)
        rs.simulate(dt, True)
    
# Export results as single vtp files (as polylines)
ana = pb.SegmentAnalyser()  # see example 3b
for i, rs in enumerate(allRS):
      vtpname = "resultsLAB/RLab_201002bexample_LAB_multiple_hydrotrop" + str(i) + ".vtp"
      rs.write(vtpname)
      ana.addSegments(rs)  # collect all
    
vp.plot_roots(ana, 'creationTime', "Multiple Hydro", True) # misto creationTime muze byt napr. subType ...

