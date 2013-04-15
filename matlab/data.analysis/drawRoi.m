function [ ] = drawRoi( roiData, lineSpec, textSpec )
%drawRoi(roiData, lineSpec, textSpec) plots ROIs depicted in roiData 
%   on the current axes.
%
%   Input roiData must be a struct from *roigui* or *getroi*.
%
%   Input lineSpec decides the line style of ROIs' contour, textSepc
%   decides the text style of ROIs' number.
%
%   Inputs lineSpec and textSpec are optional, lineSpec is in fact a cell 
%   array of parameters of LineSpec of plot function, and textSpec is a
%   cell array of parameters of text properties of text function. If not
%   specified, ROIs will be drawn with default values.
%  

if nargin < 3, textSpec = {'Color', 'w', 'FontWeight','Bold'}; end
if nargin < 2, lineSpec = {'Color','w','LineWidth',1}; end
if nargin < 1
    error('No ROI data specified');
end

roi = roiData;
nRoi = size(roi, 2);

for i=1:nRoi
    hold on;

    plot(roi(i).xi,roi(i).yi, lineSpec{:});
    text(roi(i).center(1), roi(i).center(2), num2str(i), textSpec{:});
end

end

