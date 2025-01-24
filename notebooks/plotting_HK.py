#from GeorgCodeTesting import field # does not work because GeorgCodeTesting is an .ipynb file

### this does not seem to work yet
"""
from IPython import get_ipython

ipython = get_ipython()
field = ipython.magic("store -r field")
"""

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

def plot_segment(field, segment_number):
    """
    segment_number: starts at 0
    """
    from math import sin, cos
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    #from IPython import get_ipython

    #ipython = get_ipython()
    #field = ipython.magic("store -r field")

    if segment_number > 179 or segment_number < 0:
        print("Segment number needs to be between 0 and 179")
        return
    
    leafposA = [pos - 20.0 for pos in field.cp[segment_number]['leafSetA']] # because left=20 below in barh()
    leafposB = [-pos + 20.0 for pos in field.cp[segment_number]['leafSetB']]

    try:
        fig.close()
    except:
        pass
    fig, ax = plt.subplots()

    leaf_widths_for_plot = [lw-0.02 for lw in field.leaf_width]
    
    if field.machine_type == "Agility":
        ax.barh(field.leafblade_positions, leafposA[::-1], left=20.0, height=leaf_widths_for_plot) # The right leaf bank, [::-1] as Leaf 1 in 'field' is leaf 80 in Raystation
        ax.barh(field.leafblade_positions, leafposB[::-1], left=-20.0, height=leaf_widths_for_plot) # the left leaf bank
    else:
        ax.barh(field.leafblade_positions, leafposA, left=20.0, height=leaf_widths_for_plot) # the right leaf bank
        ax.barh(field.leafblade_positions, leafposB, left=-20.0, height=leaf_widths_for_plot) # the left leaf bank
    
    ### add the jaws
    
    
    if field.machine_type == "Agility":
        jawX1pos = field.cp[segment_number]['collimatorX1']
        jawX2pos = -1.0*field.cp[segment_number]['collimatorX2']
        ax.plot([-20, 20], [jawX1pos, jawX1pos], 'g-')
        ax.plot([-20, 20], [jawX2pos, jawX2pos], 'g-')
        X1jaw = patches.Rectangle((-20, jawX1pos), 40, 20-jawX1pos, color='grey', alpha=0.7)
        X2jaw = patches.Rectangle((-20, -20), 40, 20+jawX2pos, color='grey', alpha=0.7)
        ax.add_patch(X1jaw)
        ax.add_patch(X2jaw)
    else: # for Varian
        jawX1pos = -1.0*field.cp[segment_number]['collimatorX1'] # make negative to the left of isocenter
        jawX2pos = field.cp[segment_number]['collimatorX2']
        ax.plot( [jawX1pos, jawX1pos],[-20, 20],  'g-')
        ax.plot( [jawX2pos, jawX2pos],[-20, 20], 'g-')
        jawY1pos = -1.0*field.cp[segment_number]['collimatorY1']
        jawY2pos = field.cp[segment_number]['collimatorY2']
        ax.plot( [-20, 20], [jawY1pos, jawY1pos], 'g-')
        ax.plot( [-20, 20], [jawY2pos, jawY2pos], 'g-')


        X1jaw = patches.Rectangle((-20, -20), 20+jawX1pos, 40, color='grey', alpha=0.7)
        X2jaw = patches.Rectangle((jawX2pos, -20), 20-jawX2pos, 40, color='grey', alpha=0.7)
        ax.add_patch(X1jaw)
        ax.add_patch(X2jaw)
        Y1jaw = patches.Rectangle((-20, -20), 40, 20+jawY1pos, color='grey', alpha=0.7)
        Y2jaw = patches.Rectangle((-20, jawY2pos), 40, 20-jawY2pos, color='grey', alpha=0.7)
        ax.add_patch(Y1jaw)
        ax.add_patch(Y2jaw)

    ### add leaf numbers
    vertoffset=-0.1
    for i in range(len(field.leafblade_positions)):
        if field.machine_type == "Agility":
            ax.text(leafposA[79-i]+20.0, field.leafblade_positions[i]+vertoffset, str(i+1), fontsize=8) # the leafblade_positions follow the RS BEV numbering
            ax.text(leafposA[79-i]+22.0, field.leafblade_positions[i]+vertoffset, str(80-i), fontsize=8) # the leaf number follows the order in the JSON file
        else:
            ax.text(leafposA[i]+20.0, field.leafblade_positions[i]+vertoffset, str(i+1), fontsize=8)
    
    ### add isocenter
    ax.plot([-20, 20], [0, 0], 'k--')
    ax.plot([0, 0], [-20, 20], 'k--')
    
    ### add the sup-inf direction
    alpha = -1.0*field.collimatorAngleRad # need the negative angle for plotting, as we are not rotating the leafs
    length = 20.0
    spanmax = field.cp[segment_number]['spanMax']
    spanmin = field.cp[segment_number]['spanMin']
    
    ax.plot([-length*sin(alpha), length*sin(alpha)], [-length*cos(alpha), length*cos(alpha)], 'r-', linewidth=0.5)

    ax.plot([spanmin*sin(alpha), spanmax*sin(alpha)], [spanmin*cos(alpha), spanmax*cos(alpha)], 'r-', linewidth=3)
    


    ax.set_aspect('equal')

    ax.set_title('Segment '+str(segment_number+1)+'/'+str(field.ncontrolpoints))

    #plt.plot(range(80),field.cp[segment_number]['leafSetA'])
    #plt.plot(range(80),-1*(field.cp[segment_number]['leafSetB']))



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

