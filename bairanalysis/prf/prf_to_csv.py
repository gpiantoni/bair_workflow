from numpy import where
from nibabel import load
from pathlib import Path


def convert_prf2csv(subject, session, region, r2_file, phi_file, sigma_file,
                    rho_file, hrf_file, mask_file, csv_dir, threshold=0.5):
    files = {
        'r2': r2_file,
        'phi': phi_file,
        'sigma': sigma_file,
        'rho': rho_file,
        'hrf': hrf_file,
    }

    nii = {}
    for k, v in files.items():
        nii[k] = load(v).get_data()
    mask_nii = load(mask_file)

    m = mask_nii.get_data()
    val = where(m > threshold)

    csv_file = Path(csv_dir).resolve() / f'data_{subject}_{session}_{region}.csv'
    with csv_file.open('w') as f:
        f.write(f'subject, session, region, r2, phi, sigma, rho, hrf\n')
        for x, y, z in zip(*val):
            f.write(f"{subject}, {session}, {region}")
            for k in files.keys():
                f.write(f", {nii[k][x, y, z]:.3f}")
            f.write('\n')

    return str(csv_file)
