from __future__ import division, print_function
import pandas as pd
import numpy as np
import os
#import gsw
from . import settingdefaults
import json
import pyompa
import scipy.io
from collections import OrderedDict


#def download_GP02_data():
   #os.system("wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=1Gla6o_YihOCfU5pWGLhFvL-TKm_0aXfQ' -O names_added_GP02OMPA_33RR20180918_only_gs_rosette_clean1_hy1.csv") 
    #os.system("wget 'http://optserv1.whoi.edu/jgofsopt/80/128.12.123.170/GP02_Bottle_Leg1.mat' -O GP02_Bottle_Leg1.mat")
    #os.system("wget 'http://optserv1.whoi.edu/jgofsopt/80/128.12.123.170/GP02_Bottle_Leg2.mat' -O GP02_Bottle_Leg2.mat")
    #os.system("wget 'https://github.com/nitrogenlab/gp15wmascripts/blob/e91f38333636b0f9fa5a97b49c351bc3e4f54028/GP02wma/bottleGP02_IDP2021_v2_GEOTRACES_Seawater_Discrete_Sample_Data_v2_wlG854xv.csv' -O bottleGP02_IDP2021_v2_GEOTRACES_Seawater_Discrete_Sample_Data_v2_wlG854xv.csv")

def augment_df_with_PO_NO_SiO(df):  
    #remineralization ratios
    r_PO = 155;
    r_SiO = 15
    r_NO = 9.68
    df["PO"] = df["oxygen"] + df["phosphate"]*r_PO
    df["NO"] = df["oxygen"] + df["nitrate"]*r_NO
    df["SiO"] = df["oxygen"] + df["silicate"]*r_SiO
    return df


def download_and_load_GP02_data(station_to_tc_cutoffs_url="https://github.com/nitrogenlab/GP15_watermassanalysis/blob/0a64ed0faca01701cf6c84d09365abc706594e2c/GP02_station_to_tc_cutoffs.json",
                                cutoffs_file_name="GP02_station_to_tc_cutoffs.json"):
    return load_GP02_data(station_to_tc_cutoffs_url=station_to_tc_cutoffs_url,
                          cutoffs_file_name=cutoffs_file_name)
def GP02_load_data():
   import gsw
   colnames_subset = ['Cruise', 'Station', 'Latitude [degrees_north]', 'Longitude [degrees_east]', 'yyyy-mm-ddThh:mm:ss.sss', 
                       'DEPTH [m]', 'CTDPRS_T_VALUE_SENSOR [dbar]', 'CTDTMP_T_VALUE_SENSOR [deg C]', 'CTDSAL_D_CONC_SENSOR [pss-78]',
                   'QV:SEADATANET','OXYGEN_D_CONC_BOTTLE [umol/kg]','QV:SEADATANET','SILICATE_D_CONC_BOTTLE [umol/kg]',
                   'QV:SEADATANET',  'NITRATE_D_CONC_BOTTLE [umol/kg]', 'QV:SEADATANET', 
                   'PHOSPHATE_D_CONC_BOTTLE [umol/kg]', 'QV:SEADATANET']
   col_list=["Station", "Longitude [degrees_east]", "Latitude [degrees_north]", "CTDPRS_T_VALUE_SENSOR [dbar]", 
             "CTDTMP_T_VALUE_SENSOR [deg C]", "CTDSAL_D_CONC_SENSOR [pss-78]"]
   #GP02_df = pd.read_csv('purged_csv_file.csv', usecols=col_list)

   GP02_df = pd.read_csv("/Users/rianlawrence/Downloads/ocim_dir/bottleGP02_IDP2021_v2_GEOTRACES_Seawater_Discrete_Sample_Data_v2_wlG854xv.csv", na_values = -9999)[colnames_subset]
   
   GP02_df = GP02_df.assign(Station=GP02_df['Station'].str.replace(r'\D', ''))
   GP02_df['Station'] = GP02_df['Station'].astype(int)

   GP02_columns =['cruise', 'stnnbr',"lat", 'lon', 'year', 'depth',
             'CTD pressure', 'temperature', 'salinity', "salinity flag", 
             'oxygen', "oxygen flag", 'silicate', "silicate flag", 'nitrate', 
             "nitrate flag", 'phosphate', "phosphate flag"] 
   GP02_df.columns= GP02_columns

   absolute_salinity = np.array((gsw.SA_from_SP(SP=GP02_df["salinity"],
              p=GP02_df["CTD pressure"],
              lon=GP02_df["lon"],
              lat=GP02_df["lat"])))
   GP02_df["absolute_salinity"] = absolute_salinity

   conservative_temp = gsw.CT_from_t(SA=absolute_salinity,
               t=np.array(GP02_df["temperature"]),
               p=np.array(GP02_df["CTD pressure"]))
   GP02_df["conservative_temp"] = conservative_temp

   potential_temp = gsw.pt_from_CT(SA=absolute_salinity,
                                CT=conservative_temp)
   GP02_df["potential_temp"] = potential_temp

   sig0 = gsw.rho(SA=np.array(absolute_salinity), CT=np.array(conservative_temp), p=0) - 1000
   GP02_df["sigma0"] = sig0

   z = gsw.z_from_p(p=np.array(GP02_df["CTD pressure"]), lat=np.array(GP02_df["lat"]))
   depth = -z #https://github.com/TEOS-10/python-gsw/blob/7d6ebe8114c5d8b4a64268d36100a70e226afaf6/gsw/gibbs/conversions.py#L577
   GP02_df["Depth"] = depth

   print("Rows:",len(GP02_df))

   return GP02_df


def load_GP02_data(station_to_tc_cutoffs_url,
                   cutoffs_file_name):
    GP02_df = GP02_load_data()

    download_file(url=station_to_tc_cutoffs_url, file_name=cutoffs_file_name)
    station_to_tcstartend = json.loads(open(cutoffs_file_name).read())

    GP02_intermediateanddeep = GP02_df[
        GP02_df.apply(
          lambda x: x['Depth'] >
                    station_to_tcstartend[
                      str(float(x['stnnbr']))]['depth_cutoffs'][1], axis=1)] 

    GP02_thermocline =  GP02_df[GP02_df.apply(
            lambda x: (x['Depth'] > station_to_tcstartend[
                         str(float(x['stnnbr']))]['depth_cutoffs'][0])
                  and (x['Depth'] < station_to_tcstartend[
                         str(float(x['stnnbr']))]['depth_cutoffs'][1]), axis=1)]

    return GP02_df, GP02_intermediateanddeep, GP02_thermocline


def download_file(url, file_name):
   os.system("wget "+url+" -O "+file_name)


def load_interanddeep_endmember_df(
        df_url,
        df_file_name="GP15_intermediateanddeep.csv"):
    download_file(url=df_url, file_name=df_file_name)
    endmember_df = pd.read_csv(df_file_name)
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
