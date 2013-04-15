% demo analysis

% load masks, images
bcatMs = readAndSplitMask('demo/bcatm_01pj.tif');
chRM = readMask('demo/ChRm_01pj.tif');
bcatImg = imread('demo/bcat_01pj.tif');

% select the colocalized masks
coBcatMs = selectMasksIntersectWith(bcatMs, chRM, 3);

% calculate area (in pixels) for one mask
sum(sum(coBcatMs{1,1}))
sum(sum(coBcatMs{2,1}))

% show number of colocalized masks
length(coBcatMs)

% calculate average intensity of one ROI in the original image
mean(bcatImg(coBcatMs{1,1}))
