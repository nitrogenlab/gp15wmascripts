from __future__ import division, print_function
from pyompa import OMPAProblem


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
