from math import pi, sin, cos

class Field():

    def __init__(self, file_name):

        self.file = file_name
        field_info = self.__import_field(file_name)
        self.field_ID = field_info["fieldId"]
        self.name = field_info["name"]
        self.description = field_info["description"]
        self.machine_type = field_info["machineType"]
        self.machine_name = field_info["machineName"]
        self.type = field_info["type"]
        self.mq_type = field_info["mqType"]
        self.isocentre = field_info["isocentre"]
        self.beam_meterset = field_info["beamMeterset"]
        self.cp = field_info["mqControlPoints"]
        self.ncontrolpoints = len(self.cp)
        self.collimatorAngle = self.cp[0]["collimatorAngle"]
        self.collimatorAngleRad = self.cp[0]["collimatorAngle"]*pi/180
        self.beam_energy = field_info["beamEnergy"]
        self.is_fff = field_info["isFff"]
        self.bolus_status = field_info["bolusStatus"]
        self.has_bolus = field_info["hasBolus"]
        if self.machine_type == "Agility":
            self.nleafs = 80
            self.leaf_width = [0.5]*self.nleafs #Why 0.5 for the leaf?
            self.leafblade_positions = [(pos+0.5)/2-20.0 for pos in range(80)] # arranged from negative to positive
        else: # for Varian MLC
            self.nleafs=60
            self.leaf_width = [1.0]*10+[0.5]*40 + [1.0]*10
            self.leafblade_positions = ([(pos+0.5) - 20.0 for pos in range(10)] +  
                                        [(pos+0.5)/2 - 10.0 for pos in range(40)] + 
                                        [(pos+1.0) + 9.5 for pos in range(10)]) # arranged from negative to positive
        
        self.__get_exposed_leafs()
        self.__create_matrix()
        self.__calc_span()
        import pandas as pd

        length_matrix = self.matrixA + self.matrixB # [-1.3, 2.4] -> length = 1.1

        leaf_width_series = pd.Series(self.leaf_width, index=range(1, self.nleafs + 1))
        leaf_width_series = leaf_width_series.loc[self.matrixA.index]  # [0.5, 0.5, ..., 0.5]

        self.areas_matrix = length_matrix.multiply(leaf_width_series, axis=0)
        self.__set_leaf_total_areas()
        self.__set_leaf_average_areas()
        self.__set_gantry_total_areas(self.areas_matrix)
        self.__set_gantry_average_areas(self.gantry_total_areas)
        self.total_area = self.__set_total_area()
        self.__set_circumference()
        #self.__set_MCS()

        leafgaps = self.matrixA + self.matrixB # contains the tip-to-tip distances for all control points (including some behind the jaws)
        #areas_matrix = length_matrix*self.leaf_width
        #self.__set_gantry_total_areas(areas_matrix)
        self.__calc_span()
        self.__set_MU()
        
        #self.__set_LSV()
        self.__compute_LSV()
        self.__compute_AAV()
        self.__set_MCS()


    
    def __import_field(self, file_name):
        """
        imports the field information from the file name
        ------------------------------------------------
        Parameters
            file_name (str) - the name of the file to import from

        Returns
            field_info (dict) - the information for the field

        """
        import json

        if not isinstance(file_name, str):
            print("Error __import_field: file_name must be a string")

        if not file_name.endswith(".json"):
            print("Error __import_field: make sure file is json format")

        with open(file_name, "r") as f:
            field_info = json.load(f)

        return field_info

#THIS WORKS!!! Tested with difrent fields and it is correct !!!
    
    def __create_matrix(self):
        """
        converts the field information from dictionairy for to a dataframe with
        gantry angles indexing the columns and leaf numbers indexing the rows. 
        Adds the matrices to the field object.

        ---------------------------------------------------------------------
        Attributes
            None
        Returns 
            None
        """

        import pandas as pd
        import warnings

        matrixA = pd.DataFrame()
        matrixB = pd.DataFrame()

        gantryangle = []

        for segment in self.cp:
            gantryangle.append(segment["gantryAngle"]) # segment["gantryAngle"] is an integer
            matrixA = pd.concat([matrixA, pd.Series(segment["leafSetA"])], axis = 1)
            matrixB = pd.concat([matrixB, pd.Series(segment["leafSetB"])], axis = 1)


        self.columns = gantryangle # the column names are now integers? 
        matrixA.columns = gantryangle
        matrixB.columns = gantryangle

        matrixA.index = range(1,self.nleafs+1) # The row index indicates the leaf number starting at 1
        matrixB.index = range(1,self.nleafs+1)
        # matrixB.reindex(axis='index', level=0, labels=list(range(self.nleafs)+1) # Why does this not work?
                        
        # We checked that the indexing is correct
        self.matrixA = matrixA.loc[min(self.exposed_leaf_start):max(self.exposed_leaf_end)]
        self.matrixB = matrixB.loc[min(self.exposed_leaf_start):max(self.exposed_leaf_end)]


        return
    



    

        
        

