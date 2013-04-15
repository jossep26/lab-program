function mask = readMask(fullFileName)

% Reads an grayscale mask image and split it into separate regions,
% returns a cell array of binary masks, each representing one region.

% dealing with file selection
if (nargin == 0) | (isempty(fullFileName))  % if no filename is input
    defaultPath = retrieve_path('tif');
    [FileName, PathName] = uigetfile('*.tif','Select the TIFF file',defaultPath);
    if isequal(FileName, 0)
        disp('TIFF Loading Canceled');
        masks = {};
        return
    end    % Deals with user canceling loading.
    fullFileName = strcat(PathName, FileName);
    update_default_path(PathName, 'tif');
end

% read the mask image
tmpMask = imread(fullFileName);

% convert mask image into binary(true,false) mask
mask = im2bw(tmpMask,graythresh(tmpMask));

end