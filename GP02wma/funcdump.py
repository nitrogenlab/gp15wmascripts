from __future__ import division, print_function
import pandas as pd
import numpy as np
import os
import gsw
from . import settingdefaults
import json
import pyompa
import scipy.io
from collections import OrderedDict


def download_gp15_data():
   #os.system("wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=1Gla6o_YihOCfU5pWGLhFvL-TKm_0aXfQ' -O names_added_GP15OMPA_33RR20180918_only_gs_rosette_clean1_hy1.csv") 
    #os.system("wget 'http://optserv1.whoi.edu/jgofsopt/80/128.12.123.170/GP15_Bottle_Leg1.mat' -O GP15_Bottle_Leg1.mat")
    #os.system("wget 'http://optserv1.whoi.edu/jgofsopt/80/128.12.123.170/GP15_Bottle_Leg2.mat' -O GP15_Bottle_Leg2.mat")
    os.system("wget 'http://raw.githubusercontent.com/nitrogenlab/GP15_watermassanalysis/main/GP15_Bottle_Leg1.mat' -O GP15_Bottle_Leg1.mat")
    os.system("wget 'http://raw.githubusercontent.com/nitrogenlab/GP15_watermassanalysis/main/GP15_Bottle_Leg2.mat' -O GP15_Bottle_Leg2.mat")

def augment_df_with_PO_NO_SiO(df):  
    #remineralization ratios
    r_PO = 155;
    r_SiO = 15
    r_NO = 9.68
    df["PO"] = df["oxygen"] + df["phosphate"]*r_PO
    df["NO"] = df["oxygen"] + df["nitrate"]*r_NO
    df["SiO"] = df["oxygen"] + df["silicate"]*r_SiO
    return df


def download_and_load_gp15_data(station_to_tc_cutoffs_url,
                                cutoffs_file_name="station_to_tc_cutoffs.json"):
    download_gp15_data()
    return load_gp15_data(station_to_tc_cutoffs_url=station_to_tc_cutoffs_url,
                          cutoffs_file_name=cutoffs_file_name)


def gp15_load_mat_data():
    leg1 = scipy.io.loadmat('GP15_Bottle_Leg1.mat')
    leg2 = scipy.io.loadmat('GP15_Bottle_Leg2.mat')

    header_mapping = {
        'bottle flag': ('BTLNBR_FLAG_W', 'BTLNBR_FLAG_W'),
        'CTD salinity flag': ('CTDSAL_FLAG_W', 'CTDSAL_FLAG_W'),
        #"bottle salinity flag": ('Flag_SALINITY_D_CONC_BOTTLE_tcj2lg',
        #                         'Flag_SALINITY_D_CONC_BOTTLE_zva7jm'),
        "bottle oxygen flag": ('Flag_OXYGEN_D_CONC_BOTTLE_qizf9x',
                               'Flag_OXYGEN_D_CONC_BOTTLE_n41f8b'),
        "silicate flag": ('Flag_SILICATE_D_CONC_BOTTLE_l9fh07',
                          'Flag_SILICATE_D_CONC_BOTTLE_3fot83'),
        "nitrate flag": ('Flag_NITRATE_D_CONC_BOTTLE_xhgtuv',
                         'Flag_NITRATE_D_CONC_BOTTLE_bugat8'),
        "phosphate flag": ('Flag_PHOSPHATE_D_CONC_BOTTLE_lof4ap',
                           'Flag_PHOSPHATE_D_CONC_BOTTLE_d0rgav'),
        "CTD pressure": ('CTDPRS', 'CTDPRS'),
        "CTD temperature" : ('CTDTMP', 'CTDTMP'),
        "practical_salinity" : ('CTDSAL', 'CTDSAL'), #CTD practical salinity
        "lat" : ('LATITUDE', 'LATITUDE'),
        "lon": ('LONGITUDE', 'LONGITUDE'),
        "stnnbr": ('STNNBR', 'STNNBR'),
        "geotrc_ID": ('GEOTRC_SAMPNO', 'GEOTRC_SAMPNO'),
        "bottom depth": ('DEPTH', 'DEPTH'),
        "oxygen": ('OXYGEN_D_CONC_BOTTLE_qizf9x',
                   'OXYGEN_D_CONC_BOTTLE_n41f8b'),
        "silicate": ('SILICATE_D_CONC_BOTTLE_l9fh07',
                     'SILICATE_D_CONC_BOTTLE_3fot83'),
        "nitrate": ('NITRATE_D_CONC_BOTTLE_xhgtuv',
                    'NITRATE_D_CONC_BOTTLE_bugat8'),
        'phosphate': ('PHOSPHATE_D_CONC_BOTTLE_lof4ap',
                      'PHOSPHATE_D_CONC_BOTTLE_d0rgav')
    }

    dict_for_data_frame = OrderedDict()

    def convert_if_string(arr, legname):
        numpy_arr = np.array(arr.squeeze())
        if  (legname == "STNNBR" or legname == "GEOTRC_SAMPNO"):
            return numpy_arr
        elif (str(numpy_arr.dtype) == "<U4" or str(numpy_arr.dtype) == "<U5" 
          or str(numpy_arr.dtype) == "<U6" or str(numpy_arr.dtype) == "<U7" 
          or str(numpy_arr.dtype) == "<U8" or str(numpy_arr.dtype) == "<U9" 
          or str(numpy_arr.dtype) == "<U11" or str(numpy_arr.dtype) == "<U12"): 
            return np.array([(float(x) if x != 'nd' else np.nan)
                             for x in numpy_arr])
        else:
            return numpy_arr

    for (new_header_name,
         (leg1_name, leg2_name)) in header_mapping.items():
        print(new_header_name, leg1_name, leg2_name)
        leg1_arr = convert_if_string(leg1[leg1_name], leg1_name)
        leg2_arr = convert_if_string(leg2[leg2_name], leg2_name)
        print(leg1_arr.dtype)
        if (str(leg1_arr.dtype)=='uint8'
             or str(leg1_arr.dtype)=='float64'):
            print("leg1 nans", np.sum(np.isnan(leg1_arr)))
            print("leg2 nans", np.sum(np.isnan(leg2_arr)))
        else:
            print('leg1 and leg2 arrays are strings.')
        dict_for_data_frame[new_header_name] = np.concatenate(
            [leg1_arr, leg2_arr])

    gp15_df = pd.DataFrame(dict_for_data_frame)

    return gp15_df


