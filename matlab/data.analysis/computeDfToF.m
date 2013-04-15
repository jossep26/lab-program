function dfToFTimeData = computeDfToF(botTimeData, tEvent, ...
    timeLengthBefore, timeLengthAfter)
% dfToFTimeData = computeDfToF(botTimeData, tEvent, timeLengthBefore, timeLengthAfter)
%            computes dF/F traces of all the sessions in one BOT trace.
%
% *botTimeData* should be in an n-by-nBOT [time bot] format, *bot* being 
% the time series BOT data of a total number of nBOT and *time* the 
% corresponding time. Time must be in seconds.
%
% *tEvent* should be the *time point of the event start* (like ES, drug
% application, etc.), in seconds.
%
% *timeLengthBefore* is the length of time before time point tEvent, in
% seconds. It is also the time period for calculating baseline brightness.
%
% *timeLengthAfter* is the length of time after tEvent, in seconds.
%
% (*timeLengthBefore* + *timeLengthAfter*) is the total time in one session.
%
% Output *dfToFTimeData* is an 1-by-n struct, the i-th in it represents the
% i-th session in one trial (one BOT trace in the input BOT data)

% Dependency:
%    -

% Last update was at Oct 15, 2010

nSessions = numel(tEvent); % One event means one session.

tSessionBegin = tEvent - timeLengthBefore ;
tSessionEnd = tEvent + timeLengthAfter ;
timeData = botTimeData(:,1);

% Check if input is valid
if max(tEvent) > max(timeData)
    dfToFTimeData = [];
    return
end

% A struct is used to store data in different sessions.
% data(nSessions) = [];
for i = 1:nSessions
    % Split botData into sessions, according to tEvent
	rawData = botTimeData( ...
        ((timeData > tSessionBegin(i)) & (timeData < tSessionEnd(i))) ...
          , :);  % The second dimension represents ROI
      
    % First column is time. Strip it off.
    relativeTimeData = rawData(:, 1) - tEvent(i);  % Time data
    brightnessData = rawData(:, 2:end);  % Raw data without time.
    
    % Select baseline brightness data (t<0), without time column.
    baselineBrightnessData = brightnessData((relativeTimeData < 0) , : ); 
    % Mean F of baseline (F-zero). Ready the size for './' .    
    meanBaselineF = ones(size(brightnessData,1), 1) * mean(baselineBrightnessData);  
                 
    fToF = brightnessData ./ meanBaselineF; 
    dfToF = fToF - 1;
    data(i).dfToF = [relativeTimeData dfToF];  % Merge the time back.
    data(i).rawData = rawData;
end

dfToFTimeData = data;


end