function [ nd2TimeData ] = loadNd2Time( nd2TimeFilename )
%UNTITLED6 Summary of this function goes here
%   Detailed explanation goes here
in = load(nd2TimeFilename);
in = sort(in, 1);  % in case of misarranged order

nd2TimeData = in(:,2);
return

end

