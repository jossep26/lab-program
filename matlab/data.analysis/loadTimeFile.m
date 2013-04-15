function [ timingData ] = loadTimeFile( timeFilename )
%UNTITLED3 Summary of this function goes here
%   Detailed explanation goes here

load(timeFilename, 'data');
timingData = data;

return

end

