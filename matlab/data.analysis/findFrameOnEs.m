function [tFrame tOffset] = findFrameOnEs(tImage, tEs)
% [tFrame tOffset] = findFrameOnEs(tImage, tEs)
%     finds and determines the image frames that coincides with the
%     electrical stimulus (ES). It reads from tImage the time of the edges
%     of the square wave signal depicting "on" (rising edges) or "off"
%     (falling edges) of a time series of image data, and tEs the time of 
%     ES signals ("on" or "off", also), then compares and decides which 
%     frames in the image fall on to the ES signal.
% 
%     tImage and tEs should be n by 1 vectors of the signal time.  
%     The output tFrame is a vector of the time of frame falling on ES, and
%     tOffset is the absolute distance between these two events.

nEs = length(tEs);
tFrame = zeros(1, nEs);
tOffset = zeros(1, nEs);

for i = 1:nEs
    [tOffset(i) tFrame(i)] = min( abs( tImage-tEs(i) ) );
end

return