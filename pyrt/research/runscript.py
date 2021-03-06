from pyrt.optimization.vmat import *
from pyrt.research.run_functions import *

# Josh Inputs - Prostate
# Find work directory
# cwd = '/Users/troy/Dropbox/CAP Group/TROTS/Prostate_VMAT/'
working_directory = 'outputs_josh/'
cwd = '/Users/jtmargo/Desktop/Josh/Clemson University/Research/Treatment Plan/TROTS Data/Prostate_VMAT/'

back_proj_list_of_dicts = [
   {'PTV':30.,'Bladder':15.,'default':0., 'threshold':0.},
    {'PTV':30.,'Rectum':15.,'default':0., 'threshold':0.},
#     {'PTV':5,'default':1, 'threshold':0.},
    {'PTV':100.,'default':1., 'threshold':0.},
    {'PTV':1.,'default':0., 'threshold':0.}
]

vmat_model_params = {
    'target_weights':{'PTV':1000., 'default':500.},
    'oar_weights':{'Rectum':10., 'Bladder':10., 'default':1.},
    'max_intensity':1000.,
    'min_intensity': 1.,
    'aper_limit': 1.,
    'max_distance_per_cp': 100,
    'cp_redundancy': 4,
    'back_projection_dicts':back_proj_list_of_dicts
}


input_dict = {
    'cwd': cwd,
    'figure_directory':working_directory,
    'aper_types_list': ['back_proj'],
    'filename': None,
    'Rx': {'PTV': 79.56, 'PTV Vesicles': 72.2},
    'model_params':vmat_model_params
}


#Run individual case

# Load patient information
input_dict['filename'] = 'Prostate_VMAT_102.mat'
input_dict['case_directory'] = input_dict['filename'][0:-4]+'/'


run_case(input_dict)