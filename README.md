Project Instructions
==============================

## Dataset:

- First method to get the dataset used for this project was local to violet's computer, the link is: ![Violets Data OneDrive](). This was primiarly used by George (308 fields) and now new updates were added and it is (2800 fields). 

- Second method is huggingface dataset that is continously being updated by Harry.

## Python Environment

- Python version used is `3.9.23`

## Directory Structure
------------

    ├── README.md          <- The top-level README for describing highlights for using this ML project.
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention should snake case.
    │      └──  Dataset     <- Contains the dataset used in the project in JSON format.>
           └──  modelling <- Contains the model training notebook.
                └──  data_creator.py <- To creating dataframe for JSON file, so update the folder location of the dataset. We usually call this in other files. 
                └──  EDA.ipynb <- Contains the exploratory data analysis notebook. this will call data_Creator.py files. 
                └──  new_data_models_with_transformation.ipynb <- Contains the models
    │      └──  pre-processing_and_feature_engineering <- Contains the pre-processing and feature engineering notebook. 
    ├── Previous            
    │   └── PDF files        <- George Files
    |
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    |
    ├── LICENSE  <- LICENSE terms to be included for the use of the source code distribution



