# Doc string


def load_2D():
    import os, pandas as pd
    from field import Field

    dates = "C:\\Users\\gfman\\Documents\\RadiationData" # folder that contains all radiation fields
    master = pd.DataFrame()
    for date in os.listdir(dates): # iterate through each day of saved data

        files = dates + "/" + date # folder that contains all the fields for a select day

        mcs = []
        circumferences = []
        areas = []
        spans = []
        coa = []
        ids = []
        drop = []
        for file in os.listdir(files): # iterate over every file from the day
            filename = files + "/" + file # create file name
            id = file[8:15]
            if "MetaData" in file:
                metadata = pd.read_json(filename).set_index("FieldID") # read the metadata of the daily files
                continue
            elif ".txt" in file:
                continue
            try:
                field = Field(filename) # try to make a Field object from the radiation field
            except:
                print("issue")
                continue
            ids.append(field.field_ID)
            areas.append(field.gantry_total_areas.mean())
            circumferences.append(field.aperature_circumference.mean())
            mcs.append(field.overall_mcs)
            spans.append(field.spans.max())
            coa.append(areas[-1]/circumferences[-1]) 
        for id in drop:
            metadata.drop(index = int(id), inplace=True)

        metadata["Area"] = pd.Series(areas, index = ids)
        metadata["Circumference"] = pd.Series(circumferences, index = ids) 
        metadata["MCS"] = pd.Series(mcs, index = ids) 
        metadata['Span'] = pd.Series(spans, index = ids)
        metadata["CoA"] = pd.Series(coa, index = ids)

        master = pd.concat([master, metadata])
    return master

def pad_dataframe(existing_df, n, m):
    import pandas as pd
    # Create a new matrix of size nxm filled with zeros
    padded_df = pd.DataFrame(0, index=range(n), columns=range(m), dtype="float64")
    
    # Determine the size of the existing dataframe
    p = existing_df.shape[0]
    q = existing_df.shape[1]
    
    # Copy the values from the existing dataframe to the padded matrix
    # Note: This will copy the values to the top-left corner of the padded matrix
    padded_df.iloc[:p, :q] = existing_df.iloc[:p, :q]
    
    return padded_df

def load_3D_cm(): # 3D Tensor with complexity metrics
    import pandas as pd, numpy as np, os
    from field import Field
    import math

    features = [] # list for storing matrices
    AD = [] # list for storing AD
    field_id = []

    dates = "C:\\Users\\gfman\\Documents\\RadiationData" # folder that contains all radiation fields

    for date in os.listdir(dates): # iterate through each day of saved data

        files = dates + "/" + date # folder that contains all the fields for a select day

        metadata = pd.read_json(files + "/" + os.listdir(files)[-1]).set_index("FieldID") # read the metadata of the daily files

        for file in os.listdir(files): # iterate over every file from the day
            if "MetaData" in file:
                continue
            elif ".txt" in file:
                continue
            filename = files + "/" + file # create file name
            
            try:
                field = Field(filename) # try to make a Field object from the radiation field

            except:
                continue
            areas = field.gantry_total_areas
            circumferences = field.aperature_circumference
            metric_units = field.aperature_ms
            coas = circumferences/areas*metric_units
            mcs = field.aperature_mcs
            spans = field.spans

            if math.isnan(mcs.mean()):
                    continue # some mcs columns are full of nan's

            field_features = []
            for i in range(180):
                if i >= len(areas):
                    area = areas.mean()
                    circumference = circumferences.mean()
                    mu = metric_units.mean()
                    coa = coas.mean()
                    modulation_cs = mcs.mean()
                    span = spans.mean()
                else:
                    area = areas.iloc[i]
                    circumference = circumferences.iloc[i]
                    mu = metric_units.iloc[i]
                    coa = coas.iloc[i]
                    modulation_cs = mcs.iloc[i]
                    span = spans.iloc[i]
                if math.isnan(modulation_cs):
                    modulation_cs = mcs.mean()

                field_features.append([area,circumference, mu, coa, modulation_cs, span])
                
            features.append(field_features)
            field_id.append(field.field_ID)
        
            AD.append(metadata.loc[field.field_ID, "AD"] > metadata.loc[field.field_ID, "ADPass"]) # append AD from metadata to list

    return np.array(features), np.array(AD)

def load_3D_unstructured():
    import os, pandas as pd, numpy as np
    from field import Field

    features = [] # list for storing matrices
    AD = [] # list for storing AD

    dates = "C:\\Users\\gfman\\Documents\\RadiationData" # folder that contains all radiation fields

    for date in os.listdir(dates): # iterate through each day of saved data

        files = dates + "/" + date # folder that contains all the fields for a select day

        metadata = pd.read_json(files + "/" + os.listdir(files)[-1]).set_index("FieldID") # read the metadata of the daily files

        for file in os.listdir(files): # iterate over every file from the day
            if "MetaData" in file:
                continue
            elif ".txt" in file:
                continue
            filename = files + "/" + file # create file name

            try:
                field = Field(filename) # try to make a Field object from the radiation field

            except:
                continue
            paddedA = pad_dataframe(field.matrixA, 80, 180)
            paddedB = pad_dataframe(field.matrixB, 80, 180)
            
            field_features = []
            for col in paddedA.columns:
                field_features.append(np.dstack((paddedA[col].values,paddedB[col].values)).flatten())

            features.append(field_features)
            
            AD.append(metadata.loc[field.field_ID, "AD"]<metadata.loc[field.field_ID, "ADPass"]) # append AD from metadata to list
                    
    return np.array(features), np.array(AD)


def load_4D():
    import numpy as np
    from field import Field
    features = [] # list for storing matrices
    AD = [] # list for storing AD

    dates = "C:\\Users\\gfman\\Documents\\RadiationData" # folder that contains all radiation fields

    for date in os.listdir(dates): # iterate through each day of saved data

        files = dates + "/" + date # folder that contains all the fields for a select day

        metadata = pd.read_json(files + "/" + os.listdir(files)[-1]).set_index("FieldID") # read the metadata of the daily files

        for file in os.listdir(files): # iterate over every file from the day
            if "MetaData" in file:
                continue
            elif ".txt" in file:
                continue
            filename = files + "/" + file # create file name

            try:
                field = Field(filename) # try to make a Field object from the radiation field

            except:
                continue
            paddedA = pad_dataframe(field.matrixA, max_n, max_m)
            paddedB = pad_dataframe(field.matrixB, max_n, max_m)
            
            field_features = []
            for col in paddedA.columns:
                field_features.append([paddedA[col], paddedB[col]])

            features.append(field_features)
            
            AD.append(metadata.loc[field.field_ID, "AD"]) # append AD from metadata to list

    return np.array(features), np.array(AD)

