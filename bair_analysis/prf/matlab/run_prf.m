function run_prf(nii_file, n_volumes, indices)

if isdeployed
    n_volumes = str2num(n_volumes);
    indices = str2num(indices);
end

load('/Fridge/users/giovanni/projects/prf_mrvista/mcc/data/images.mat', 'images')
stimulus = {};
for i = 1:length(n_volumes)
    stimulus{i} = images(:, :, 1:n_volumes(i));
end
stimulus = cat(3, stimulus{:});
size(stimulus)

TR = 0.850;

nii = niftiread(nii_file);
x = reshape(nii, [], size(nii, 4));

results = analyzePRF({stimulus}, {x(indices + 1, :)}, TR, struct('seedmode', [0, 1 ], 'display', 'off'));

params = shiftdim(results.params, 1).';
out = cat(2, params, results.R2);

disp('Results')
fprintf('=%.20f\n', out.')

