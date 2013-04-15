% Script for imaging processing

%%
% Input path, filename.
expDateShort = '091217';
expDateLong = strcat('20', expDateShort);
expName = 'drug-test-03';

% imageFileName = strcat('e:\data\zby\registered\', expDateLong, ...
%     '\registered-', expName, '.tif');
imageFileName = strcat('e:\data\zby\registered\', expDateLong, ...
    '\', expName, '.tif');
timingFileName = strcat('e:\data\zby\time\', expDateShort, '\', ...
    expName, '.mat');

% Output path, filename.
outputPath = strcat('e:\data\zby\analysed\', expDateLong, '\');
outputRoiFigName = strcat(expName,'-roi');

% Load image, timing data.
imageData = load1p(imageFileName);
load(timingFileName, 'data');  
timingData = data;
clear data

%%
% ROIs and compute BOT
handleRoiFig = figure();
imagesc(imageData(:, :, 1));  % Figure handle to remember, not image handle

prompt = {'Total ROI Number:'};  % ask for ROI number
dlg_title = 'Inputs for mmROI function';
num_lines = 1;
def = {'1'};
inputs  = str2num(char(inputdlg(prompt, dlg_title, num_lines, def)));
nRoi = inputs(1);  % get ROI number

roiInfo = getroi(nRoi, handleRoiFig);
botData = bot(imageData, roiInfo);
% todo: save the ROI position figure

%%
% Find timing infomation
[tFrameUp tEsUp tFrameOnEsUp tFrameOnEsDown] = timing(timingData);
tEvent = tEsUp([1 5 9 13]);

% Timing and frame match together
% In cases of mismatch ...
[nFrameRecorded n] = size(botData);
clear n
nFrameDetected = numel(tFrameUp);
if (nFrameDetected < nFrameRecorded)
    botData = botData(1:nFrameDetected, :); 
end  % ... throw away some tail frames.

% Merge time with BOT, and compute dF/F
botTimeData = [tFrameUp, botData];
dfToFTimeData = computeDfToF(botTimeData, tEvent, 5, 15);

%%
% Plot

% Plot BOT for each ROI
botPlotData = [tFrameUp/10000, botData];  % scale the time, now in seconds
handleBotFig = figure();
for iRoi = 1:nRoi
    subplot(nRoi, 1, iRoi);
    plot(botPlotData(:, 1), botPlotData(:, 1+iRoi));
    xlabel('Time (s)');
    ylabel('Luminence');
    title(strcat('ROI ', num2str(iRoi)));
    vline(tEvent/10000); % dependancy on "vline" from internet
end
%%
% Plot dF/F for each ROI, and each session
nSession = size(dfToFTimeData, 2); 
handleDfToFFig = figure();
for iRoi = 1:nRoi
    for iSession = 1:nSession
        subplot(nRoi, nSession, iRoi*iSession);
        plot(dfToFTimeData(iSession).dfToFRelativeInSeconds(:, 1), ...
            dfToFTimeData(iSession).dfToFRelativeInSeconds(:, 1+iRoi));
    end
end

for iRoi = 1:nRoi
    subplot(nRoi, 1, iRoi);
    plot(df(:, 1), df(:, 1+iRoi));
    xlabel('Time (s)');
    ylabel('\DeltaF / F');
    title(strcat('ROI ', num2str(iRoi)));
    vline(tEvent/10000); % dependancy on "vline" from internet
end

