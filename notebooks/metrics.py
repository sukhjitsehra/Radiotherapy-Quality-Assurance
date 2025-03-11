def calcualte_area(control_points, leaf_number, gantry_angle):
    i = 0
    while gantry_angle != control_points[i]["gantryAngle"]:
        i += 1

    length = control_points[i]["leafSetA"][leaf_number] + control_points[i]["leafSetB"][leaf_number]

    width = control_points[i]["fieldY"] / control_points[i]["mlcLeaves"]

    return length*width

def calculate_leaf_area(control_points, leaf_number):
    total_area = 0
    for i in control_points:
        length = control_points[i]["leafSetA"][leaf_number] + control_points[i]["leafSetB"][leaf_number]
        width = control_points[i]["fieldY"] / control_points[i]["mlcLeaves"]
        total_area += length*width

    return total_area


def calculate_gantry_area(control_points, gantry_angle):
    i = 0
    while gantry_angle != control_points[i]["gantryAngle"]:
        i += 1

    total_area = 0

    gantry = control_points[i]

    for i in range(len(gantry["leafSetA"])):
        length = gantry["leafSetA"][i] + gantry["leafSetB"][i]
        width = gantry["fieldY"] / gantry["mlcLeaves"]
        total_area += length*width
    return total_area

def calculate_total_area(control_points):

    n_leaves = control_points[0]["mlcLeaves"]
    total_area = 0

    for i in range(n_leaves):

        total_area += calculate_leaf_area(control_points, i)

    return total_area

def average_leaf_area(control_points):
    n_leaves = control_points[0]["mlcLeaves"]

    total_area = calculate_total_area(control_points)

    return total_area/n_leaves

def average_gantry_area(control_points):
    n_gantry = len(control_points)
    total_area = calculate_total_area(control_points)
    return total_area/n_gantry


def leaf_area_weights(control_points):
    import pandas as pd

    n_leaves = control_points[0]["mlcLeaves"]

    total_area = 0
    leaf_areas = []

    for i in range(n_leaves):
        leaf_area = calculate_leaf_area(control_points, i)
        total_area += leaf_area
        leaf_areas.append(leaf_area)

    weigths = pd.Series(leaf_areas)/total_area

    return weigths
