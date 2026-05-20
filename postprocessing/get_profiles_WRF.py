import numpy as np
import pandas as pd
import wrf
import netCDF4 as nc
from metpy.units import units

"""
Code to get profiles from WRF outputs
"""

# General info
path_wrf_     = "/g/data/w28/ai2733"
path_profiles = "/g/data/up6/ai2733/Gusts_downdrafts/data/Profiles_WRF/"

dates_radiosonde = {
     "CASE1":["2015-12-16 00:00:00","2015-12-16 06:00:00"],
     "CASE2_new":["2009-01-20 00:00:00","2009-01-20 06:00:00"]}

lat_lon_cases = {"CASE1": (-29.49, 149.85), 
                "CASE2_new": (-35.16, 147.46), 
                 "CASE3_new": (-31.07,150.84)}

cases = ["CASE1", "CASE2_new"]

def save_profiles(coarsen, domains): 

    """
    Function to save profiles from WRF outputs (coarsen or original resolution)
    Nearest point to AWS location for each case
    """
    
    for dom in domains:
        # Path where outputs are saved
        path_wrf = {"CASE1": [f"{path_wrf_}/outputs_CASE1/spinup/wrfout_{dom}_2015-12-15_23:35:00",
                              f"{path_wrf_}/outputs_CASE1/wrfout_{dom}_2015-12-16_05:35:00"],
                    "CASE2_new":[f"{path_wrf_}/outputs_CASE2_new/wrfout_{dom}_2009-01-20_00:00:00",
                                f"{path_wrf_}/outputs_CASE2_new/wrfout_{dom}_2009-01-20_05:35:00"]}        
    
        for case in cases:
    
            for date_idx in [0]: # I am just getting the profile for the 00:00
    
                # Read WRF output in date selected
                try:
                    wrfout   = nc.Dataset(path_wrf[case][date_idx])
                except:
                    if case == "CASE1":
                        new_path = path_wrf[case][date_idx].replace("2015-12-15_23:35:00", "2015-12-16_00:00:00")
                        wrfout   = nc.Dataset(new_path)
                        
                times_d3 = wrf.extract_times(wrfout,wrf.ALL_TIMES)
                time_idx = list(times_d3).index(np.datetime64(dates_radiosonde[case][date_idx]))
                print ("Reading file from ", str(times_d3[time_idx]))
                                    
                # Variables of interest
                tc_wrf  = wrf.getvar(wrfout,"tc", timeidx=time_idx)   #Celcius
                hgt_wrf = wrf.getvar(wrfout,"z", timeidx=time_idx)    #m
                p_wrf   = wrf.getvar(wrfout,"p", timeidx=time_idx)    #Pa
                td_wrf  = wrf.getvar(wrfout,"td", timeidx=time_idx)   #Celcius
                u_wrf, v_wrf = wrf.getvar(wrfout,"uvmet", timeidx=time_idx)   #m/s wind components rotated to earth coordinates
                wspd_wrf, wdir_wrf = wrf.getvar(wrfout,"uvmet_wspd_wdir", timeidx=time_idx) # wind direction and speed rotated to earth coordinates
                
                #Extract profiles nearest to AWS
                x_y = wrf.ll_to_xy(wrfout,lat_lon_cases[case][0],lat_lon_cases[case][1])
                x, y = int(x_y.sel(x_y="x").values), int(x_y.sel(x_y="y").values)    
    
                if dom == "d03" and coarsen: # to 5 km 
                    tc_wrf = tc_wrf.coarsen({"south_north":25, "west_east":25}).mean()
                    hgt_wrf = hgt_wrf.coarsen({"south_north":25, "west_east":25}).mean()
                    p_wrf  = p_wrf.coarsen({"south_north":25, "west_east":25}).mean()
                    td_wrf = td_wrf.coarsen({"south_north":25, "west_east":25}).mean()
                    u_wrf  = u_wrf.coarsen({"south_north":25, "west_east":25}).mean()
                    v_wrf  = v_wrf.coarsen({"south_north":25, "west_east":25}).mean()
                    wspd_wrf  = wspd_wrf.coarsen({"south_north":25, "west_east":25}).mean()
                    wdir_wrf  = wdir_wrf.coarsen({"south_north":25, "west_east":25}).mean()
    
                    xlat = np.array(tc_wrf.XLAT)
                    xlong = np.array(tc_wrf.XLONG)
                    y, x = np.unravel_index(((xlat - lat_lon_cases[case][0])**2 + (xlong - lat_lon_cases[case][1])**2).argmin(), xlat.shape)
    
                elif dom == "d02" and coarsen: # to 5 km
                    tc_wrf = tc_wrf.coarsen({"south_north":5, "west_east":5}).mean()
                    hgt_wrf = hgt_wrf.coarsen({"south_north":5, "west_east":5}).mean()
                    p_wrf  = p_wrf.coarsen({"south_north":5, "west_east":5}).mean()
                    td_wrf = td_wrf.coarsen({"south_north":5, "west_east":5}).mean()
                    u_wrf  = u_wrf.coarsen({"south_north":5, "west_east":5}).mean()
                    v_wrf  = v_wrf.coarsen({"south_north":5, "west_east":5}).mean()
                    wspd_wrf  = wspd_wrf.coarsen({"south_north":5, "west_east":5}).mean()
                    wdir_wrf  = wdir_wrf.coarsen({"south_north":5, "west_east":5}).mean()
    
                    xlat = np.array(tc_wrf.XLAT)
                    xlong = np.array(tc_wrf.XLONG)
                    y, x = np.unravel_index(((xlat - lat_lon_cases[case][0])**2 + (xlong - lat_lon_cases[case][1])**2).argmin(), xlat.shape)
                    
                for log_space in [True,False]:
    
                    if log_space:
                        #Extract profiles but decrease spacing to log-p for nice wind barb spacing
                        xp = np.flip(p_wrf.sel(west_east=x,south_north=y).values)
                        yp = np.flip(p_wrf.bottom_top.values)
                        xi = np.logspace(3,2,20) * 100
    
                        pind = np.interp(xi,xp,yp).round().astype(int)    
    
                        #Take wrf grids and output arrays with units, but with log spacing in vertical (for nice wind barb spacing)
                        p_out  = p_wrf.sel(west_east=x,south_north=y,bottom_top=pind).values/100 * units.hectopascal
                        tc_out = tc_wrf.sel(west_east=x,south_north=y,bottom_top=pind).values * units.degree_Celsius
                        td_out = td_wrf.sel(west_east=x,south_north=y,bottom_top=pind).values * units.degree_Celsius    
                        hgt_out = hgt_wrf.sel(west_east=x,south_north=y,bottom_top=pind).values * units.meter
                        u_out   = u_wrf.sel(west_east=x,south_north=y,bottom_top=pind).values * units.meter_per_second
                        v_out   = v_wrf.sel(west_east=x,south_north=y,bottom_top=pind).values * units.meter_per_second
                        wspd_out = wspd_wrf.sel(west_east=x,south_north=y,bottom_top=pind).values * units.meter_per_second
                        wdir_out = wdir_wrf.sel(west_east=x,south_north=y,bottom_top=pind).values * units.deg
    
                    else: #All pressure levels
                        p_out   = p_wrf.sel(west_east=x,south_north=y).values/100 * units.hectopascal
                        tc_out  = tc_wrf.sel(west_east=x,south_north=y).values * units.degree_Celsius
                        td_out  = td_wrf.sel(west_east=x,south_north=y).values * units.degree_Celsius    
                        hgt_out = hgt_wrf.sel(west_east=x,south_north=y).values * units.meter
                        u_out   = u_wrf.sel(west_east=x,south_north=y).values * units.meter_per_second
                        v_out   = v_wrf.sel(west_east=x,south_north=y).values * units.meter_per_second
                        wspd_out = wspd_wrf.sel(west_east=x,south_north=y).values * units.meter_per_second
                        wdir_out = wdir_wrf.sel(west_east=x,south_north=y).values * units.deg
    
                    # Create dataframe and save as csv
                    wrf_profile = pd.DataFrame()
                    wrf_profile["p [hPa]"] = p_out
                    wrf_profile["tc [C]"]  = tc_out
                    wrf_profile["td [C]"]  = td_out
                    wrf_profile["hgt [m]"] = hgt_out
                    wrf_profile["u [m/s]"] = u_out
                    wrf_profile["v [m/s]"] = v_out
                    wrf_profile["wspd [m/s]"] = wspd_out
                    wrf_profile["wdir [deg]"] = wdir_out
    
                    if coarsen:
                        wrf_profile.to_csv(f"{path_profiles}/ProfileAWS_{case}_{str(times_d3[time_idx])[:16]}_logspace{log_space}_{dom}_coarsen5km.csv")
                    else:
                        wrf_profile.to_csv(f"{path_profiles}/ProfileAWS_{case}_{str(times_d3[time_idx])[:16]}_logspace{log_space}_{dom}.csv")
    
                    print (f"ProfileAWS_{case}_{str(times_d3[time_idx])[:16]}_logspace{log_space}_{dom}.csv SAVED")
                    
                del wrfout

# Save profiles original grid
save_profiles(coarsen = False, domains = ["d03"])

# Save profiles coarsen to 5 km
save_profiles(coarsen = True,  domains = ["d01", "d02", "d03"])