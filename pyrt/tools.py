import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

__author__ = 'troy'


def print_in_box(string_input, indent_amount = 0):
    length = len(string_input)
    print '/t'*indent_amount+'-'*(length+6)
    print '/t'*indent_amount+'|  {}  |'.format(string_input)
    print '/t'*indent_amount+'-'*(length+6)



def print_structure_info(data):
    print '-'*20
    for s in data.structures:
        print s.name,s.rx, s.num_vox, s.num_beamlets, s.is_target, s.Dij.shape
        print '-'*20

def plot_DVH(model, saveName='', showPlots=False, saveDVH=False, run_tag=None,num_bins = 500):
    if run_tag is not None:
        dose_per_struct = [np.copy(model.dose_dict[run_tag][s]) for s in range(len(model.data.structures))]
        run_label = run_tag
    else:
        dose_per_struct = [np.copy(model.current_dose_per_structure[s]) for s in range(len(model.data.structures))]
        run_label='current'

    plt.clf()
    for s in range(len(model.data.structures)):

        hist, bins = np.histogram(dose_per_struct[s], bins=num_bins)
        dvh = 1. - np.cumsum(hist) / float(model.data.structures[s].num_vox)
        plt.plot(bins[:-1], dvh, label=model.data.structures[s].name, linewidth=2)
    lgd = plt.legend(fancybox=True, framealpha=0.5, bbox_to_anchor=(1.05, 1), loc=2)

    plt.title('DVH for run tag: {}'.format(run_tag))

    plt.xlabel('Dose')
    plt.ylabel('Fractional Volume')

    plt.gca().set_xlim(left=0.)
    plt.gca().set_ylim(bottom=0., top=1.)


    if len(saveName) > 1 or saveDVH:

        if not os.path.exists(model.data.input_dict['cwd'] + model.data.input_dict['figure_directory']):
            os.makedirs(model.data.input_dict['cwd'] + model.data.input_dict['figure_directory'])

        plt.savefig(model.data.input_dict['cwd'] + model.data.input_dict['figure_directory'] + 'dvh_' + saveName + '_' + run_label + '.png',
                    bbox_extra_artists=(lgd,), bbox_inches='tight')
    if showPlots:
        plt.show()

def plot_fluence(model,saveName='', showPlots=False, saveDVH=False, run_tag=None, aperture_list = []):
    pass

def plot_fluence_map(fluence):

    pass

def is_adjacent(aper_L, aper_R, distance_limit):
    # for each row, check if L and R leafs are within distance limit
    pass


def plot_fluence_map(data, CP, beamlet_intensities, tight_bool=False, save_bool=False, save_name='aper_', buffer=1):
    relevant_beamlets = range(CP.initial_beamlet_index, CP.final_beamlet_index)

    fluence_map = np.zeros(data.control_points[CP.cp_number].field.shape)
    if len(relevant_beamlets) != len(beamlet_intensities):
        print "PLOTTING BEAMLET LENGTHS DIFFERENT"
    for r in range(len(relevant_beamlets)):
        x, y = tuple(data.control_points[CP.cp_number].field_position[r, :])
        fluence_map[int(x), int(y)] = beamlet_intensities[r]
    plt.figure()



    if tight_bool or np.min(fluence_map) > 0:
        rmin, rmax, cmin, cmax = bounding_box(fluence_map, buffer=buffer)
        sns.heatmap(fluence_map[rmin:rmax, cmin:cmax])
    else:
        sns.heatmap(fluence_map)

    if save_bool:
        if not os.path.exists(data.input_dict['cwd'] + data.input_dict['figure_directory']):
            os.makedirs(data.input_dict['cwd'] + data.input_dict['figure_directory'])

        plt.savefig(
            data.input_dict['cwd'] + data.input_dict['figure_directory'] + save_name + '_' + str(CP.cp_number) + '.png',
            bbox_inches='tight')



def plot_aper(aper, data, aper_number, tight_bool=False, save_bool=False, save_name='aper_', buffer=1):
    relevant_beamlets = np.array(aper.beamlet_members[:]) - data.control_points[aper.cp_number].initial_beamlet_index
    fluence_map = np.zeros(data.control_points[aper.cp_number].field.shape)
    for r in relevant_beamlets:
        x, y = tuple(data.control_points[aper.cp_number].field_position[r, :])
        fluence_map[x, y] = 1.
    plt.figure()

    if tight_bool:
        rmin, rmax, cmin, cmax = bounding_box(fluence_map, buffer=buffer)
        sns.heatmap(fluence_map[rmin:rmax, cmin:cmax])
    else:
        sns.heatmap(fluence_map)

    if save_bool:
        if not os.path.exists(data.input_dict['cwd'] + data.input_dict['figure_directory']):
            os.makedirs(data.input_dict['cwd'] + data.input_dict['figure_directory'])

        plt.savefig(
            data.input_dict['cwd'] + data.input_dict['figure_directory'] + save_name + '_' + str(aper_number) + '.png',
            bbox_inches='tight')


def bounding_box(img, buffer = 1):

    rows = np.any(img, axis=1)
    cols = np.any(img, axis=0)
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]

    rmin = max(0,rmin-buffer)
    rmax = min(img.shape[0],rmax+buffer+1)
    cmin = max(0, cmin - buffer)
    cmax = min(img.shape[1], cmax + buffer+1)

    return rmin, rmax, cmin, cmax