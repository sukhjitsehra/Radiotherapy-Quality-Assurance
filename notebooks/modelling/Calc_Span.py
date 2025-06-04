


import matplotlib.pyplot as plt
import math


def calcAlpha(ordinate, abscissa):
    # the 'ordinate' is the vertical, the 'abscissa' is the horizontal axis
    
    if ordinate == 0 and abscissa == 0:
        alpha = 0
    elif ordinate > 0 and abscissa == 0:
        alpha = 90
    elif ordinate < 0 and abscissa == 0:
        alpha = 270
    
    elif ordinate >= 0 and abscissa > 0:
        alpha= math.degrees(math.atan(ordinate/abscissa))
    elif ordinate >= 0 and abscissa < 0:
        alpha= math.degrees(math.atan(ordinate/abscissa)) + 180
    elif ordinate <= 0 and abscissa < 0:
        alpha= math.degrees(math.atan(ordinate/abscissa)) + 180    
    elif ordinate <= 0 and abscissa > 0:
        alpha= math.degrees(math.atan(ordinate/abscissa)) + 360
    
    return alpha
    
    

def span(machine_type, collimatorAngle, X1, X2, Y1 = None, Y2 = None):

    # machine_type == Agility: X1, X2 are the "top" and "bottom" jaws, "Y1" and "Y2" are the imaginary left and right jaws (to be replaced by the maxima of LeafbankB and LeafbankA respectively)

    if machine_type == "Agility":
    
        alpha1 = calcAlpha(X1, Y2) #UR
        alpha2 = calcAlpha(X1, -Y1)  #UL
        alpha3 = calcAlpha(-X2, -Y1) #BL
        alpha4 = calcAlpha(-X2, Y2) #BR
        
        radius1 = math.sqrt(math.pow(X1,2)+math.pow(Y2,2)) #UR
        radius2 = math.sqrt(math.pow(X1,2)+math.pow(-Y1,2)) #UL
        radius3 = math.sqrt(math.pow(-X2,2)+math.pow(-Y1,2)) #BL
        radius4 = math.sqrt(math.pow(-X2,2)+math.pow(Y2,2)) #BR
        
        
        print(alpha1, alpha2, alpha3, alpha4)
        print(radius1, radius2, radius3, radius4)
        
        
        ### calculate the rotated field edges
        # collimatorAngle needs to be in radians units
        UR_rotated = [radius1*math.cos(math.radians(alpha1)+collimatorAngle), radius1*math.sin(math.radians(alpha1)+collimatorAngle)]
        UL_rotated = [radius2*math.cos(math.radians(alpha2)+collimatorAngle), radius2*math.sin(math.radians(alpha2)+collimatorAngle)]
        BL_rotated = [radius3*math.cos(math.radians(alpha3)+collimatorAngle), radius3*math.sin(math.radians(alpha3)+collimatorAngle)]
        BR_rotated = [radius4*math.cos(math.radians(alpha4)+collimatorAngle), radius4*math.sin(math.radians(alpha4)+collimatorAngle)]
        
        field_rotated = [UR_rotated, UL_rotated, BL_rotated, BR_rotated]
        field_rotated_ordinate = [corner[1] for corner in field_rotated]
        
        span = max(field_rotated_ordinate) - min(field_rotated_ordinate)
        print('span = ', span)

    elif machine_type == 'Varian':
        # please copy the above code with the correct X1, X2, Y1, Y2 for the Varian linacs. 
        pass
        
    return field_rotated



    
    
if __name__ == '__main__':


    X1 = 2.0
    X2 = 5.0
    Y1 = 5.0
    Y2 = 5.0
    
    coll = 90 # in degrees
    coll = math.radians(coll)
    
    fig, ax = plt.subplots()
    
    # plot the unrotated field with collimator angle = 0
    ax.plot([Y2, -Y1, -Y1, Y2, Y2], [X1, X1, -X2, -X2, X1], 'ro-')
    
    # plot field center
    ax.plot([0, 0], [20, -20], '--', color='black')
    ax.plot([-20, 20], [0, 0], '--', color='black')    
    
    
    ax.set_aspect('equal')
    
    
    field_rotated = span("Agility", coll, X1, X2, Y1, Y2)
    
    # plot the rotated field
    field_rotated_abscissa = [corner[0] for corner in field_rotated]
    field_rotated_ordinate = [corner[1] for corner in field_rotated]
    ax.plot(field_rotated_abscissa+[field_rotated_abscissa[0]], field_rotated_ordinate+[field_rotated_ordinate[0]], 'bo-')

    plt.show()
    
    