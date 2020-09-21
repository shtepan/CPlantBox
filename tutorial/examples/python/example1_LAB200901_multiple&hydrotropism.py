"""hydrotropism in a middle of a two plants"""
import sys; sys.path.append("../../..")
import plantbox as pb
import vtk_plot as vp

rs = pb.RootSystem()
path = "../../../modelparameter/rootsystem/"
name = "Anagallis_femina_Leitner_2010"
rs.readParameters(path + name + ".xml")

# Manually set tropism to hydrotropism for the first ten root types
sigma = [0.4, 1., 1., 1., 1. ] * 2
for p in rs.getRootRandomParameter():
        p.dx = 0.25  # adjust resolution
        p.tropismT = pb.TropismType.hydro
        p.tropismN = 2  # strength of tropism
        p.tropismS = sigma[p.subType - 1]

# Static soil property in a thin layer
maxS = 0.7  # maximal
minS = 0.1  # minimal
slope = 10  # linear gradient between min and max (cm)
box = pb.SDF_PlantBox(20, 20, 10)  # cm
layer = pb.SDF_RotateTranslate(box, pb.Vector3d(0, 0, -10))
soil_prop = pb.SoilLookUpSDF(layer, maxS, minS, slope)

# Set the soil properties before calling initialize
rs.setSoil(soil_prop)

# Initialize
rs.initialize()

# Simulate
simtime = 100  # e.g. 30 or 60 days
dt = 1
N = round(simtime / dt)
for _ in range(0, N):
    # in a dynamic soil setting you would need to update the soil properties (soil_prop)
    rs.simulate(dt)

# Export results (as vtp)
#<<<<<<< HEAD
#rs.write("results/example_5a.vtp")

# Export geometry of static soil
#rs.setGeometry(layer)  # just for vizualisation
#rs.write("results/example_5a.py")
#=======
#rs.write("results/example_4a.vtp")

# Export geometry of static soil
#rs.setGeometry(layer)  # just for vizualisation
#rs.write("results/example_4a.py")

# Plot, using vtk
vp.plot_roots(rs, 'subType', 'oblique', True)
#>>>>>>> upstream/master


# testujeme kod

# print(pb.SoilLookUpSDF)