#THIS WORKS!!! Tested with difrent fields and it is correct !!!
    
    def __set_total_area(self):
        return self.leaf_total_areas.sum()

    def __set_leaf_average_areas(self):

        self.leaf_average_areas = self.areas_matrix.T.mean()
        return
    
    def __set_leaf_total_areas(self):
        self.leaf_total_areas =  self.areas_matrix.T.sum()
        return
    
    def __set_gantry_average_areas(self, areas_matrix):
        self.gantry_average_areas =  areas_matrix.mean()
        return

    def __set_gantry_total_areas(self, areas_matrix):
        self.gantry_total_areas = areas_matrix.sum()
        return 
    
    def __get_exposed_leafs(self):
        """ 
        Reports the exposed leafs (not behind a jaw) 
        - for Elekta: counting from the top JSON leaf 1 (top = positive y-values)
        - for Varian: counting from the bottom JSON leaf 1
        
        """

        if self.machine_type == "Agility":
            #exposed_leaf_start = [int(seg["mlcLeaves"]/2 - seg["collimatorX1"]/self.leaf_width[0] + 1) for seg in self.cp] 
            #exposed_leaf_end = [int(seg["mlcLeaves"]/2 + seg["collimatorX2"]/self.leaf_width[0]) for seg in self.cp]
            
            exposed_leaf_start = [smallest_larger_than(self.leafblade_positions, seg["collimatorX1"]) for seg in self.cp]
            exposed_leaf_start = [80 - l + 1 for l in exposed_leaf_start]
            exposed_leaf_end = [smallest_larger_than(self.leafblade_positions, seg["collimatorX2"]) for seg in self.cp]

            # '1' is the first leaf here, 'X1' is the top jaw, the retrieved leaf numbers using smallest_larger_than() start from 0

        else:
            exposed_leaf_start = [smallest_larger_than(self.leafblade_positions, -1.0*seg["collimatorY1"]) for seg in self.cp]
            exposed_leaf_start = [l + 1 for l in exposed_leaf_start] # the retrieved leaf numbers from smallest_larger_than() start from 0
            exposed_leaf_end = [smallest_larger_than(self.leafblade_positions, seg["collimatorY2"]) for seg in self.cp]
            # no leaf number adjustment necessary here

        self.exposed_leaf_start = exposed_leaf_start # leaf numbers starting from 1
        self.exposed_leaf_end = exposed_leaf_end

        return
    
    def __set_leaf_travel(self):
        import pandas as pd

        leaf_travel = []
        for i in self.matrixA.index:
            travel = abs(self.matrixA.loc[i].diff()).sum()
            leaf_travel.append(travel)

        self.leafA_travel = pd.Series(leaf_travel, index = self.matrixA.index)

        leaf_travel = []
        for i in self.matrixB.index:
            travel = abs(self.matrixB.loc[i].diff()).sum()
            leaf_travel.append(travel)

        self.leafB_travel = pd.Series(leaf_travel, index = self.matrixB.index)

        return 
    
    def __calcAlpha(self, ordinate, abscissa):
        import math
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
        
    
    """
    def __calc_span(self, machine_type, collimatorAngle, X1, X2, Y1 = None, Y2 = None):
        import math
        # machine_type == Agility: X1, X2 are the "top" and "bottom" jaws, "Y1" and "Y2" are the imaginary left and right jaws (to be replaced by the maxima of LeafbankB and LeafbankA respectively)

        if machine_type == "Agility":
        
            alpha1 = self.__calcAlpha(Y1, X1) #UR
            alpha2 = self.__calcAlpha(-Y2, X1)  #UL
            alpha3 = self.__calcAlpha(-Y2, -X2) #BL
            alpha4 = self.__calcAlpha(Y1, -X2) #BR
            
            radius2 = math.sqrt(math.pow(X1,2)+math.pow(Y2,2)) #UR
            radius1 = math.sqrt(math.pow(X1,2)+math.pow(-Y1,2)) #UL
            radius4 = math.sqrt(math.pow(-X2,2)+math.pow(-Y1,2)) #BL
            radius3 = math.sqrt(math.pow(-X2,2)+math.pow(Y2,2)) #BR
            
        elif machine_type == "TrueBeam":
            alpha1 = self.__calcAlpha(X2, Y2) #UR
            alpha2 = self.__calcAlpha(-X1, Y2)  #UL
            alpha3 = self.__calcAlpha(-X1, -Y1) #BL
            alpha4 = self.__calcAlpha(X2, -Y1) #BR
            
            radius1 = math.sqrt(math.pow(Y2,2)+math.pow(X2,2)) #UR
            radius2 = math.sqrt(math.pow(Y2,2)+math.pow(-X1,2)) #UL
            radius3 = math.sqrt(math.pow(-Y1,2)+math.pow(-X1,2)) #BL
            radius4 = math.sqrt(math.pow(-Y1,2)+math.pow(X2,2)) #BR            
            
        ### calculate the rotated field edges
        # collimatorAngle needs to be in radians units
        UR_rotated = [radius1*math.cos(math.radians(alpha1)+collimatorAngle), radius1*math.sin(math.radians(alpha1)+collimatorAngle)]
        UL_rotated = [radius2*math.cos(math.radians(alpha2)+collimatorAngle), radius2*math.sin(math.radians(alpha2)+collimatorAngle)]
        BL_rotated = [radius3*math.cos(math.radians(alpha3)+collimatorAngle), radius3*math.sin(math.radians(alpha3)+collimatorAngle)]
        BR_rotated = [radius4*math.cos(math.radians(alpha4)+collimatorAngle), radius4*math.sin(math.radians(alpha4)+collimatorAngle)]
        
        field_rotated = [UR_rotated, UL_rotated, BL_rotated, BR_rotated]
        field_rotated_ordinate = [corner[1] for corner in field_rotated]
        
        span = max(field_rotated_ordinate) - min(field_rotated_ordinate)
            #print('span = ', span)
            
        return span

    def __set_span(self):
        import math
        
        num_cp = len(self.cp)
        max_span = 0

        spans = []

        for i in range(num_cp):
            max_span = 0
            if self.machine_type == "Agility":
                Y1 = self.matrixA.max().max()
                Y2 = self.matrixB.max().max()
            else:
                Y1 = self.cp[0]["collimatorY1"]
                Y2 = self.cp[0]["collimatorY2"]
            X1 = self.cp[0]["collimatorX1"]
            X2 = self.cp[0]["collimatorX2"]
            collimatorAngle = self.cp[i]["collimatorAngle"]*math.pi/180
            span = self.__calc_span(self.machine_type, collimatorAngle,
                                    X1, X2, Y1, Y2)
            spans.append(span)
            
        import pandas as pd
        self.spans = pd.Series(spans, index = self.columns)

    """
    def __calc_span(self):  # calculates the maximum vertical span
        import numpy as np
        alpha = -1.0 * self.collimatorAngleRad  # projecting onto vertical axis (y-axis)
        unitvector = np.array([sin(alpha), cos(alpha)])

        for segmentno in range(self.ncontrolpoints):
            gantry_angle = self.matrixA.columns[segmentno]
            start = self.exposed_leaf_start[segmentno]
            end = self.exposed_leaf_end[segmentno]

            # Extract leaf positions
            xvalsA = self.matrixA.loc[start:end, gantry_angle]
            xvalsB = self.matrixB.loc[start:end, gantry_angle]

            if self.machine_type == "Agility":
                # Elekta: invert B bank and reverse y-axis indexing
                xvalsB = -xvalsB
                yvals = self.leafblade_positions[::-1][start - 1:end]
                
            else:
                # Varian: direct indexing
                yvals = self.leafblade_positions[start - 1:end]

            # Form tip vectors and project onto axis defined by collimator angle
            leaftipvectorsA = np.array(list(zip(xvalsA, yvals)))
            leaftipvectorsB = np.array(list(zip(xvalsB, yvals)))

            dot_products_A = leaftipvectorsA @ unitvector
            dot_products_B = leaftipvectorsB @ unitvector

            self.cp[segmentno].update({'spanMin': min(*dot_products_A, *dot_products_B)})
            self.cp[segmentno].update({'spanMax': max(*dot_products_A, *dot_products_B)})

        cpspans = [seg['spanMax'] - seg['spanMin'] for seg in self.cp]
        self.span = cpspans

    def __compute_AAV(self):
        import numpy as np

        matrixA = self.matrixA.values.T  # shape: (num_cp, num_leaves)
        matrixB = self.matrixB.values.T

        aperture_diff = matrixA + matrixB  # shape: (num_cp, num_leaves)
        numerators = np.sum(aperture_diff, axis=1)  # one per CP

        max_A = np.max(matrixA, axis=0)
        max_B = np.max(matrixB, axis=0)
        denominator = np.sum(max_A + max_B)

        if denominator == 0:
            denominator = 1e-8

        AAV_cp = numerators / denominator
        self.AAV_cp = AAV_cp



    def __compute_LSV(self):
        import numpy as np

        def lsv_bank(bank_matrix):
            bank_matrix = bank_matrix.T  # shape = (num_cp, num_leaves)

            N = bank_matrix.shape[1]  # number of leaves
            pos_diff = np.abs(np.diff(bank_matrix, axis=1))
            p_max = np.max(bank_matrix, axis=1) - np.min(bank_matrix, axis=1)
            p_max = np.where(p_max == 0, 1e-8, p_max)
            numerator = np.sum(p_max[:, np.newaxis] - pos_diff, axis=1)
            lsv = numerator / ((N - 1) * p_max)
            return lsv

        lsvA = lsv_bank(self.matrixA.values)
        lsvB = lsv_bank(self.matrixB.values)
        self.LSV_cp = lsvA * lsvB

        
    def __set_MCS(self):
        import numpy as np
        import pandas as pd

        AAV = self.AAV_cp
        LSV = self.LSV_cp
        mu_weights = self.mu_weights.values  # normalized MU weights (length = num_cp)

        MCS_values = []
        cp_labels = []

        for i in range(len(AAV) - 1):
            avg_AAV = (AAV[i] + AAV[i + 1]) / 2
            avg_LSV = (LSV[i] + LSV[i + 1]) / 2
            mu_fraction = mu_weights[i + 1]  # corresponds to MU between CP_i and CP_{i+1}
            MCS_values.append(avg_AAV * avg_LSV * mu_fraction)
            cp_labels.append(f"CP{i}-{i+1}")

        self.MCS_terms = pd.Series(MCS_values, index=cp_labels)

        self.MCS_arc = round(np.sum(MCS_values), 6)
        








