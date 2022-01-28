import pyompa
from pyompa import EndMemExpPenaltyFunc
from pyompa.endmemberpenaltyfunc import GeneralPenaltyFunc
from collections import OrderedDict

PARAM_NAMES = ["conservative_temp", "absolute_salinity",
              "silicate", "nitrate", "phosphate", "oxygen"]

CONVERTEDPARAM_GROUPS = [
    pyompa.ConvertedParamGroup(
        groupname="phosphate_remin",
        conversion_ratios=[#Representing C:P = 66
                           {"oxygen": -155*(66.0/106.0),
                            "phosphate": 1.0,
                            "nitrate": 16.0*(66.0/106.0)},
                           #Representing C:P = 209
                           {"oxygen": -155*(209.0/106.0),
                            "phosphate": 1.0,
                            "nitrate": 16.0*(209.0/106.0)}
                          ],
        always_positive=False)
]

PARAM_WEIGHTINGS = {
    "conservative_temp": 56.0,
    "absolute_salinity": 80.0,
    "silicate": 3.0,
    "nitrate": 5.0,
    "phosphate": 5.0,
    "oxygen": 1.0,
    "NO": 1.0,
    "PO": 0.5
}

USAGE_PENALTY = { 
    "ENPCW_*": GeneralPenaltyFunc(
        spec={
            'sigma0':{'type':'exp_density_default', 'upperbound':27},
            'lat': {'type':'exp_other',"alpha":0.03, "beta":50, 'lowerbound':0}
            }),
    
    "SPCW_*": GeneralPenaltyFunc(
        spec={
            'sigma0':{'type':'exp_density_default', 'upperbound':27.4},
            'lat': {'type':'exp_other',"alpha":0.03, "beta":50, 'upperbound':5}
              }),

    "PSUW_*": GeneralPenaltyFunc(
        spec={#'sigma0':{'type':'density_default', 'upperbound':27.5},
              'lat': {'type':'exp_other',"alpha":0.03, "beta":50, 'lowerbound':20}
              #'Depth': {'type':'depth_default', 'upperbound':2000}
              }),

    "ESSW_*": GeneralPenaltyFunc(
        spec={'sigma0':{'type':'exp_density_default', 'upperbound':27.2},
              'lat': {'type':'exp_other',"alpha":0.03, "beta":50, 'lowerbound':-20, 'upperbound':20}
              #'Depth': {'type':'depth_default', 'upperbound':2000}
              }),

    "EqIW_*": GeneralPenaltyFunc(
        spec={'sigma0':{'type':'exp_density_default', 'upperbound':27.6},
              'lat': {'type':'exp_other',"alpha":0.03, "beta":50, 'lowerbound':-20, 'upperbound':20}
              #'Depth': {'type':'depth_default', 'upperbound':2000}
              }),
    
    "LCDW_*": GeneralPenaltyFunc(
        spec={'sigma0': {'type':'exp_density_default', 'lowerbound':27.7},
            'lat': {'type':'exp_latlon_default', 'upperbound':40}
            }),

    "AAIW_*": GeneralPenaltyFunc(
        spec={'sigma0':{'type':'exp_density_default', 'upperbound':27.6},
              'lat': {'type':'exp_other',"alpha":0.03, "beta":50, 'upperbound':10}
              #'Depth': {'type':'exp_depth_default', 'upperbound':2000}
              }),

    "NPIW_*": GeneralPenaltyFunc(
        spec={'lat': {'type':'exp_latlon_default', 'lowerbound':20}
              #{'lat': {'type':'exp_other',"alpha":0.03, "beta":50, 'lowerbound':10}
              #{'sigma0':{'type':'exp_density_default', 'lowerbound':26, 'upperbound':27.6},
              }),
              
    "UCDW_*": GeneralPenaltyFunc(
        spec={'sigma0': {'type':'exp_density_default', 'lowerbound':27.3},
            'lat': {'type':'exp_latlon_default', 'upperbound':40}
            }),

    "AABW_*": GeneralPenaltyFunc(
        spec={'sigma0': {'type':'exp_density_default', 'lowerbound':27.8},
            'lat': {'type':'exp_latlon_default', 'upperbound':30}
            }),
} 
