#!/usr/bin/env python3

from scipy.io import loadmat
from numpy import zeros, concatenate, ndindex, array
from ctypes import c_short
from popeye.visual_stimulus import VisualStimulus
from skimage.transform import resize
from nibabel import load
import popeye.og_hrf as og
import popeye.utilities as utils
from multiprocessing import Pool
import os
from nipype.interfaces.base import BaseInterface, \
    BaseInterfaceInputSpec, traits, File, TraitedSpec


def read_prf_stimuli(n_vols=(224, 224)):
    img = loadmat('/Fridge/users/margriet/stimuli/BAIR_pRF/bar_apertures.mat')
    images = img['bar_apertures']

    baseline = int(11.9 / 0.85)

    b_img = zeros((images.shape[0], images.shape[1], baseline))
    c = concatenate((b_img, images, b_img), 2)

    all_img = []
    for n_vol in n_vols:
        all_img.append(
            c[:, :, :n_vol].copy()
            )

    st = concatenate(all_img, 2)

    st = resize(st, (100, 100), anti_aliasing=True)
    stimulus = VisualStimulus(st, 112, 32, scale_factor=0.1, tr_length=0.85, dtype=c_short)

    return stimulus


def make_model(stimulus):

    # these define min and max of the edge of the initial brute-force search.
    x_grid = (-8, 8)
    y_grid = (-8, 8)
    s_grid = (1 / stimulus.ppd + 0.25, 5.25)
    h_grid = (-1.0, 1.0)

    # these define the boundaries of the final gradient-descent search.
    x_bound = (-10.0, 10.0)
    y_bound = (-10.0, 10.0)
    s_bound = (1 / stimulus.ppd, 12.0)  # smallest sigma is a pixel
    b_bound = (1e-8, None)
    u_bound = (None, None)
    h_bound = (-3.0, 3.0)

    GRIDS = (x_grid, y_grid, s_grid, h_grid)
    BOUNDS = (x_bound, y_bound, s_bound, h_bound, b_bound, u_bound,)
    model = og.GaussianModel(stimulus, utils.double_gamma_hrf)

    return model, GRIDS, BOUNDS


def compute(in_file, n_vols, out_file):

    print('reading stimuli')
    st = read_prf_stimuli(n_vols)
    print('making model')
    model, grids, bounds = make_model(st)

    nii = load(in_file)
    data = nii.get_data()

    indices = array(list(ndindex(data.shape[:3])))

    x = data.reshape((-1, data.shape[-1]))

    good_voxels = x.mean(axis=1) > 2500

    x = x[good_voxels, :]
    indices = indices[good_voxels, :]

    bundle = utils.multiprocess_bundle(og.GaussianFit, model, x,
                                       grids, bounds, indices,
                                       auto_fit=True, verbose=1, Ns=3)

    print('starting computation')
    with Pool(40) as pool:
        output = pool.map(utils.parallel_fit, bundle)

    nif = utils.recast_estimation_results(output, nii)
    nif.to_filename(out_file)


class PRFInputSpec(BaseInterfaceInputSpec):
    in_file = File(exists=True, desc='nifti file', mandatory=True)
    orig_files = traits.List(desc='nifti files',
                             mandatory=True)


class PRFOutputSpec(TraitedSpec):
    out_file = File(exists=True, desc="prf values")


class PRF(BaseInterface):
    input_spec = PRFInputSpec
    output_spec = PRFOutputSpec

    def _run_interface(self, runtime):
        fname = self.inputs.in_file

        n_vol = []
        for nifti in self.inputs.orig_files:
            nii = load(nifti)
            n_vol.append(
                nii.shape[3])

        output = os.path.abspath('prf.nii.gz')

        compute(fname, n_vol, output)

        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs["out_file"] = os.path.abspath('prf.nii.gz')
        return outputs
