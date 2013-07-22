function averagedRoiData = applyMasks(imageData, maskImage)
% applyMasks takes an image stack and apply masks to each slice.
%   imageData typically has many slices representing time series;
%
%   maskImage may have many 'slices' each represent a different ROI;
%
%   Resulting averagedRoiData has size [nSlices nRois], each column
%   representing a series of averaged values within a ROI. The oder
%   of the ROI is preserved, i.e. the first column of averagedRoiData
%   corresponds to the first 'slice' of maskImage.


wbHandle = waitbar(0, sprintf('Applying masks\nImporting masks'));
maskData = (maskImage ~= 0);
nSlices = size(imageData, 3);
nRois = size(maskData, 3);
waitbar(0, wbHandle, sprintf('Masks imported: %d ROIs', nRois));

averagedRoiData = nan(nSlices, nRois);

for iRoi = 1:nRois
    waitbar((iRoi-1)/nRois, wbHandle, sprintf('Calculating ROI %d/%d', iRoi, nRois));
    roiMask = maskData(:,:,iRoi);
    nPixels = sum(roiMask(:));
    
    % repeat mask to a final size same as imageData
    roiRep = repmat(roiMask, [1 1 nSlices]);
    
    % after selection with mask, the dimesions will shrink to a vector;
    % so reshape it accordingly
    masked = reshape(imageData(roiRep), nPixels, nSlices);
%     masked = bsxfun(@times, imageData, roiMask); % another way to mask
    averagedRoiData(:,iRoi) = sum(masked, 1)' / nPixels;
    waitbar(iRoi/nRois, wbHandle, sprintf('Completed ROI %d/%d', iRoi, nRois));
end;

delete(wbHandle);
end