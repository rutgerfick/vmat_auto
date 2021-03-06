import numpy as np
import scipy.sparse as sps
import os
import h5py
from pyrt.data.tools import *


class patient_data(object):
    def __init__(self, input_dict, modality):
        self.input_dict = input_dict.copy()
        self.f = h5py.File(self.input_dict['cwd'] + self.input_dict['filename'], 'r')

        # read in num beamlets and cumulative beamlet thing
        self.num_control_points = int(np.asarray(self.f['patient/Beams/Num']))
        self.beamlets_per_cp = np.asarray(self.f['patient/Beams/ElementIndex'], dtype=np.int32).flatten()
        self.cumulative_beamlets_per_cp = np.array([0] + np.cumsum(self.beamlets_per_cp).tolist())
        self.num_beamlets = int(self.beamlets_per_cp.sum())

        self.cp_redundancy = self.input_dict['model_params']['cp_redundancy']

        print 'Building Structures'
        self.structures = []
        self.build_structures()


        print 'Building CP'
        self.control_points = []
        self.generate_control_point_data(modality,cp_redundancy=self.cp_redundancy)


    def generate_control_point_data(self, modality, cp_redundancy=1 ):

        if modality=='imrt':
            min_row, max_row = find_min_max_row_imrt(self)
            for c in range(self.num_control_points):
                # build metadata read in field
                b = self.f['patient/Beams/BeamConfig']
                field = np.asarray(self.f[b['Field'][c][0]])
                #todo troy control point only works with vmat cases because of non-continuous FM in imrt problems
                self.control_points.append(control_point_vmat(c, c, field, min_row[c], max_row[c], self.cumulative_beamlets_per_cp[c], self.beamlets_per_cp[c],modality))
        elif modality=='vmat' or modality=='conf_arc':
            min_row, max_row = find_min_max_row(self)
            self.num_control_points = self.num_control_points * cp_redundancy

            for c in range(self.num_control_points):
                current_cp =  int(c/cp_redundancy)
                # build metadata read in field
                b = self.f['patient/Beams/BeamConfig']
                field = np.asarray(self.f[b['Field'][current_cp][0]])
                self.control_points.append(control_point_vmat(c,current_cp, field, min_row, max_row, self.cumulative_beamlets_per_cp[current_cp],
                                                              self.beamlets_per_cp[current_cp],modality))
        else:
            print 'improper modality: {}'.format(modality)



    def build_structures(self):
        # Create list of real structure names
        structure_names = []
        structure_sizes = {}
        patient_structure_names = self.f['patient/StructureNames']
        patient_structure_sizes = self.f['patient/SampledVoxels']
        structure_index = {}
        for i in range(patient_structure_names.size):
            structure_names.append(''.join(chr(j) for j in self.f[patient_structure_names[i][0]][:]))
            structure_index[structure_names[-1]] = i
            structure_sizes[structure_names[-1]] = int(self.f[patient_structure_sizes[i][0]].shape[0])

        # gather init data for struct
        # Get all volume/structure/data names
        data_matrix = self.f['data/matrix']
        for s in range(data_matrix['A'].size):

            name = ''.join(chr(j) for j in self.f[data_matrix['Name'][s][0]][:])

            if name in structure_names:
                # set prescription, is_target
                Rx, is_target = 0., False

                if name in self.input_dict['Rx'].keys():
                    Rx = self.input_dict['Rx'][name]
                    is_target = True

                A_ref = data_matrix['A'][s]

                self.structures.append(structure(name=name,index=structure_index[name], A_ref=A_ref, f=self.f, Rx=Rx, num_vox=structure_sizes[name],
                                                 num_beamlets=self.num_beamlets, is_target=is_target))