def load_gp15_data_unsplit():
    gp15_df = gp15_load_mat_data()
    #remove bad data
    for flag_type in ["bottle flag", "CTD salinity flag", "bottle oxygen flag",
                      "silicate flag", "nitrate flag", "phosphate flag"]:
        gp15_df = gp15_df[gp15_df[flag_type] <= 3]
    gp15_df = pd.DataFrame(gp15_df)

    #add PO and NO to data frame
    augment_df_with_PO_NO_SiO(gp15_df)

    absolute_salinity = gsw.SA_from_SP(
        SP=np.array(gp15_df["practical_salinity"]),
        p=np.array(gp15_df["CTD pressure"]),
        lon=np.array(gp15_df["lon"]),
        lat=np.array(gp15_df["lat"]))
    gp15_df["absolute_salinity"] = absolute_salinity

    conservative_temp = gsw.CT_from_t(SA=absolute_salinity,
                                      t=np.array(gp15_df["CTD temperature"]),
                                      p=np.array(gp15_df["CTD pressure"]))
    gp15_df["conservative_temp"] = conservative_temp

    potential_temp = gsw.pt_from_CT(SA=absolute_salinity,
                                    CT=conservative_temp)
    gp15_df["potential_temp"] = potential_temp

    sig0 = gsw.rho(SA=absolute_salinity, CT=conservative_temp, p=0) - 1000
    gp15_df["sigma0"] = sig0

    z = gsw.z_from_p(p=np.array(gp15_df["CTD pressure"]),
                     lat=np.array(gp15_df["lat"]))
    depth = -z #https://github.com/TEOS-10/python-gsw/blob/7d6ebe8114c5d8b4a64268d36100a70e226afaf6/gsw/gibbs/conversions.py#L577
    gp15_df["Depth"] = depth

    spic0 = gsw.spiciness0(SA=absolute_salinity, CT=conservative_temp)
    gp15_df["spiciness"] = spic0

    print("Rows in gp15 datafile:",len(gp15_df))
    gp15_df = gp15_df.dropna()
    print("Rows without NA values:",len(gp15_df))

    return gp15_df


def load_gp15_data(station_to_tc_cutoffs_url,
                   cutoffs_file_name):

    gp15_df = load_gp15_data_unsplit()

    download_file(url=station_to_tc_cutoffs_url, file_name=cutoffs_file_name)
    station_to_tcstartend = json.loads(open(cutoffs_file_name).read())

    gp15_intermediateanddeep = gp15_df[
        gp15_df.apply(
          lambda x: x['Depth'] >
                    station_to_tcstartend[
                      str(float(x['stnnbr']))]['depth_cutoffs'][1], axis=1)] 

    gp15_thermocline =  gp15_df[gp15_df.apply(
            lambda x: (x['Depth'] > station_to_tcstartend[
                         str(float(x['stnnbr']))]['depth_cutoffs'][0])
                  and (x['Depth'] < station_to_tcstartend[
                         str(float(x['stnnbr']))]['depth_cutoffs'][1]), axis=1)]

    return gp15_df, gp15_intermediateanddeep, gp15_thermocline


def download_file(url, file_name):
   os.system("wget "+url+" -O "+file_name)


def load_interanddeep_endmember_df(
        df_url,
        df_file_name="GP15_intermediateanddeep.csv"):
    download_file(url=df_url, file_name=df_file_name)
    endmember_df = pd.read_csv(df_file_name)
    endmember_df = augment_df_with_PO_NO_SiO(endmember_df)
    return endmember_df


def get_pyompa_soln(obs_df, endmember_df_touse,
                     param_names=None, param_weightings=None,
                     convertedparam_groups=None, usagepenalty=None,
                     endmember_name_column="watermass_name",
                     batch_size=100):

    if param_names is None:
        param_names = settingdefaults.PARAM_NAMES 
        print("param_names is None; using defaults:")
        print(param_names)

    if param_weightings is None:
        param_weightings = settingdefaults.PARAM_WEIGHTINGS
        print("param_weightings is None; using defaults:")
        print(param_weightings)

    if convertedparam_groups is None:
        convertedparam_groups=settingdefaults.CONVERTEDPARAM_GROUPS
        print("convertedparam_groups is None; using defaults")
        print(convertedparam_groups)

    if usagepenalty is None:
        usagepenalty = settingdefaults.USAGE_PENALTY
        print("usagepenalty is None; using defaults")
        print(usagepenalty)

    return pyompa.OMPAProblem(
              obs_df=obs_df,
              endmembername_to_usagepenaltyfunc=usagepenalty,
              param_names=param_names,
              param_weightings=param_weightings,
              convertedparam_groups=convertedparam_groups).solve(
                  endmember_df_touse,
                  endmember_name_column=endmember_name_column,
                  batch_size=batch_size)
