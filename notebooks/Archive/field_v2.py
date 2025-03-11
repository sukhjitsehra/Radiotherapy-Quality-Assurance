class Field():

    def __init__(self, file_name):
        
        self.file = file_name
        field_info = self.__import_field(file_name)
        self.field_ID = field_info["fieldId"]
        # self.name = field_info["name"]
        # self.description = field_info["description"]
        # self.machine_type = field_info["machineType"]
        # self.machine_name = field_info["machineName"]
        # self.type = field_info["type"]
        # self.mq_type = field_info["mqType"]
        # self.isocentre = field_info["isocentre"]
        self.beam_meterset = field_info["beamMeterset"]
        self.mq_control_points = field_info["mqControlPoints"]
        # self.beam_energy = field_info["beamEnergy"]
        # self.is_fff = field_info["isFff"]
        # self.bolus_status = field_info["bolusStatus"]
        # self.has_bolus = field_info["hasBolus"]
        self.__set_leaf_activity_interval()
        self.__create_matrix()
        # if self.machine_type == "Agility":
        #     self.leaf_width = 0.5
        # else:
        self.leaf_width = 0.5
        #     #self.leaf_width = self.__determine_leaf_width()
        self.length_matrix = self.matrixA + self.matrixB
        self.areas_matrix = self.length_matrix*self.leaf_width
        # # self.__set_leaf_average_areas()
        # # self.__set_leaf_total_areas()
        self.__set_gantry_average_areas()
        self.__set_gantry_total_areas(areas_matrix)
        # # self.__set_total_area()
        # # self.__set_leaf_travel()
        # self.__set_span()
        self.__set_MU()
    
    
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

        self.aperature_ms = prop_ms 

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
    
    def __set_gantry_average_areas(self):
        self.gantry_average_areas =  self.areas_matrix.mean()
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
    
    def __set_span(self):
        import math
        
        num_cp = len(self.mq_control_points)
        max_span = 0

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
            if collimatorAngle > 180:
                collimatorAngle = 360 - collimatorAngle
            if X1 ==0 or X2 == 0:
                alpha1 = 0
                alpha2 = 0
            else:
                if self.machine_type == "Agility":
                    alpha1 = math.atan(X1/Y2)
                    alpha2 = math.atan(X2/Y1)
                else:
                    alpha1 = math.atan(X1/Y2)
                    alpha2 = math.atan(X2/Y1)
            R1 = math.sqrt(math.pow(X1,2)+math.pow(Y2,2))
            R2 = math.sqrt(math.pow(X2,2)+math.pow(Y1,2))
            CornerY1 = R1*math.sin(alpha1+collimatorAngle)
            CornerY2 = R2*math.sin(-(alpha2+collimatorAngle))
            span = abs(CornerY2)+abs(CornerY1)
            if span > max_span:
                max_span = span
            
        self.max_span = max_span

        