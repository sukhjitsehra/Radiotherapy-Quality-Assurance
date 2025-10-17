# Doc string


def load_2D():
    import os, pandas as pd
    from field import Field

    dates = "/Users/armin/Desktop/Banafshe/project/test/Radiotherapy-Quality-Assurance/notebooks/Dataset"  # <-- update this line
    #print(dates) # folder that contains all radiation fields
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
        machine_type = []
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
            except Exception as e:
                print(f"Skipping broken file in load_2D: {filename} - Error: {e}")
                continue
            ids.append(field.field_ID)
            areas.append(field.gantry_total_areas.mean()) # Why mean?
            circumferences.append(field.aperture_circumference.mean())
            mcs.append(field.MCS_arc)
            spans.append(max(field.span))
            coa.append(areas[-1]/circumferences[-1]) 
            machine_type.append(field.machine_type)
        for id in drop:
            metadata.drop(index = int(id), inplace=True)

        metadata["Area"] = pd.Series(areas, index = ids)
        metadata["Circumference"] = pd.Series(circumferences, index = ids) 
        metadata["MCS"] = pd.Series(mcs, index = ids) 
        metadata['Span'] = pd.Series(spans, index = ids)
        metadata["CoA"] = pd.Series(coa, index = ids)
        metadata["MachineType"] = pd.Series(machine_type, index = ids)

        master = pd.concat([master, metadata])
    #print(master)
    # if field is agility, then calculate the span 
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
    print("Loading 3D cm data...")
    import pandas as pd, numpy as np, os
    from field import Field
    import math
    
    features = [] # list for storing matrices
    AD = [] # list for storing AD
    field_id = []

    dates = "/Users/armin/Desktop/Banafshe/project/test/Radiotherapy-Quality-Assurance/notebooks/Dataset" # folder that contains all radiation fields

    for date in os.listdir(dates): # iterate through each day of saved data

        files = dates + "/" + date # folder that contains all the fields for a select day

        # Find the metadata file by name
        metadata = None
        for file in os.listdir(files):
            if "MetaData" in file:
                metadata = pd.read_json(files + "/" + file).set_index("FieldID")
                break
        if metadata is None:
            continue  # skip if no metadata file found

        for file in os.listdir(files): # iterate over every file from the day
            if "MetaData" in file or ".txt" in file:
                continue
            filename = files + "/" + file # create file name
            
            try:
                field = Field(filename) # try to make a Field object from the radiation field
            except:
                continue
            areas = field.gantry_total_areas
            circumferences = field.aperture_circumference
            metric_units = field.aperture_ms
            coas = circumferences/areas*metric_units
            mcs = field.MCS_arc
            spans = field.span
            

            if math.isnan(mcs.mean()):
                continue # some mcs columns are full of nan's
            import numpy as np
            field_features = []
            def get_value(x, i):
                # If x is a scalar, return it; if array/Series, index it
                if isinstance(x, (float, int, np.float64, np.int64)):
                    return x
                try:
                    return x[i]
                except Exception:
                    return np.mean(x)
            
            
            for i in range(180):
                area = areas.mean() if i >= len(areas) else areas.iloc[i]
                circumference = circumferences.mean() if i >= len(circumferences) else circumferences.iloc[i]
                mu = metric_units.mean() if i >= len(metric_units) else metric_units.iloc[i]
                coa = coas.mean() if i >= len(coas) else coas.iloc[i]
                modulation_cs = get_value(mcs, i)
                span = get_value(spans, i)
                if math.isnan(modulation_cs):
                    modulation_cs = np.mean(mcs)
                field_features.append([area, circumference, mu, coa, modulation_cs, span])
                
               
            features.append(field_features)
            field_id.append(field.field_ID)
            
            AD.append(metadata.loc[field.field_ID, "AD"] > metadata.loc[field.field_ID, "ADPass"]) # append AD from metadata to list

    return np.array(features), np.array(AD)

def load_3D_unstructured():
    import os, pandas as pd, numpy as np
    from field import Field

    features = [] # list for storing matrices
    AD = [] # list for storing AD

    dates = "/Users/armin/Desktop/Banafshe/project/test/Radiotherapy-Quality-Assurance/notebooks/Dataset"

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