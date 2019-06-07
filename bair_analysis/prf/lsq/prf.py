#!/usr/bin/env python3
from popeye.utilities import double_gamma_hrf
from scipy.signal import convolve
from scipy.optimize import least_squares
from numpy import concatenate, ones, c_, zeros, arange, r_, dot, mean, max, meshgrid, pi, abs, std, where, dot, corrcoef, isnan, exp, empty
from numpy import cos, sin, arctan2, pi, mod, NaN, zeros, sqrt
from time import time
from datetime import datetime, timedelta
from skimage.transform import resize
from numpy.linalg import lstsq
from popeye.utilities import double_gamma_hrf
from scipy.signal import convolve
from scipy.optimize import least_squares
from pathlib import Path
from nibabel import Nifti1Image, load
from scipy.io import loadmat
from argparse import ArgumentParser



STIM_FILE = '/Fridge/R01_BAIR/visual_fmri/data/bids/stimuli/sub-{}_ses-UMCU{}_task-bairprf_run-{:02d}.mat'


def compute_prf(subject, session, nii_file, n_vols, out_dir, threshold=100):

    if session == '3TMB':
        orig_res = 658
        res = False  # to do
        visual_angle = 6.5175 * 2
    else:
        orig_res = 1394
        res = 82
        visual_angle = 6.428 * 2

    nii = load(nii_file)

    TR = nii.header.get_zooms()[3]

    assert sum(n_vols) == nii.shape[3]

    all_img = []
    baseline = int(11.9 / TR)

    for run, n_vol in enumerate(n_vols):

        img = loadmat(STIM_FILE.format(subject, session, run + 1))
        images = img['stimulus']['images'][0, 0]

        b_img = zeros((images.shape[0], images.shape[1], baseline))
        c = concatenate((b_img, images, b_img), 2)
        all_img.append(c[:, :, :n_vol].copy())

    st = concatenate(all_img, 2)

    tmp = ones(st.shape)
    tmp[st == 128] = 0
    tmp[st == 0] = 0

    images = resize(tmp, (res, res), anti_aliasing=True)

    images[images > .1] = 1
    images[images <= .1] = 0

    images_flat = images.reshape(-1, sum(n_vols))

    data = nii.get_data().copy().reshape(-1, sum(n_vols))
    mask = mean(data, axis=1) > 100
    i_good = where(mask)[0]

    r_ones = ones(sum(n_vols))
    r_runs = center(r_[zeros(n_vols[0]), ones(n_vols[1])])
    r_lin = r_[center(arange(n_vols[0], dtype=float)), center(arange(n_vols[1], dtype=float))]
    r_quad = center(r_lin ** 2)

    regressors = c_[r_ones, r_runs, r_lin, r_quad]

    beta, residuals, rank, singular_values = lstsq(regressors, data.T)

    X = dot(regressors, beta)
    data -= X.T

    data /= std(data, axis=1)[:, None]

    delta_x = arange(res) - (res - 1) / 2
    delta_x = delta_x / res * visual_angle
    xx, yy = meshgrid(delta_x, delta_x)

    results = empty((data.shape[0], 4))
    results.fill(NaN)

    t = time()
    start_time = datetime.now()

    for i_x, i in enumerate(i_good):

        x_vox = n(data[i, :])

        def minimize(params):
            x0 = params[0]
            y0 = params[1]
            sigma = params[2]
            gaussian2d = exp(-((xx - x0) ** 2 + (yy - y0) ** 2) / (2 * abs(sigma) ** 2)) * (2 * pi * abs(sigma) ** 2)

            out = dot(gaussian2d.flatten(), images_flat)

            hrf = double_gamma_hrf(params[3], TR)
            full_hrf = r_[zeros(hrf.shape[0]), hrf]

            out_hrf = convolve(out, full_hrf, 'same')
            return x_vox - n(out_hrf)

        try:
            result = least_squares(minimize, [0, 0, 5, 0], method='lm')
            results[i, :] = result.x

            if i_x % 1000 == 0:
                elapsed = time() - t
                s = elapsed / (i_x + 1) * len(i_good)
                eta = start_time + timedelta(seconds=s)
                print(f'{i_x: 7d}/{len(i_good): 7d}. {elapsed: 8.f}s. ETA: {eta:%b/%d %H:%M:%S}')
        except KeyboardInterrupt:
            break

    phi, rho = polar2clock(results)

    out_nii = Nifti1Image(phi.reshape(nii.shape[:3]), nii.affine)
    out_file = Path(out_dir) / f'{subject}_{session}_phi.nii.gz'
    out_nii.to_filename(str(out_file))

    out_nii = Nifti1Image(rho.reshape(nii.shape[:3]), nii.affine)
    out_file = Path(out_dir) / f'{subject}_{session}_rho.nii.gz'
    out_nii.to_filename(str(out_file))

    out_nii = Nifti1Image(results[:, 2].reshape(nii.shape[:3]), nii.affine)
    out_file = Path(out_dir) / f'{subject}_{session}_sigma.nii.gz'
    out_nii.to_filename(str(out_file))

    out_nii = Nifti1Image(results[:, 3].reshape(nii.shape[:3]), nii.affine)
    out_file = Path(out_dir) / f'{subject}_{session}_hrf.nii.gz'
    out_nii.to_filename(str(out_file))


def n(x):
    return (x - mean(x)) / std(x)


def center(x):
    x -= mean(x)
    return x / max(x)

def polar2clock(results):

    x = results[:, 0]
    y = results[:, 1]
    phi = mod(arctan2(x, y) / pi * 180, 360)
    rho = sqrt(x ** 2 + y ** 2)

    return phi, rho


if __name__ == '__main__':

    parser = ArgumentParser(prog='prf')
    parser.add_argument('subject')
    parser.add_argument('session')
    parser.add_argument('nii_file')
    parser.add_argument('out_dir')
    parser.add_argument('threshold')
    parser.add_argument('--n_vols', nargs=2)

    args = parser.parse_args()

    print(args)

    n_vols = [int(x) for x in args.n_vols]

    compute_prf(args.subject, args.session, args.nii_file, n_vols,
                args.out_dir, float(args.threshold))

