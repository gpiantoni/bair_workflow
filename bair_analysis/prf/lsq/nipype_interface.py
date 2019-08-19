from nipype.interfaces.base import BaseInterfaceInputSpec, BaseInterface, File, TraitedSpec, traits
from os.path import realpath, join

from .prf import compute_prf


class PRFInputSpec(BaseInterfaceInputSpec):
    subject = traits.String(
        mandatory=True,
        desc='subject code',
        )
    session = traits.String(
        mandatory=True,
        desc='session code',
        )
    nii1_file = File(
        exists=True,
        mandatory=True,
        desc='preprocessed data (first run)')
    nii2_file = File(
        exists=True,
        mandatory=True,
        desc='preprocessed data (second run)')
    threshold = traits.Float(
        mandatory=True,
        desc='threshold to mask the input images',
        default=100,
        )


class PRFOutputSpec(TraitedSpec):
    phi_file = File(
        desc='phi (angle)')
    rho_file = File(
        desc='rho (eccentricity)')
    sigma_file = File(
        desc='sigma (receptive field size)')
    hrf_file = File(
        desc='time delay of hrf')
    r2_file = File(
        desc='r2 (explained variance)')


class PRF(BaseInterface):
    input_spec = PRFInputSpec
    output_spec = PRFOutputSpec

    def _run_interface(self, runtime):

        out_dir = realpath('./prf')

        compute_prf(
            self.inputs.subject,
            self.inputs.session,
            self.inputs.nii1_file,
            self.inputs.nii2_file,
            out_dir,
            self.inputs.threshold,
            )

        return runtime

    def _list_outputs(self):

        out_dir = realpath('./prf')

        outputs = {}
        conditions = ['phi', 'rho', 'hrf', 'sigma', 'r2']
        for c in conditions:
            outputs[c + '_file'] = join(out_dir, f'{self.inputs.subject}_{self.inputs.session}_{c}.nii.gz')

        return outputs
