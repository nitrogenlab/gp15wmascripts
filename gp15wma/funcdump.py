from __future__ import division, print_function
import pandas as pd
import numpy as np
import os

def download_gp15_data():
   os.system("wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=1Gla6o_YihOCfU5pWGLhFvL-TKm_0aXfQ' -O names_added_GP15OMPA_33RR20180918_only_gs_rosette_clean1_hy1.csv") 
