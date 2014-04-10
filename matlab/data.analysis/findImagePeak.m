function peakImg = findImagePeak(img, varargin)
% findImagePeak(img, fStart, fEnd) will look up the images between fStart and fEnd and find
% among those images the peak intensity values, pixel for pixel

[y x z] = size(img);
switch nargin
    case 3
        fStart = varargin{1};
        fEnd = varargin{2};
    case 2
        fStart = varargin{1};
        fEnd = z;
    case 1
        fStart = 1;
        fEnd = z;
    otherwise
        warning('wrong input');
end

if (fStart < 1) | (fStart > z) | (fEnd < 1) | (fEnd > z)
    disp('Error: Invalid index.');
    return
end

peakImg = max(img(:,:,(fStart:fEnd)), [], 3);
    
return