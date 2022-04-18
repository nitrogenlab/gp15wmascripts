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


def download_p16_data():
    os.system("wget 'http://www.ncei.noaa.gov/data/oceans/ncei/ocads/data/0237935/GLODAPv2.2021_Pacific_Ocean.csv' -O GLODAPv2.2021_Pacific_Ocean.csv")

def download_and_load_p16_data(station_to_tc_cutoffs_url,
                                cutoffs_file_name="P16_33RO20150525_station_to_tc_cutoffs.json"):
    download_p16_data()
    return load_gp15_data(station_to_tc_cutoffs_url=station_to_tc_cutoffs_url,
                          cutoffs_file_name=cutoffs_file_name)


def p16_load_data():
    colnames_subset = ['G2cruise', 'G2station', "G2latitude", 'G2longitude', 'G2year', 'G2depth',
                   'G2pressure', 'G2temperature', 'G2salinity',
                   'G2salinityf','G2oxygen','G2oxygenf','G2silicate',
                   'G2silicatef',  'G2nitrate', 'G2nitratef', 
                   'G2phosphate', 'G2phosphatef','G2sigma0']


    gp15_df = pd.read_csv("GLODAPv2.2021_Pacific_Ocean.csv", na_values = -9999)[colnames_subset]

    gp15_columns =['cruise', 'stnnbr',"lat", 'lon', 'year', 'depth',
             'CTD pressure', 'temperature','salinity', "salinity flag", 
             'oxygen', "oxygen flag", 'silicate', "silicate flag", 'nitrate', 
             "nitrate flag", 'phosphate', "phosphate flag", 'sigma0'] 
    gp15_df.columns= gp15_columns

    absolute_salinity = np.array((gsw.SA_from_SP(SP=gp15_df["salinity"],
                                   p=gp15_df["CTD pressure"],
                                   lon=gp15_df["lon"],
                                   lat=gp15_df["lat"])))
    gp15_df["absolute_salinity"] = absolute_salinity

    conservative_temp = gsw.CT_from_t(SA=absolute_salinity,
                                  t=np.array(gp15_df["temperature"]),
                                  p=np.array(gp15_df["CTD pressure"]))
    gp15_df["conservative_temp"] = conservative_temp

    potential_temp = gsw.pt_from_CT(SA=absolute_salinity,
                                CT=conservative_temp)
    gp15_df["potential_temp"] = potential_temp

    sig0 = gsw.rho(SA=np.array(absolute_salinity), CT=np.array(conservative_temp), p=0) - 1000
    gp15_df["sigma0"] = sig0

    z = gsw.z_from_p(p=np.array(gp15_df["CTD pressure"]), lat=np.array(gp15_df["lat"]))
    depth = -z #https://github.com/TEOS-10/python-gsw/blob/7d6ebe8114c5d8b4a64268d36100a70e226afaf6/gsw/gibbs/conversions.py#L577
    gp15_df["Depth"] = depth

    print("Rows:",len(gp15_df))

    return gp15_df


def load_p16_data_unsplit():
    gp15_df = p16_load_data()
    #filter out bad data
    for flag_type in ["salinity flag", "oxygen flag",
                      "silicate flag", "nitrate flag", "phosphate flag"]:
        gp15_df = gp15_df[gp15_df[flag_type] > 0]
    print("no. of rows with flag above zero:",len(gp15_df))
    #make into df
    gp15_df = pd.DataFrame(gp15_df)
    #remove rows with missing data
    gp15_df = gp15_df.dropna()
    print("no. of rows with NaN:",len(gp15_df))
    #remove ros west of -140
    gp15_df = gp15_df[gp15_df['lon']<-140]
    print("no. of rows east of -140:",len(gp15_df))

    return gp15_df


def load_gp15_data(station_to_tc_cutoffs_url,
                   cutoffs_file_name):

    gp15_df = load_p16_data_unsplit()

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
