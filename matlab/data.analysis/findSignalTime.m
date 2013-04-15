function [tUp tDown] = findSignalTime(data, THRESHOLD)
% findSignalTime(data, THRESHOLD) 
%               returns the vectors of detected rising edges and falling 
%               edges of a time series of square wave signals, 'data', the 
%               amplitude of which characterized by THRESHOLD.
%
% Syntax: [tUp tDown] = findSignalTime(data, THRESHOLD)
%         'data' should be a n by 1 vector of time series data, THRESHOLD
%         should be an arbitrary number that fits the squal wave signal.
% 

% Zhou Bangyu @ Guo's Lab, 2009
% Last update was at Oct 15, 2010

% Copied and modified from Li Hao's original th :
% 
% function [up down]=th(data,threshold)
% 
% data2=[data(2:end); data(end)];
% 
% up=find(data<threshold & data2>threshold);
% down=find(data>threshold & data2<threshold);
% 
% if numel(up) ~= numel(down)
%     warning('Number of rising edges unequal to the number of falling edges');
% else
% %     figure;plot(down-up);
% end
% % delta=down-up;
% 
% return

data2 = [data(2:end); data(end)];
% The idea is to find the point i where t(i) is less than THRESHOLD but 
% t(i+1) greater than THRESHOLD. That will be the 'rising edge'. 
% The 'falling edge' will be the point i where t(i) > THRESHOLD and
% t(i+1) < THRESHOLD.
% So shift data 1 step (time unit) ahead to be compared to the original
% one.

tUp = find(data<THRESHOLD & data2>THRESHOLD);
tDown = find(data>THRESHOLD & data2<THRESHOLD);

if numel(tUp) ~= numel(tDown)
    warning('Number of rising edges unequal to the number of falling edges');
end

return