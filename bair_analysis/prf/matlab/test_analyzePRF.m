addpath('/Fridge/users/giovanni/projects/margriet/scripts/bair_analysis/prf/matlab')
addpath('~/tools/analyzePRF/')
addpath('~/tools/analyzePRF/utilities/')
addpath('/usr/local/freesurfer_6.0.0/fsfast/toolbox')

brain_file = '/Fridge/users/giovanni/projects/margriet/analysis/preproc_wouter/nipype/full_visual11/3TMB/coreg_3T_fs/test/brain_f.nii.gz';
mask = niftiread(brain_file);

nii_file = '/Fridge/users/giovanni/projects/margriet/analysis/preproc_wouter/nipype/full_visual11/3TMB/preproc/warpapply/preprocessed.nii';
subject = 'visual11';
session = '3TMB';

n_volumes = 250;
hdr = niftiinfo(nii_file);                        % read nifti header
TR = hdr.PixelDimensions(4);                      % 850 ms

images = {};
for run = [1, 2]
    images{run} = read_bair_stimuli(subject, session, run, n_volumes, TR);
end    

disp('Loading fMRI')
nii_all = niftiread(nii_file);
nii = {};
nii{1} = nii_all(:, :, :, 1:250);
nii{2} = nii_all(:, :, :, 251:500);

hrf = fast_fslgamma(0:TR:17);

vxs = find(mask > 0);

results = analyzePRF(images, nii, TR, struct('seedmode', [0 1 2],'display','off', 'hrf', hrf, 'vxs', vxs));
save('results', 'results')

hdr.ImageSize = hdr.ImageSize(1:3);
hdr.PixelDimensions = hdr.PixelDimensions(1:3);
hdr.Datatype = 'double';

output_dir = '/Fridge/users/giovanni/projects/margriet/analysis/preproc_wouter/nipype/full_visual11/3TMB/coreg_3T_fs/test/results';
% Output parameters saved in <output_dir>
fields = {'ang', 'ecc', 'expt', 'rfsize', 'R2', 'gain', 'meanvol'};
for i = 1:length(fields)
    niftiwrite(double(results.(fields{i})), fullfile(output_dir, [fields{i}  '.nii']), hdr);
end

%%

TR = 0.85;
PATH_TO_APERTURES = '/Fridge/users/margriet/stimuli/BAIR_pRF/bar_apertures.mat';
BASELINE = 11.9;     % seconds
RESOLUTION = 100;

apertures = load(PATH_TO_APERTURES);
images = uint8(apertures.bar_apertures);

temp = zeros(RESOLUTION, RESOLUTION, size(images,3));
for p=1:size(images,3)
    temp(:,:,p) = imresize(images(:,:,p), [RESOLUTION RESOLUTION], 'cubic');
end
images = temp;

% Ensure that all images are binary
images_bin = zeros(size(images));
images_bin(images > .5) = 1;
images = images_bin;

% Add baseline
BASELINE_TR = round(BASELINE / TR);
stimulus_baseline = zeros(RESOLUTION, RESOLUTION, BASELINE_TR);

images = cat(3, stimulus_baseline, images, stimulus_baseline);

save('/Fridge/users/giovanni/projects/prf_mrvista/mcc/data/images.mat', 'images')
