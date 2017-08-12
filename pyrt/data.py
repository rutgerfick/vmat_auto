import numpy as np
import scipy.sparse as sps
import os
import h5py


class patient_data(object):
    def __init__(self, input_dict):
        self.input_dict = input_dict.copy()
        self.f = h5py.File(self.input_dict['cwd'] + self.input_dict['filename'], 'r')

        # read in num beamlets and cumulative beamlet thing
        self.num_control_points = int(np.asarray(self.f['patient/Beams/Num']))
        self.beamlets_per_cp = np.asarray(self.f['patient/Beams/ElementIndex']).flatten()
        self.cumulative_beamlets_per_cp = np.array([0] + np.cumsum(self.beamlets_per_cp).tolist())
        self.num_beamlets = int(self.beamlets_per_cp.sum())

        # todo josh read in spatial beamlet information

        print self.beamlets_per_cp
        print self.cumulative_beamlets_per_cp

        self.structures = []
        self.build_structures()

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




class structure(object):
    def __init__(self, name,index,  A_ref, f, Rx, num_vox, num_beamlets, is_target=False):
        self.name = name
        self.index = index
        self.rx = Rx
        self.num_vox = num_vox
        self.Dij = None
        self.num_beamlets = num_beamlets
        self.is_target = is_target
        self.import_dose(A_ref, f)

    def import_dose(self, A_ref, f):
        if np.asarray(f[A_ref[0]]).shape == (3,):
            print 'importing {} Dij as sparse matrix'.format(self.name)
            indices = np.asarray(f[A_ref[0]]['jc'])
            indptr = np.asarray(f[A_ref[0]]['ir'])
            data = np.asarray(f[A_ref[0]]['data'])
            # sanity check
            if self.num_beamlets != indices.size - 1:
                print 'ERROR IN DIMENSION MISMATCH' * 40

            self.Dij = sps.csr_matrix((data, indptr, indices), shape=(self.num_beamlets, self.num_vox))
        else:
            print 'importing {} Dij as dense matrix, converting to sparse...'.format(self.name)
            self.Dij = sps.csr_matrix(np.asarray(f[A_ref[0]]))
