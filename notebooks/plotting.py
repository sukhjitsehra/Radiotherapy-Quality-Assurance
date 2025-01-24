def create_leaf_progression(control_points, leaf_num, set = "A"):

    if leaf_num < 1 or leaf_num > 80:
        print("please use a leaf number between 1 and 80")
        return

    leaf_num -= 1

    values = []

    for segment in control_points:
        value = segment["leafSet" + set][leaf_num]
        values.append(value)

    return values

def plot_leaf_progression(leaf_values):

    import matplotlib.pyplot as plt

    if len(leaf_values) != 180:

        print("There must be 180 leaf values")
        return

    plt.plot(range(180), leaf_values)
    plt.show()

    return 

def plot_segment(field_info, segment_number):
    import pandas as pd
    import matplotlib.pyplot as plt

    if segment_number > 180 or segment_number < 0:
        print("Segment number needs to be between 0-180")
        return
    
    plt.plot(range(80),field_info['mqControlPoints'][segment_number]['leafSetA'])
    plt.plot(range(80),-1*pd.Series(field_info['mqControlPoints'][segment_number]['leafSetB']))

    plt.show()

    return

def plot_active_segment(field_info, segment_number, active_start, active_end):
    import matplotlib.pyplot as plt
    import pandas as pd

    if segment_number > 180 or segment_number < 0:
        print("Segment number needs to be between 0-180")
        return
    plt.plot(range(80)[active_end:active_start],field_info['mqControlPoints'][segment_number]['leafSetA'][active_end:active_start])
    plt.plot(range(80)[active_end:active_start],-1*pd.Series(field_info['mqControlPoints'][segment_number]['leafSetB'][active_end:active_start]))
    plt.show()

    return

def plot_active_segment(field_info, segment_number, active_start, active_end):
    import matplotlib.pyplot as plt
    import pandas as pd

    if segment_number > 180 or segment_number < 0:
        print("Segment number needs to be between 0-180")
        return
    plt.plot(range(80)[active_end:active_start],field_info['mqControlPoints'][segment_number]['leafSetA'][active_end:active_start])
    plt.plot(range(80)[active_end:active_start],-1*pd.Series(field_info['mqControlPoints'][segment_number]['leafSetB'][active_end:active_start]))
    plt.show()

    return

def degrees_to_radians(degrees_list): # written by chatgpt
    import math
    radians_list = [math.radians(angle) for angle in degrees_list]
    return radians_list

def plot_radial_leaf_progression(leaf_number, control_points):
    import numpy as np 
    import matplotlib.pyplot as plt
    import pandas as pd

    gantrys = []
    leafA_values = []
    leafB_values = []

    for i in control_points:
        gantrys.append(i["gantryAngle"])
        leafA_values.append(i["leafSetA"][leaf_number])
        leafB_values.append(i["leafSetB"][leaf_number])

    gantrys = degrees_to_radians(gantrys)

    offset = np.pi / 2

    fig, ax = plt.subplots(figsize = (20,10), subplot_kw={"projection":"polar"})

    ax.set_theta_offset(offset)

    ax.set_ylim(-10, 10)

    ax.set_frame_on(False)

    ax.plot(gantrys, pd.Series(leafA_values), drawstyle = "steps", mouseover = True)#, width = width, fill = False, edgecolor = "blue")
    ax.plot(gantrys, -pd.Series(leafB_values), drawstyle = "steps", mouseover = True)#, width = width, fill = False, edgecolor = "red")

    plt.show()

    return

