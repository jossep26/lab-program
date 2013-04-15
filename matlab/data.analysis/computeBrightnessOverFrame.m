function [ bofData ] = computeBrightnessOverFrame( imageData, roi )
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here

[nPixelsY nPixelsX nSlices] = size(imageData);
nROIs = length(roi);

% Check if the image and the ROI have the same size
[nMaskPixelsY nMaskPixelsX] = size(roi(1).BW);
if ~(nPixelsY == nMaskPixelsY) || ~(nPixelsX == nMaskPixelsX)
    bofData = [];
    return
end

bofData = zeros(nSlices, nROIs);
for iROI = 1:nROIs
    for jSlice = 1:nSlices
        sliceData = imageData( : , : , jSlice);  
        maskedSliceData = sliceData(roi(iROI).BW);  % Get ROI masked pixel data, is a vector
        meanMaskedSliceData = mean(maskedSliceData);
        bofData( jSlice , iROI ) = meanMaskedSliceData;  % "Kick in" one avaraged brightness at a time
    end
end

return
end