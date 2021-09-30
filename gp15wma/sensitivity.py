from __future__ import division, print_function
from pyompa import OMPAProblem
from pyompa.core import ExportToCsvMixin
from collections import namedtuple


OmpaArguments = namedtuple("OMPAArguments",
                           ["constructor_arguments", "solve_arguments"])


class BaseSensitivityAnalysis(object):

    def __init__(self, static_ompa_arguments):
        self.static_ompa_arguments = static_ompa_arguments
    
    def run(self, varying_arguments_list, outdir, export_settings):
      ompa_solns = []
      for i,varying_arguments in enumerate(varying_arguments_list):
          print("On varying argument",i,"out of",len(varying_arguments_list))
          print("varying arguments:",varying_arguments)
          all_constructor_arguments =\
                self.static_ompa_arguments.constructor_arguments
          all_constructor_arguments.update(varying_arguments.constructor_arguments)
          all_solve_arguments = self.static_ompa_arguments.solve_arguments
          all_solve_arguments.update(varying_arguments.solve_arguments)
          ompa_soln = OMPAProblem(**all_constructor_arguments).solve(
              **all_solve_arguments)
          if (outdir is not None):
              ompa_soln.export_to_csv(
                  csv_output_name=outdir+"/run_"+str(i)+".csv",
                  **export_settings)
          ompa_solns.append(ompa_soln)
      return ompa_solns


#Creating ExportToCsvMixin objects (skeleton soln objects)
# for the mean and standard deviation
# so I can reuse some of the plotting and export code
def get_mean_and_stdev_skeletons(ompa_solns):

    mean_endmember_fractions =\
      np.mean([x.endmember_fractions for x in ompa_solns], axis=0)
    std_endmember_fractions = np.std([
      x.endmember_fractions for x in ompa_solns], axis=0)

    mean_param_residuals =\
      np.mean([x.param_residuals for x in ompa_solns], axis=0)
    std_param_residuals = np.std([
      x.param_residuals for x in ompa_solns], axis=0)
    
    mean_groupname_to_totalconvertedvariable = OrderedDict()
    std_groupname_to_totalconvertedvariable = OrderedDict()

    mean_groupname_to_effectiveconversionratios = OrderedDict()
    std_groupname_to_effectiveconversionratios = OrderedDict()
    
    groupnames = ompa_solns[0].groupname_to_totalconvertedvariable.keys()
    for groupname in groupnames:
        mean_groupname_to_totalconvertedvariable[groupname] =\
          np.mean([x.groupname_to_totalconvertedvariable[groupname]
                   for x in ompa_solns], axis=0)
        std_groupname_to_totalconvertedvariable[groupname] =\
          np.std([x.groupname_to_totalconvertedvariable[groupname]
                   for x in ompa_solns], axis=0)
        
        convratiokeys =\
          ompa_solns[0].groupname_to_effectiveconversionratios[groupname].keys()
        mean_groupname_to_effectiveconversionratios[groupname] = OrderedDict()
        std_groupname_to_effectiveconversionratios[groupname] = OrderedDict()

        for convratiokey in convratiokeys:
          mean_groupname_to_effectiveconversionratios[
             groupname][convratiokey] = np.mean([
              x.groupname_to_effectiveconversionratios[groupname][convratiokey]
              for x in ompa_solns], axis=0)
          std_groupname_to_effectiveconversionratios[
             groupname][convratiokey] = np.std([
              x.groupname_to_effectiveconversionratios[groupname][convratiokey]
              for x in ompa_solns], axis=0)
             
    endmember_names = list(                                                    
            ompa_solns[0].endmember_df[ompa_solns[0].endmember_name_column])
    obs_df = ompa_solns[0].obs_df

    mean_ompa_skeleton = ExportToCsvMixin(
        param_names=ompa_solns[0].param_names,
        endmember_names=endmember_names,
        obs_df=obs_df,
        endmember_fractions=mean_endmember_fractions,
        param_residuals=mean_param_residuals,
        groupname_to_effectiveconversionratios=
          mean_groupname_to_effectiveconversionratios,
        groupname_to_totalconvertedvariable=
          mean_groupname_to_totalconvertedvariable)
    
    std_ompa_skeleton = ExportToCsvMixin(
        param_names=ompa_solns[0].param_names,
        endmember_names=endmember_names,
        obs_df=obs_df,
        endmember_fractions=std_endmember_fractions,
        param_residuals=std_param_residuals,
        groupname_to_effectiveconversionratios=
          std_groupname_to_effectiveconversionratios,
        groupname_to_totalconvertedvariable=
          std_groupname_to_totalconvertedvariable)

    return (mean_ompa_skeleton, std_ompa_skeleton)
