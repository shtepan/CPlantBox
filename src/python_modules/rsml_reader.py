import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

""" 
RSML Reader, by Daniel Leitner (2019) 
"""


def parse_rsml_(organ :ET, polylines :list, properties :dict, functions :dict, parent :int) -> (list, dict, dict):
    """ Recursivly parses the rsml file, used by read_rsml """
    for poly in organ.iterfind('geometry'):  # only one
        polyline = []
        for p in poly[0]:  # 0 is the polyline
            n = p.attrib
            newnode = [ float(n['x']), float(n['y']), float(n['z']) ]
            polyline.append(newnode)
        polylines.append(polyline)
        properties.setdefault("parent-poly", []).append(parent)

    for prop in organ.iterfind('properties'):
        for p in prop:  # i.e legnth, type, etc..
            properties.setdefault(str(p.tag), []).append(float(p.attrib['value']))

    for funcs in organ.iterfind('functions'):
        for fun in funcs:
            samples = [ ]
            for sample in fun.iterfind('sample'):
                samples.append(float(sample.attrib['value']))
            functions.setdefault(str(fun.attrib['name']), []).append(samples)

    pi = len(polylines) - 1
    for elem in organ.iterfind('root'):  # and all laterals
        polylines, properties, functions = parse_rsml_(elem, polylines, properties, functions, pi)

    return polylines, properties, functions


def read_rsml(name :str) -> (list, dict, dict):
    """Parses the RSML file into:

    Args:
    name(str): file name of the rsml file

    Returns: 
    (list, dict, dict):
    (1) a (flat) list of polylines, with one polyline per root
    (2) a dictionary of properties, one per root, adds "parent_poly" holding the index of the parent root in the list of polylines
    (3) a dictionary of functions     
    """
    root = ET.parse(name).getroot()
    plant = root[1][0]
    polylines = []
    properties = { }
    functions = { }
    for elem in plant.iterfind('root'):
        (polylines, properties, functions) = parse_rsml_(elem, polylines, properties, functions, -1)

    return polylines, properties, functions


def artificial_shoot(polylines, properties, functions):
    """ inserts an artificial shoot, with functions and properties of the the first polyline """ 
    polylines.insert(0, [[0, 0, -0.1], [0, 0, -2.]])
    for key, v in properties.items():
        properties[key].insert(0, properties[key][0])
    for key, v in functions.items():        
        functions[key].insert(0, [functions[key][0][0], functions[key][0][1]])    
    for i, p in enumerate(polylines):  # add one to the parent poly indices 
        properties["parent-poly"][i] += 1
    properties["parent-poly"][0] = -1
    properties["parent-node"][0] = -1
    for i, p in enumerate(polylines):
        if properties["parent-node"][i] < 0:
            properties["parent-node"][i] = 1
    return polylines, properties, functions


def get_segments(polylines :list, props :dict) -> (list, list):
    """ Converts the polylines to a list of nodes and an index list of line segments
        
    Args:
    polylines(list): flat list of polylines, one polyline per root
    props(dict): dictionary of properties, one per root, must contain "parent-node", (and "parent-poly" that was added by read_rsml)
    
    Returns: 
    (list, list): 
    (1) list of nodes
    (2) list of two integer node indices for each line segment 
    """
    nodes, offset, segs = [], [], []
    offset.append(0)  # global node index at each polyline
    for p in polylines:
        for n in p:
            nodes.append(n)
        offset.append(offset[-1] + len(p))
    for i, p in enumerate(polylines):
        ni = props["parent-node"][i]
        pi = props["parent-poly"][i]
        # print(i , "pn", ni, "parent", pi, len(polylines[pi]))
        assert ni < len(polylines[pi]), "parent node index exceeds number of parent nodes"
        if (pi >= 0):
            # print("pi", pi, "ni", ni, "s", [offset[pi] + ni, offset[i]])
            segs.append([offset[pi] + ni, offset[i]])
        for j in range(0, len(p) - 1):
            segs.append([offset[i] + j, offset[i] + j + 1])
    return nodes, segs


def get_parameter(polylines :list, funcs :dict, props :dict) -> (list, list, list):
    """ Copies radius, creation times, and types one value per segment 
    """    
    if "diameter" in props:
        fdiam_p = True
        fdiam = props["diameter"]
    else:
        fdiam_p = False
        fdiam = funcs["diameter"]
    if "type" in props:
        ptype_p = True
        ptype = props["type"]
    else:
        if "subType" in props:
            ptype_p = True
            ptype = props["subType"]
        else:
            ptype_p = False
            ptype = funcs["type"]  # otherwise we are in trouble
    if "emergence_time" in funcs:
        fet = funcs["emergence_time"]
    else: 
        fet = funcs["node_creation_time"]  # otherwise we are in trouble
    radii, cts, types = [], [], []  # copy stuff    
    for i, p in enumerate(polylines):
        for j in range(0, len(p)):
            if fdiam_p:
                radii.append(fdiam[i] / 2.)
            else:
                radii.append(fdiam[i][j] / 2.)
            if ptype_p:
                types.append(ptype[i])
            else:
                types.append(ptype[i][j])                
            cts.append(fet[i][j])        
    return radii[1:], cts[1:], types[1:]


def plot_rsml(polylines :list, prop :list):
    """Plots the polylines in y-z axis with colors given by a root property

    Args:
    polylines(list): flat list of polylines, one polyline per root 
    prop(list): a single property, list of scalar value, on per root 
    """
    f = matplotlib.colors.Normalize(vmin=min(prop), vmax=max(prop))
    cmap = plt.get_cmap("jet", 256)
    for i, pl in enumerate(polylines):
        nodes = np.array(pl)
        plt.plot(nodes[:, 1], nodes[:, 2], color=cmap(f(prop[i])))
    plt.axis('equal')
    plt.show()


def plot_segs(nodes :list, segs :list, fun :list):
    """Plots the segments in y-z axis (rather slow)
    
    Args:
    nodes(list): list of nodes
    segs(list): list of two integer node indices for each line segment 
    fun(list): a single function, list of scalar value, on per segment, see TODO 
    """
    f = matplotlib.colors.Normalize(vmin=min(fun), vmax=max(fun))
    cmap = plt.get_cmap("jet", 256)
    print("Segments")
    for i, s in enumerate(segs):
        plt.plot([nodes[s[0], 1], nodes[s[1], 1]], [nodes[s[0], 2], nodes[s[1], 2]], color=cmap(f(fun[i])))
    plt.axis('equal')
    plt.show()


if __name__ == '__main__':
    
    # fname = "../../../dumux-rosi/grids/RootSystem.rsml"
    fname = "../../tutorial/examples/python/results/example_3c.rsml"  # run example3c_write.py first (in tutorial/examples/python/)

    polylines, properties, functions = read_rsml(fname)
    polylines, properties, functions = artificial_shoot(polylines, properties, functions)  # for multiple base roots, add artificial root 
    
    print("Properties:")
    for key, v in properties.items() :
        print("\t", key, len(properties[key]))
    print("Functions:")
    for key, v in functions.items() :
        print("\t", key, len(functions[key]))
    plot_rsml(polylines, properties["parent-node"])

    nodes, segs = get_segments(polylines, properties)
    nodes = np.array(nodes)
    segs = np.array(segs, dtype=np.int64)
        
    radii, cts, types = get_parameter(polylines, functions, properties)
    plot_segs(nodes, segs, cts)  # slow
