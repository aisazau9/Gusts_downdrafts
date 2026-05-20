import glob
import pandas as pd
import numpy as np

"""
Read Raw AWS data and save variables and time period of interest
"""

# Paths
path_aws  =  "/scratch/up6/ai2733/Data_AWS/" # Raw 1- minute outputs all variables
path_save = "/g/data/up6/ai2733/Gusts_downdrafts/data/"

# General info
cases = ["CASE1", "CASE2_new", "CASE3_new"]

date_cases    = {"CASE1": ("2015-12-15", "2015-12-16"), 
                 "CASE2_new": ("2009-01-19","2009-01-20"), 
                 "CASE3_new": ("2017-02-16","2017-02-17")}

station_cases = {"CASE1": "053115", 
                 "CASE2_new": "072150", 
                 "CASE3_new": "055325"}

name_cases    = {"CASE1": "Moree Aero",
                 "CASE2_new": "Wagga Wagga", 
                 "CASE3_new": "Tamworth Airport"}

def read_aws_raw(path_file, order_cols = 1):
    """
    Function to read raw AWS data from BOM
    """
    
    name_cols = {' Year Month Day Hour Minutes in YYYY.1':"year",
        'MM.1':'month',
        'DD.1':'day',
        'HH24.1':'hour',
       'MI format in Universal coordinated time':'minute',
       'Air Temperature in degrees Celsius':"ta[C]",
       'Dew point temperature in degrees Celsius':"td[C]",
       'Wind (1 minute) speed in km/h':"ws[km/h]",
       'Highest maximum 3 sec wind gust in last 1 minutes in km/h where observations count >= 0':"max_ws[km/h]",
       'Average direction of wind in last 1 minutes in degrees true where observations count >= 0':"wd[deg]",
       'Wind (1 minute) direction in degrees true': "wd[deg]",
       'Mean sea level pressure in hPa':"mslp[hPa]", 
       'Precipitation since last (AWS) observation in mm':"prec[mm]", 
        'Quality of precipitation since last (AWS) observation value':"q_prec"}
    
    if order_cols == 1: 
        cols_read = [7,8,9,10,11,12,13,15,17,19,21,23,29]
    else: # In some files, wind speed is in a different position
        cols_read = [7,8,9,10,11,12,13,15,17,19,21,24,29]
        
    # Read raw data
    df = pd.read_csv(path_file,usecols = cols_read,low_memory=False)
    # Relabel the columns & replace the default index with a datetime index
    df.columns = [name_cols[col] for col in list(df.columns)]
    df.index = pd.to_datetime(df[["year",'month','day','hour','minute']])
    # Convert any strings that look like numbers to numbers 
    df2 = df.apply(pd.to_numeric, errors = 'coerce')
    df2.drop(["year",'month','day','hour','minute'], axis = 1, inplace = True)
    # Quality columns cannot be numbers, so add them "raw":
    if "q_prec" in df2.columns: df2["q_prec"] = df["q_prec"]
    del df
    return df2

# Paths: Raw data (1 minute --- Not quality checked)
path_cases_aws   = {}
for case in cases:
    path_cases_aws[case]   = glob.glob(f"{path_aws}/*{station_cases[case]}*")[0]

# Read and save
df_aws     = {}
df_aws_all = {}
for case in cases:
    df_aws_all[case] = read_aws_raw(path_cases_aws[case], order_cols = 1 if case not in ["CASE4", "CASE5"] else 2)
    df_aws[case]     = df_aws_all[case].loc[date_cases[case][0]:date_cases[case][1]]
    df_aws[case].to_csv(f"{path_save}/AWS/AWS_{case}.csv")