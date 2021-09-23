from __future__ import division, print_function
import pandas as pd
import numpy as np
import os

def download_gp15_data():
   os.system("wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=1Gla6o_YihOCfU5pWGLhFvL-TKm_0aXfQ' -O names_added_GP15OMPA_33RR20180918_only_gs_rosette_clean1_hy1.csv") 

def augment_df_with_PO_NO_SiO(df):  
    #remineralization ratios
    r_PO = 155;
    r_SiO = 15
    r_NO = 9.68
    df["PO"] = df["oxygen"] + df["phosphate"]*r_PO
    df["NO"] = df["oxygen"] + df["nitrate"]*r_NO
    df["SiO"] = df["oxygen"] + df["silicate"]*r_SiO
    return df

def load_gp15_data():
    import pandas as pd
    import numpy as np

    header = ["c"+str(i) for i in range(1,30)]
    header[4] = "bottle flag"
    header[14] = "CTD salinity flag"
    #header[16] = "bottle salinity flag"
    header[20] = "bottle oxygen flag"
    header[22] = "silicate flag"
    header[24] = "nitrate flag"
    header[28] = "phosphate flag"

    header[11] = "CTD pressure"
    header[12] = "CTD temperature"
    header[13] = "practical_salinity" #CTD practical salinity
    #header[15] = "bottle_practical_salinity" 
    header[8] = "lat"
    header[9] = "lon"

    header[0] = "stnnbr"
    header[5] = "geotrc_ID"
    header[10] = "bottom depth"
    header[19] = "oxygen"
    header[21] = "silicate"
    header[23] = "nitrate"
    header[27] = "phosphate"

    gp15_df = pd.read_csv(
      "names_added_GP15OMPA_33RR20180918_only_gs_rosette_clean1_hy1.csv",
      names=header, na_values = -999)

    #remove bad data
    for flag_type in ["bottle flag", "CTD salinity flag", "bottle oxygen flag",
                      "silicate flag", "nitrate flag", "phosphate flag"]:
        gp15_df = gp15_df[gp15_df[flag_type] <= 3]
    gp15_df = pd.DataFrame(gp15_df)

    #add PO and NO to data frame
    augment_df_with_PO_NO_SiO(gp15_df)

    absolute_salinity = gsw.SA_from_SP(SP=gp15_df["practical_salinity"],
                                       p=gp15_df["CTD pressure"],
                                       lon=gp15_df["lon"],
                                       lat=gp15_df["lat"])
    gp15_df["absolute_salinity"] = absolute_salinity

    conservative_temp = gsw.CT_from_t(SA=absolute_salinity,
                                      t=gp15_df["CTD temperature"],
                                      p=gp15_df["CTD pressure"])
    gp15_df["conservative_temp"] = conservative_temp

    potential_temp = gsw.pt_from_CT(SA=absolute_salinity,
                                    CT=conservative_temp)
    gp15_df["potential_temp"] = potential_temp

    sig0 = gsw.rho(SA=absolute_salinity, CT=conservative_temp, p=0) - 1000
    gp15_df["sigma0"] = sig0

    z = gsw.z_from_p(p=gp15_df["CTD pressure"], lat=gp15_df["lat"])
    depth = -z #https://github.com/TEOS-10/python-gsw/blob/7d6ebe8114c5d8b4a64268d36100a70e226afaf6/gsw/gibbs/conversions.py#L577
    gp15_df["Depth"] = depth

    spic0 = gsw.spiciness0(SA=absolute_salinity, CT=conservative_temp)
    gp15_df["spiciness"] = spic0

    print("Rows in gp15 datafile:",len(gp15_df))
    gp15_df = gp15_df.dropna()
    print("Rows without NA values:",len(gp15_df))

    return gp15_df
