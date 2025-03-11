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
        self.mq_control_points = field_info["mqControlPoints"]
        self.beam_energy = field_info["beamEnergy"]
        self.is_fff = field_info["isFff"]
        self.bolus_status = field_info["bolusStatus"]
        self.has_bolus = field_info["hasBolus"]
        self.__set_leaf_activity_interval()
        self.__create_matrix()
        if self.machine_type == "Agility":
            self.leaf_width = 0.5
        else:
            self.leaf_width = 0.5
        length_matrix = self.matrixA + self.matrixB
        areas_matrix = length_matrix*self.leaf_width
        self.__set_gantry_total_areas(areas_matrix)
        self.__set_span()
        self.__set_MU()
        self.__set_circumference()
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

    
    def __create_matrix(self):
        """
        converts the field information from dictionairy for to a matrix with
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

        index = []

        for segment in self.mq_control_points:
            index.append(segment["gantryAngle"])
            matrixA = pd.concat([matrixA, pd.Series(segment["leafSetA"])], axis = 1)
            matrixB = pd.concat([matrixB, pd.Series(segment["leafSetB"])], axis = 1)


        self.columns = index
        matrixA.columns = index
        matrixB.columns = index
        self.matrixA = matrixA.loc[self.active_leaf_start:self.active_leaf_end]
        self.matrixB = matrixB.loc[self.active_leaf_start:self.active_leaf_end]

        return
    
    def __set_MU(self):
        import pandas as pd
        cum_ms = []

        total_ms = self.beam_meterset
        for aperature in self.mq_control_points:
            cum_ms.append(aperature['cumulativeMetersetWeight'])

        cum_ms = pd.Series(cum_ms, index = self.columns)
        prop_ms = cum_ms.diff()
        prop_ms[self.columns[0]] = 0

        self.aperature_ms = prop_ms*total_ms 

    def __determine_leaf_width(self):
        """
        determines the width of the collimator leaves
        (under the assumption that all leaves share the same width)
        ----------------------------------------------------------
        Returns
            leaf_width (float) - the width of the collimator leaves
        """

        control_points = self.mq_control_points

        lengthY = control_points[0]["fieldY"]
        num_leaves = control_points[0]["mlcLeaves"]

        leaf_width = lengthY/num_leaves
        return leaf_width
    
    def __set_total_area(self):
        return self.leaf_total_areas.sum()

    def __set_leaf_average_areas(self):

        self.leaf_average_areas = self.areas_matrix.T.mean()
        return
    
    def __set_leaf_total_areas(self):
        self.leaf_total_areas =  self.areas_matrix.T.sum()
        return
    
    def __set_gantry_average_areas(self, areas):
        self.gantry_average_areas =  areas.mean()
        return

    def __set_gantry_total_areas(self, areas_matrix):
        self.gantry_total_areas = areas_matrix.sum()
        return 
    
    def __set_leaf_activity_interval(self):
        active_leaf_start = int(self.mq_control_points[0]["mlcLeaves"]//2 - self.mq_control_points[0]["collimatorX1"]/0.5) # first leaf outside jaw
        active_leaf_end = int(self.mq_control_points[0]["mlcLeaves"]//2 + self.mq_control_points[0]["collimatorX2"]/0.5)
        
        self.active_leaf_start = active_leaf_start
        self.active_leaf_end = active_leaf_end

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
        
        num_cp = len(self.mq_control_points)
        max_span = 0

        spans = []

        for i in range(num_cp):
            max_span = 0
            if self.machine_type == "Agility":
                Y1 = self.matrixA.max().max()
                Y2 = self.matrixB.max().max()
            else:
                Y1 = self.mq_control_points[0]["collimatorY1"]
                Y2 = self.mq_control_points[0]["collimatorY2"]
            X1 = self.mq_control_points[0]["collimatorX1"]
            X2 = self.mq_control_points[0]["collimatorX2"]
            collimatorAngle = self.mq_control_points[i]["collimatorAngle"]*math.pi/180
            span = self.__calc_span(self.machine_type, collimatorAngle,
                                    X1, X2, Y1, Y2)
            spans.append(span)
            
        import pandas as pd
        self.spans = pd.Series(spans, index = self.columns)

    def __set_circumference(self):
        matrixA = self.matrixA.T
        rightA = matrixA.iloc[:,1:]
        rightA.columns = matrixA.columns[:-1]

        leftA = matrixA.iloc[:, :-1]
        leftA.columns = matrixA.columns[1:]

        left_diffA = abs(matrixA.iloc[:,1:] - leftA) 
        left_diffA[self.active_leaf_start] = 0

        right_diffA = abs(matrixA.iloc[:,:-1] - rightA)
        right_diffA[self.active_leaf_end] = 0 

        circumferenceA  = 1/2*(left_diffA+ right_diffA) + self.leaf_width

        matrixB = self.matrixB.T
        rightB = matrixB.iloc[:,1:]
        rightB.columns = matrixB.columns[:-1]

        leftB = matrixB.iloc[:, :-1]
        leftB.columns = matrixB.columns[1:]

        left_diffB = abs(matrixB.iloc[:,1:] - leftB) 
        left_diffB[self.active_leaf_start] = 0

        right_diffB = abs(matrixB.iloc[:,:-1] - rightB)
        right_diffB[self.active_leaf_end] = 0 

        circumferenceB  = 1/2*(left_diffB+ right_diffB) + self.leaf_width

        total_circumference = circumferenceA + circumferenceB

        aperature_circumference = total_circumference.T.sum() + self.matrixA.iloc[0] + self.matrixB.iloc[0] + self.matrixA.iloc[-1] + self.matrixB.iloc[-1]

        self.aperature_circumference = aperature_circumference

    def __set_MCS(self):
        
        pos_a = self.matrixA
        pos_b = self.matrixB

        pos_max_a = pos_a.max() - pos_a.min()
        pos_max_b = pos_b.max() - pos_b.min()
        n = pos_a.shape[0]

        lsv_a = (pos_max_a - pos_a.diff()).sum()/((n)*pos_max_a)
        lsv_b = (pos_max_b - pos_b.diff()).sum()/((n)*pos_max_b)

        lsv_segment = lsv_a * lsv_b

        aav = (pos_a + pos_b).sum()/(pos_a.T.max() + pos_b.T.max()).sum()

        mcs_beam = (aav * lsv_segment * self.aperature_ms).sum()

        self.aperature_mcs = aav * lsv_segment * self.aperature_ms
        self.overall_mcs = mcs_beam

    









        