function [data outFullname] = load1p(fullFileName)
% load1p: Load one multi-page TIFF image into an array.
%    load1p Loads the file fullFileName into a three dimensional array data
%    (height, width, number of pages).
%
%    If no input argument is specified, or the input is empty, an interface
%    will pop up for choosing files. 
%
%    Returns empty arrays if user canceled file selection in the interface,
%    outFullname will be 0.
% 
%    The multi-page TIFF file should be grayscale and same size across all
%    pages. It's meant to be the data from a imaging experiment.
% 
%    fullFileName is a string and should be filename with full path, 
%    e.g. 'C:\data\imaging.tif' .

% Dependency:
%   retrieve_path, update_default_path    

% Written by Li Hao @ Guo Lab, ION, 2009.
% Modified by Zhou Bangyu @ Guo Lab, ION, Nov. 29, 2009.
% Last update was Oct. 14, 2010

if (nargin == 0) | (isempty(fullFileName))  % if no filename is input
    defaultPath = retrieve_path('tif');
    [FileName, PathName] = uigetfile('*.tif','Select the TIFF file',defaultPath);
    if isequal(FileName, 0)
        disp('TIFF Loading Canceled');
        data = [];
        outFullname = 0;
        return
    end    % Deals with user canceling loading.
    fullFileName = strcat(PathName, FileName);
    update_default_path(PathName, 'tif');
else
    example = imread(fullFileName, 1);
    [y x] = size(example);
%     nPage=fileno;
end

INFO = imfinfo(fullFileName);
nPage = numel(INFO);    % number of pages (frames) in the multi-page TIFF
x = INFO(1).Width;
y = INFO(1).Height;

data = zeros(y, x, nPage, 'int16');

texFullFileName = strrep(fullFileName,'\','\\'); % Make filename TeX.
handle = waitbar(0,sprintf('Loading image\n%s', texFullFileName));
for i = 1:nPage
%   Only after R2009a, elsewise use the following line
%     data(:,:,i) = imread(fullFileName,i);
    data(:, :, i) = imread(fullFileName, i, 'Info', INFO);
    waitbar(i/nPage, handle);
end
delete(handle);

outFullname = fullFileName;
disp(fullFileName);

return