#THIS WORKS!!! Tested with different fields and it is correct !!!
    def __set_circumference(self):
        import pandas as pd
        leaf_width_series = pd.Series(self.leaf_width, index=range(1, self.nleafs + 1))
        leaf_width_series = leaf_width_series.loc[self.matrixA.index]
        perimeters = []
        # Initialize Series for each control point
        
        for angle in self.matrixA.columns:
            a = self.matrixA[angle]
            b = self.matrixB[angle]
            gaps= a + b  # tip-to-tip distances for all control points
            gaps = (a + b).loc[a + b > 0]
            #print("gaps", gaps)
            if gaps.empty:
                perimeters.append(0)
                continue
           
            
            # Sum of vertical edges
            vertical_jumps = gaps.diff().abs().iloc[1:].sum()
            # Add horizontal edges (top + bottom leaf opening)
            horizontal = gaps.iloc[0] + gaps.iloc[-1]
            n_leaves = len(gaps)
            vertical_sides = 2 * n_leaves * leaf_width_series.iloc[0]  # constant width
            P = horizontal + vertical_jumps + vertical_sides
            perimeters.append(P)

        self.aperture_circumference = pd.Series(perimeters, index=self.matrixA.columns)
        
      

    def __set_MU(self):
    # """Calculates the monitor units (MUs) delivered at each control point
    #     and stores both raw MU and normalized weights (w_i)."""
        import pandas as pd
        # Step 1: Extract cumulativeMetersetWeight from each control point
        cum_ms = [cp['cumulativeMetersetWeight'] for cp in self.cp]
    # Step 2: Convert to Series indexed by gantry angles
        cum_ms_series = pd.Series(cum_ms, index=self.columns)
    # Step 3: Compute MU delivered at each segment as the difference in CMW    
        mu_diff = cum_ms_series.diff().fillna(0)
    # Step 4: Scale by total MUs delivered for the field
        mu_diff = mu_diff * self.beam_meterset
        self.aperture_ms = mu_diff
    # Step 5: Normalize MUs to get weights
        self.mu_weights = mu_diff / (mu_diff.sum())

    

        
        


def smallest_larger_than(lst, a):
    """
    With thanks to chatGPT
    returns the index in the list lst containing the smallest element larger than a. 

    :param lst: 
    :type lst: integer or float
    :param a: Description
    :type a: 
    :return: Description
    :rtype: int | None
    """
    
    filtered_indices = [i for i, x in enumerate(lst) if x > a]
    if not filtered_indices:
        return None
    smallest_index = min(filtered_indices, key=lambda i: lst[i])
    return smallest_index