from subprocess import Popen, PIPE
from os import environ, pathsep
from nibabel import load
from numpy import where, array, ndindex, NaN, empty, array_split


MCRROOT = '/home/giovanni/tools/MATLAB_Runtime/v94'
TO_ADD = [
    '.',
    f'{MCRROOT}/runtime/glnxa64',
    f'{MCRROOT}/bin/glnxa64',
    f'{MCRROOT}/sys/os/glnxa64',
    f'{MCRROOT}/sys/opengl/lib/glnxa64',
    ]
environ['LD_LIBRARY_PATH'] = pathsep.join(TO_ADD)

PRF_PATH = '/Fridge/users/giovanni/projects/prf_mrvista/mcc/run_prf'

# mcc -v -N -m run_prf.m -a /home/giovanni/tools/toolboxes/analyzePRF -a /usr/local/matlab2018a/toolbox/shared/optimlib/ -a /usr/local/matlab2018a/toolbox/stats/stats -a /usr/local/matlab2018a/toolbox/images/iptformats

s = lambda x: '[' + ' '.join(str(i) for i in x) + ']'


def analyze_prf(nii_file, n_vols, n_cpu=30):
    nii = load(nii_file)
    data = nii.get_data()

    all_indices = array(list(ndindex(data.shape[:3])))

    x = data.reshape((-1, data.shape[-1]))

    good_voxels = x.mean(axis=1) > 1
    x = x[good_voxels, :]
    indices = all_indices[good_voxels, :]

    indices = where(good_voxels)[0]
    indices_split = array_split(indices, n_cpu)

    print('submitting processes')
    p_all = []
    for one_index in indices_split:
        cmd = [
            'nice',
            '-n',
            '15',
            PRF_PATH,
            nii_file,
            s(n_vols),
            s(one_index),
            ]

        p_all.append(
            Popen(cmd, env=environ, stdout=PIPE, text=True))

    output_nii = empty(data.shape[:3] + (6, ))
    output_nii.fill(NaN)

    for p in p_all:
        p.wait()
        print('Process finished')
        output_nii = _read_output(p, all_indices, output_nii)

    return output_nii


def _read_output(p, indices, output_nii):
    val = p.stdout.read().split('\n=')[1:]
    output = array([float(o) for o in val])

    output = output.reshape((-1, 6))
    ix = p.args[-1]
    ix = [int(x) for x in ix[1:-1].split()]

    for one_ix, one_out in zip(ix, output):
        output_nii[tuple(indices[one_ix])] = one_out

    return output_nii
