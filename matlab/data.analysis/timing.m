function [tFrameUp tEsUp tFrameOnEsUp tFrameOnEsDown] = timing(data)
% [tFrameUp tEsUp tFrameOnEsUp tFrameOnEsDown] = timing(data)
%    returns the timing infomation of image and electrical stimulus (ES).
%
%    The input should be a time series data array from recording program,
%    usually n-by-3. The output *tFrameUp* and *tEsUp* are the time of frame
%    signal rising and the time of ES signal rising, usually they mark the
%    start of these signal. The output *tFrameOnEsUp* and *tFrameOnEsDown* are
%    the frame number that fall on ES up (rising edge of signal) or ES down
%    (falling egde of signal), respectively.

% Zhou Bangyu @ Guo Lab, 2009
% Copied and modified from Li Hao, 2009

CH_IMAGE = uint8(1);  % The channel of image signal data.
CH_ES    = uint8(3);  % THe channel of electrical stimulus(ES) signal data.
THRESHOLD_IMAGE = 2.5; % Threshold for detecting image signal.
THRESHOLD_ES    = 2.5; % Threshold for detcting ES signal.

[tFrameUp tFrameDown] = findSignalTime(data(:, CH_IMAGE), THRESHOLD_IMAGE);
[tEsUp tEsDown] = findSignalTime(data(:, CH_ES), THRESHOLD_ES);

[tFrameOnEsUp tOffsetFrameOnEsUp] = findFrameOnEs(tFrameUp, tEsUp);
[tFrameOnEsDown tOffsetFrameOnEsDown] = findFrameOnEs(tFrameUp, tEsDown);
% Find the frames that contain ES signal, either rising edge of ES
% (tFrameOnEsUp), or falling edge (tFrameOnEsDown), as well as the offsets.

return