#!/usr/bin/env python3
from popeye.utilities import double_gamma_hrf
from scipy.signal import convolve
from scipy.optimize import least_squares
from numpy import concatenate, ones, c_, zeros, arange, r_, mean, max, meshgrid, pi, abs, std, where, dot, corrcoef, exp, empty
from numpy import arctan2, mod, NaN, sqrt
from time import time
from datetime import datetime, timedelta
from skimage.transform import resize
from numpy.linalg import lstsq
from pathlib import Path
from nibabel import Nifti1Image, load
from scipy.io import loadmat
from argparse import ArgumentParser
from logging import getLogger, StreamHandler, Formatter, INFO


STIM_FILE = '/Fridge/R01_BAIR/visual_fmri/data/bids/stimuli/sub-{}_ses-UMCU{}_task-bairprf_run-0{}.mat'

lg = getLogger('prf')


def compute_prf(subject, session, nii_file1, nii_file2, out_dir, threshold=100):

    if session == '3TMB':
        orig_res = 658
        res = 94
        visual_angle = 6.5175 * 2
    else:
        orig_res = 1394
        res = 82
        visual_angle = 6.428 * 2

    lg.info('loading data')
    nii = {
        '1': load(nii_file1),
        '2': load(nii_file2),
        }
    TR = nii['1'].header.get_zooms()[3]

    lg.info('loading stimuli')
    all_img = []
    baseline = int(11.9 / TR)

    n_vols = []
    for run in ['1', '2']:
        n_vol = nii['1'].shape[3]
        n_vols.append(n_vol)

        img = loadmat(STIM_FILE.format(subject, session, run))
        images = img['stimulus']['images'][0, 0]

        b_img = zeros((images.shape[0], images.shape[1], baseline))
        c = concatenate((b_img, images, b_img), 2)

        all_img.append(c[:, :, :n_vol].copy())

    st = concatenate(all_img, 2)

    tmp = ones(st.shape)
    tmp[st == 128] = 0
    tmp[st == 0] = 0

    lg.info('resampling stimuli')
    images = resize(tmp, (res, res), anti_aliasing=True)

    images[images > .1] = 1
    images[images <= .1] = 0

    images_flat = images.reshape(-1, sum(n_vols))

    lg.info('cleaning up data')
    data = concatenate((nii['1'].get_data(), nii['2'].get_data()), axis=3)
    data = data.reshape(-1, sum(n_vols))
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

    lg.info('starting computation about prf')
    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(exist_ok=True, parents=True)

    t = time()
    start_time = datetime.now()

    for i_x, i in enumerate(i_good):

        try:
            x_vox = n(data[i, :])
        except KeyboardInterrupt:
            # ignore if KeyboardInterrupt happens here
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
                lg.info(f'{i_x: 7d}/{len(i_good): 7d}. {elapsed: 8.0f}s. ETA: {eta:%b/%d %H:%M:%S}')
        except KeyboardInterrupt:

            # re-run it
            result = least_squares(minimize, [0, 0, 5, 0], method='lm')
            results[i, :] = result.x
            _export_data(results, nii, out_dir, subject, session, i_good, data,
                         xx, yy, TR, images_flat)
            lg.info('continuing')

    _export_data(results, nii, out_dir, subject, session, i_good, data, xx, yy,
                 TR, images_flat)
    lg.info('done')


def _export_data(results, nii_all, out_dir, subject, session, i_good, data, xx, yy,
                 TR, images_flat):
    lg.info('exporting data')
    nii = nii_all['1']
    phi, rho = polar2clock(results)

    out_nii = Nifti1Image(phi.reshape(nii.shape[:3]), nii.affine)
    out_file = Path(out_dir) / f'{subject}_{session}_phi.nii.gz'
    out_nii.to_filename(str(out_file))

    out_nii = Nifti1Image(rho.reshape(nii.shape[:3]), nii.affine)
    out_file = Path(out_dir) / f'{subject}_{session}_rho.nii.gz'
    out_nii.to_filename(str(out_file))

    out_nii = Nifti1Image(abs(results[:, 2].reshape(nii.shape[:3])), nii.affine)
    out_file = Path(out_dir) / f'{subject}_{session}_sigma.nii.gz'
    out_nii.to_filename(str(out_file))

    out_nii = Nifti1Image(results[:, 3].reshape(nii.shape[:3]), nii.affine)
    out_file = Path(out_dir) / f'{subject}_{session}_hrf.nii.gz'
    out_nii.to_filename(str(out_file))

    lg.info('converting to r2')
    r2 = empty((data.shape[0], ))
    r2.fill(NaN)
    for i_x in range(len(i_good)):
        i = i_good[i_x]
        x_fit = predict(results[i, :], xx, yy, TR, images_flat)
        x_vox = n(data[i, :])
        r2[i] = corrcoef(x_fit, x_vox)[0, 1] ** 2 * 100
    out_nii = Nifti1Image(r2.reshape(nii.shape[:3]), nii.affine)
    out_file = Path(out_dir) / f'{subject}_{session}_r2.nii.gz'
    out_nii.to_filename(str(out_file))


def predict(params, xx, yy, TR, images_flat):
    x0 = params[0]
    y0 = params[1]
    sigma = params[2]
    gaussian2d = exp(-((xx - x0) ** 2 + (yy - y0) ** 2) / (2 * abs(sigma) ** 2)) * (2 * pi * abs(sigma) ** 2)

    out = dot(gaussian2d.flatten(), images_flat)

    hrf = double_gamma_hrf(params[3], TR)
    full_hrf = r_[zeros(hrf.shape[0]), hrf]

    out_hrf = convolve(out, full_hrf, 'same')
    return n(out_hrf)


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
    parser.add_argument('nii_run1')
    parser.add_argument('nii_run2')
    parser.add_argument('out_dir')
    parser.add_argument('threshold')

    args = parser.parse_args()

    DATE_FORMAT = '%H:%M:%S'
    lg.setLevel(INFO)
    FORMAT = '{asctime:<10}{message}'

    formatter = Formatter(fmt=FORMAT, datefmt=DATE_FORMAT, style='{')
    handler = StreamHandler()
    handler.setFormatter(formatter)

    lg.handlers = []
    lg.addHandler(handler)

    compute_prf(args.subject, args.session, args.nii_run1, args.nii_run2,
                args.out_dir, float(args.threshold))
