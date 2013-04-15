function eventList = matFromSrt(fn, cText)
%matFromSrt(fn,cText) will parse .srt file(filename = fn) into a matrix of 
%  events having [start time, end time, event id]. Event id is determined
%  from an input cell array cText (e.g. {'latency','courtship',''}), with
%  -1 indicates no matches.

%  Bangyu Zhou, 2013 Apr 2

if nargin < 2, cText = {'1','2','3','4','5','6','7','8','9','0','latency','courtship',''}; end

[path, basename, ext] = fileparts(fn);
if ~strcmpi(ext, '.srt')
    error('File name extension should be .srt');
end

fid = fopen(fn);

% initialize 
% nEventEst = length(regexp(fileread('20121012-CH1-01.srt'), ' --> ', 'match'));
% eventList = zeros(nEventEst, 3);
eventList = [];

rxTimeLine = '^[0-9]{2}:[0-9]{2}:[0-9]{2},[0-9]{3} --> [0-9]{2}:[0-9]{2}:[0-9]{2},[0-9]{3}';
rxStartEndTimeSep = ' --> ';
rxTimeSep = '[:,]';

line = fgetl(fid);

while ~isnumeric(line)
    
    % go through lines, until finding the time line
    while isempty(regexp(line, rxTimeLine, 'once'))
        line = fgetl(fid);
        if(isnumeric(line))
            break
        end
    end
    
    % fail-safe
    if isnumeric(line) || isempty(regexp(line, rxTimeLine, 'once'))
        break
    end
    
    % get time
    srtTimeStringList = regexp(line, rxStartEndTimeSep, 'split');
    timeStringList = regexp(srtTimeStringList{1}, rxTimeSep, 'split');
    startTime = str2num(timeStringList{1}) * 60 * 60 * 1000 ...
                + str2num(timeStringList{2}) * 60 * 1000 ...
                + str2num(timeStringList{3}) * 1000 ...
                + str2num(timeStringList{4});

    etimeStringList = regexp(srtTimeStringList{2}, rxTimeSep, 'split');
    endTime = str2num(etimeStringList{1}) * 60 * 60 * 1000 ...
                + str2num(etimeStringList{2}) * 60 * 1000 ...
                + str2num(etimeStringList{3}) * 1000 ...
                + str2num(etimeStringList{4});

    % try get event type line
    line = fgetl(fid);
    if isnumeric(line)
        break
    end
    
    % get event type, if not in the list, = -1
    eventId = find(ismember(cText, line));
    if isempty(eventId)
        eventId = -1;
    end
    
    eventList = [eventList; [startTime, endTime, eventId]];

end

fclose(fid);

return
