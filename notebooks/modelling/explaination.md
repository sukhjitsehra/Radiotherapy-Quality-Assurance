Diffrence between 2D and 3D_complexity :
What it does:
Summarizes each radiation field into one row of features.

How it works:

Iterates through all fields in a day.

For each field, it computes averages or summary statistics:

Mean area

Mean circumference

Mean/overall MCS

Maximum span

Ratio CoA

Plus metadata (machine type, etc.).

Appends these into one flat DataFrame (table).

Shape of data:
Each row = 1 field (treatment plan).
Each column = a metric (e.g., Area, Circumference, MCS, Span, CoA).


What it does:
Keeps the time sequence of control points (up to 180 control points per field).

How it works:

For each field, loops over 180 control points.

At each control point, extracts:

Aperture area

Circumference

Monitor units (MU)

CoA

MCS

Span

Builds a sequence: field_features = [ [area, circ, mu, coa, mcs, span]_t1 , … , _t180 ].

Stores this whole sequence of vectors for each field.

Shape of data:
(n_fields, 180, 6)

n_fields = number of radiation fields

180 = time steps (control points along gantry rotation)

6 = features per control point