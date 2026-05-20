import numpy as np
import sys
import pickle

"""
This script identifies the strongest updrafts and downdrafts in WRF vertical velocity (wa)
within 80 km of AWS locations using coarsened 3D arrays.

For a selected case (CASE1, CASE2_new, CASE3_new) and domain (d02 or d03), the script:
1. Loads coarsened WRF arrays of vertical velocity (wa) and temperature.
2. Separates updrafts and downdrafts.
3. Identifies the strongest drafts using a fixed threshold (e.g., 5 m/s) or percentile.
4. Splits drafts into above-freezing and below-freezing regions based on temperature.
5. Stores the strongest drafts and their indexes (time, south_north, west_east).
6. Saves the results as pickle files for later analysis.

Input: case id, domain

"""

path_arrays = "/scratch/up6/ai2733/arrays_mp/"
dom_      = str(sys.argv[1]) # d02 or d03

case_     = "CASE2_new_testmp"

thr_fixed = 5. # m/s
prefix = f"new{int(thr_fixed)}_" if type(thr_fixed) == float else f"{str(thr_fixed_)}" # Percentile or fixed threshold
stages = ["All"]

index_stages_all = {
 'CASE2_new_testmp': {'All': [0, None]},
}

def get_strongest(wa, aux_temp, above_freezing=True, up=True):
    
    if above_freezing:
        mask = aux_temp <= 273.15
    else:
        mask = aux_temp > 273.15

    wa_masked = np.where(mask, wa, np.nan)

    if type(thr_fixed) == float:
        thr = 1.*thr_fixed if up else -1*thr_fixed
    else: # percentile 99
        if "per" in thr_fixed:
            value_per = float(thr_fixed[3:]) / 100
            quant = value_per if up else (1-value_per)
            thr = np.nanquantile(wa_masked, quant)
        
    if up:
        strongest = np.where(wa_masked >= thr, wa_masked, np.nan)
    else:
        strongest = np.where(wa_masked <= thr, wa_masked, np.nan)

    # Indexes (collapse vertical dim)
    mask_any = np.any(~np.isnan(strongest), axis=1)  # (time, south_north, west_east)
    time_idx, lat_idx, lon_idx = np.where(mask_any)

    return strongest, {
        "Time": time_idx,
        "south_north": lat_idx,
        "west_east": lon_idx
    }

def get_all_indexes(case, dom):
    vars_read = ["wa", "temp"]
    how_read = ["All", "All"]
    vars_coarsen_all  = {}

    for var, how in zip (vars_read,how_read):
        key = f"{var}_{how}_{case}_{dom}"
                
        file_coar = f'{path_arrays}/{case}_{dom}_{var}{how}_80kmAWS_coarsen_Alldims.npy'
                
        # Coarsen grid 80 km from AWS
        vars_coarsen_all[key]  = np.load(file_coar)

    # Now get strongest drafts
    wa   = vars_coarsen_all[f"wa_All_{case}_{dom}"]
    temp = vars_coarsen_all[f"temp_All_{case}_{dom}"]

    wa_down_strongest_below, wa_down_strongest_above = {},  {}
    wa_up_strongest_below, wa_up_strongest_above = {},  {}
    idx_down_below, idx_down_above = {},  {}
    idx_up_below, idx_up_above = {},  {}
    
    for stage in stages:
        i0, i1 = index_stages_all[case][stage]
        wa_stage = wa[i0:i1]
        aux_temp = temp[i0:i1]

        # Filter pos and negative W: IN EACH STAGE
        wa_down = np.where(wa_stage < 0, wa_stage, np.nan)
        wa_up   = np.where(wa_stage > 0, wa_stage, np.nan)

        # Get strongest drafts and indexes
        key_save = f"{case}_{dom}_{stage}"
        wa_down_strongest_below[key_save],  idx_down_below[key_save] = get_strongest(wa_down, aux_temp, above_freezing=False, up=False)
        wa_down_strongest_above[key_save],  idx_down_above[key_save] = get_strongest(wa_down, aux_temp, above_freezing=True,  up=False)
        wa_up_strongest_below[key_save],  idx_up_below[key_save]     = get_strongest(wa_up,   aux_temp, above_freezing=False, up=True)
        wa_up_strongest_above[key_save],  idx_up_above[key_save]     = get_strongest(wa_up,   aux_temp, above_freezing=True,  up=True)

    # Save W
    with open(f"{path_arrays}/{prefix}wa_down_strongest_below_{case}_{dom}coarsen.pkl", "wb") as f: pickle.dump(wa_down_strongest_below, f)
    with open(f"{path_arrays}/{prefix}wa_down_strongest_above_{case}_{dom}coarsen.pkl", "wb") as f: pickle.dump(wa_down_strongest_above, f)
    with open(f"{path_arrays}/{prefix}wa_up_strongest_below_{case}_{dom}coarsen.pkl", "wb") as f: pickle.dump(wa_up_strongest_below, f)
    with open(f"{path_arrays}/{prefix}wa_up_strongest_above_{case}_{dom}coarsen.pkl", "wb") as f: pickle.dump(wa_up_strongest_above, f)

get_all_indexes(case_, dom_)