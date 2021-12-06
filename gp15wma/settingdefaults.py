import pyompa
from pyompa import EndMemExpPenaltyFunc
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
    "ENPCW_0": EndMemExpPenaltyFunc(
        spec={
            'sigma0':{'type':'density_default', 'upperbound':27},
            'lat': {'type':'other',"alpha":0.03, "beta":50, 'lowerbound':0}
            }),
    "ENPCW_1": EndMemExpPenaltyFunc(
        spec={
            'sigma0':{'type':'density_default', 'upperbound':27},
            'lat': {'type':'other',"alpha":0.03, "beta":50, 'lowerbound':0}
            }),

    "SPCW_0": EndMemExpPenaltyFunc(
        spec={
            'lat': {'type':'other',"alpha":0.03, "beta":50,'upperbound':5},
            'sigma0':{'type':'density_default', 'upperbound':27.4},
              }),
    "SPCW_1": EndMemExpPenaltyFunc(
        spec={
            'lat': {'type':'other',"alpha":0.03, "beta":50, 'upperbound':5},
            'sigma0':{'type':'density_default', 'upperbound':27.4},
              }),
    "PSUW_0": EndMemExpPenaltyFunc(
        spec={
              'lat': {'type':'other',"alpha":0.03, "beta":50, 'lowerbound':20}
              }),
    "PSUW_1": EndMemExpPenaltyFunc(
        spec={'lat': {'type':'other',"alpha":0.03, "beta":50, 'lowerbound':20}
              }),

    "ESSW_0": EndMemExpPenaltyFunc(
        spec={'sigma0':{'type':'density_default', 'upperbound':27.2},
              'lat': {'type':'other',"alpha":0.03, "beta":50, 'lowerbound':-20, 'upperbound':20}
              }),
    "ESSW_1": EndMemExpPenaltyFunc(
        spec={'sigma0':{'type':'density_default', 'upperbound':27.2},
              'lat': {'type':'other',"alpha":0.03, "beta":50, 'lowerbound':-20, 'upperbound':20}
              }),

    "EqIW_0": EndMemExpPenaltyFunc(
        spec={'sigma0':{'type':'density_default', 'upperbound':27.6},
              'lat': {'type':'other',"alpha":0.03, "beta":50, 'lowerbound':-20, 'upperbound':20}
              }),
    "EqIW_1": EndMemExpPenaltyFunc(
        spec={'sigma0':{'type':'density_default', 'upperbound':27.6},
              'lat': {'type':'other',"alpha":0.03, "beta":50, 'lowerbound':-20, 'upperbound':20}
              }),
    
    "LCDW_0": EndMemExpPenaltyFunc(
        spec={'sigma0': {'type':'density_default', 'lowerbound':27.7},
            'lat': {'type':'latlon_default', 'upperbound':40}
            }),
    "LCDW_1": EndMemExpPenaltyFunc(
        spec={'sigma0': {'type':'density_default', 'lowerbound':27.7},
            'lat': {'type':'latlon_default', 'upperbound':40}
            }),

    "AAIW_0": EndMemExpPenaltyFunc(
        spec={'sigma0':{'type':'density_default', 'upperbound':27.6},
              'lat': {'type':'other',"alpha":0.03, "beta":50, 'upperbound':10}
              }),
    "AAIW_1": EndMemExpPenaltyFunc(
        spec={'sigma0':{'type':'density_default', 'upperbound':27.6},
              'lat': {'type':'other',"alpha":0.03, "beta":50, 'upperbound':10}
              }),

    "NPIW_0": EndMemExpPenaltyFunc(
        spec={'lat': {'type':'latlon_default', 'lowerbound':20}
              }),
    "NPIW_1": EndMemExpPenaltyFunc(
        spec={'lat': {'type':'latlon_default', 'lowerbound':20}
              }),
    "NPIW_2": EndMemExpPenaltyFunc(
        spec={'lat': {'type':'latlon_default', 'lowerbound':20}
              }),
              
    "UCDW_0": EndMemExpPenaltyFunc(
        spec={'sigma0': {'type':'density_default', 'lowerbound':27.3},
            'lat': {'type':'latlon_default', 'upperbound':40}
            }),

    "AABW_0": EndMemExpPenaltyFunc(
        spec={'sigma0': {'type':'density_default', 'lowerbound':27.8},
            'lat': {'type':'latlon_default', 'upperbound':30}
            }),
} 
