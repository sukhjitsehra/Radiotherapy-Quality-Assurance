from field import Field

# Load the test field
f = Field("/Users/armin/Desktop/Banafshe/project/test/Radiotherapy-Quality-Assurance/notebooks/modelling/SimpleTestField.json.json")

# Display key outputs
print("Field ID:", f.field_ID)
print("Total Area:", f.total_area)
print("Max Span:", f.span)
print("MCS:", f.overall_mcs)
print("Gantry Angles:", f.columns[:5])  # just first few
print("Matrix A sample:")
print(f.matrixA.head())
