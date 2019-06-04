function output_stim = read_bair_stimuli(subject, session, run, n_volumes, TR)
% 
% function images = READ_BAIR_STIMULI (n_volumes, TR)
%
% This function reads in the images of the stimuli presented per run, along with
% the the number of dynamics (<n_volumes>) and the repetition time (<TR>).
% <n_volumes> is a list of integers, with the number of volumes for each
% session.
%
% Input:
% <subjectcode>, <session>, <run>, <n_volumes>, <TR>
%
% Output: 
% <output_stim> containing pRF stimulus information with added baseline.
%%

% ========= Read in stimuli for specific run ========= % 
stim_file = sprintf('/Fridge/R01_BAIR/visual_fmri/data/bids/stimuli/sub-%s_ses-UMCU%s_task-bairprf_run-%02d.mat', ...
    subject, session, run);
img = load(stim_file);
images = img.stimulus.images;

% ========= Turn stimuli into binary mask: include all non-grey pixels  ========= % 
images = images ~= 128;

% ========= Convert to 100X100 resolution ========= % 
RESOLUTION = 100;

temp = zeros(RESOLUTION, RESOLUTION, size(images,3));
for p=1:size(images,3)
    temp(:,:,p) = imresize(images(:,:,p), [RESOLUTION RESOLUTION], 'cubic');
end
images = temp;

% ========= Add baseline ========= % 
BASELINE = 11.9;                         % In seconds
BASELINE_TR = round(BASELINE / TR);      % In dynamics
stimulus_baseline = zeros(RESOLUTION, RESOLUTION, BASELINE_TR);

images = cat(3, stimulus_baseline, images, stimulus_baseline);

% ========= OUTPUT with n_volumes ========= % 
output_stim = images(:, :, 1:n_volumes);

%% End