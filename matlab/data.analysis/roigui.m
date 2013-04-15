function varargout = roigui(varargin)
% ROIGUI M-file for roigui.fig
%      ROIGUI, by itself, creates a new ROIGUI or raises the existing
%      singleton*.
%
%      H = ROIGUI returns the handle to a new ROIGUI or the handle to
%      the existing singleton*.
%
%      ROIGUI('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in ROIGUI.M with the given input arguments.
%
%      ROIGUI('Property','Value',...) creates a new ROIGUI or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before roigui_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to roigui_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Dependency(1-level):
%   load1p, retrieve_path, update_default_path, drawRoi

% Edit the above text to modify the response to help roigui

% Last Modified by GUIDE v2.5 18-Oct-2010 19:59:05

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @roigui_OpeningFcn, ...
                   'gui_OutputFcn',  @roigui_OutputFcn, ...
                   'gui_LayoutFcn',  [] , ...
                   'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT


% --- Executes just before roigui is made visible.
function roigui_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to roigui (see VARARGIN)

% Choose default command line output for roigui
handles.output = hObject;

% UIWAIT makes roigui wait for user response (see UIRESUME)
% uiwait(handles.figure1);

% Managing inputs: There can be no inputs, or 1 string to indicate image
% filename, or 1 3-dimensional array that is image data.

handles.imageData = [];
handles.fullFilename = [];
handles.roi = [];
handles.nRoi = 0;
handles.isRoipolyRunning = false;

% Update handles structure
guidata(hObject, handles);

% --- Outputs from this function are returned to the command line.
function varargout = roigui_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;


% --- Executes during object creation, after setting all properties.
function axes1_CreateFcn(hObject, eventdata, handles)
% hObject    handle to axes1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: place code in OpeningFcn to populate axes1
isLoaded = false;  % add a flag for loading image, initially not loaded
handles.isLoaded = isLoaded;
guidata(hObject, handles); 


% --- Executes on mouse press over axes background.
function axes1_ButtonDownFcn(hObject, eventdata, handles)
% hObject    handle to axes1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)



% --- Executes during object creation, after setting all properties.
function startendtoggle_CreateFcn(hObject, eventdata, handles)
% hObject    handle to startendtoggle (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called
set(hObject, 'Enable', 'off'); % initially not available to user

handles.Strings = {'Start';'End'};
guidata(hObject, handles); 


% --- Executes on button press in exportbutton.
function exportbutton_Callback(hObject, eventdata, handles)
% hObject    handle to exportbutton (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
roi = handles.roi;
imageData = handles.imageData;
fullFilename = handles.fullFilename;
drawingState = get(handles.startendflag, 'String');
if strcmp(drawingState, 'ready')
    assignin('base', 'roi', roi); % output to workspace!
    assignin('base', 'imageData', imageData);
    assignin('base', 'fullname', fullFilename);
else
    set(handles.tipsbox, 'String', 'Must End first');
end

% --- Executes during object creation, after setting all properties.
function tipsbox_CreateFcn(hObject, eventdata, handles)
% hObject    handle to tipsbox (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called
set(hObject, 'String', 'Press Load Image to load a stacked tiff image');


% --- Executes on button press in loadbutton.
function loadbutton_Callback(hObject, eventdata, handles)
% hObject    handle to loadbutton (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
isLoaded = handles.isLoaded;  % get flag
imageData = handles.imageData;
fullFilename = handles.fullFilename;

if isLoaded % do not load twice
  set(handles.tipsbox, 'String', 'Image already loaded');
else  %  if not loaded, load image and enable buttons
  [imageData fullFilename] = load1p();  % load image from file
  % imageData = evalin('base', 'imageData');  % load image from workspace
  if isempty(imageData)  % deals with user cancelling file selection
    return
  else
%     imagesc(mean(imageData, 3));  % show image stack, averaged
    imshow(mean(imageData(:,:,1:50),3),[]);
    axis off;
    isLoaded = true;  % set flag to 'loaded'
    set(handles.startbutton, 'Enable', 'on');
    set(handles.exportbutton, 'Enable', 'on');
    set(handles.loadroibutton, 'Enable', 'on');
    set(hObject, 'Enable', 'off');
    set(handles.tipsbox, 'String', 'Press Start to draw ROIs, Load ROI to load ROIs from file');
   end
end

handles.isLoaded = isLoaded;  % "cache" and initialize some general var
handles.imageData = imageData;
handles.fullFilename = fullFilename;
guidata(hObject, handles);   % update the "cache"


% --- Executes during object creation, after setting all properties.
function exportbutton_CreateFcn(hObject, eventdata, handles)
% hObject    handle to exportbutton (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called
set(hObject, 'Enable', 'off');  %  


% --- Executes during object creation, after setting all properties.
function loadbutton_CreateFcn(hObject, eventdata, handles)
% hObject    handle to loadbutton (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called


% --- Executes on button press in loadroibutton.
function loadroibutton_Callback(hObject, eventdata, handles)
% hObject    handle to loadroibutton (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

%  Get ROI filename
defaultPath = retrieve_path('roimat');
[FileName, PathName] = uigetfile('*.mat','Select the MAT file with roi',defaultPath);
if isequal(FileName, 0)
     return
end    % Deals with user canceling loading.
roiFilename = strcat(PathName, FileName);
update_default_path(PathName, 'roimat');

% Load ROIs from file
load(roiFilename, 'roi');
if exist('roi', 'var') == 1  % proceed only if variable 'roi' is loaded
  nRoi = size(roi, 2);

  %  Draw loaded ROIs
  drawRoi(roi);
  
  handles.roi = roi;
  handles.nRoi = nRoi;
  guidata(hObject, handles);
  
  set(handles.tipsbox, 'String', 'ROI loaded. Press Start to draw more ROIs');
  set(handles.startendflag, 'String', 'ready');
  set(hObject, 'Enable', 'off');
end
  
% --- Executes during object creation, after setting all properties.
function loadroibutton_CreateFcn(hObject, eventdata, handles)
% hObject    handle to loadroibutton (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called
set(hObject, 'Enable', 'off'); 


% --- Executes on button press in startbutton.
function startbutton_Callback(hObject, eventdata, handles)
% hObject    handle to startbutton (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
set(handles.loadroibutton, 'Enable', 'off');  % Don't load ROI after start
set(handles.tipsbox, 'String', ...
      'Started. Press End to draw another ROI and stop'); % show tips to end drawing
set(hObject, 'Enable', 'off'); 
set(handles.endbutton, 'Enable', 'on'); 

% The core work will be done here, as the "Start" button is pressed, and
% don't start multiple times (indicated by isRoipolyRunning)

% get from "cached" parameters
i = handles.nRoi; % initial conditions, prepare the roi next to "cached" roi
roi = handles.roi;

% A loop of drawing polygonal ROIs, end until "End" is pressed
while ishandle(handles.axes1)
    
    % When "End" is pressed and roipoly stopped, reset status and break
    if strcmp(get(handles.startendflag,'String'), 'end') && ~handles.isRoipolyRunning
        set(hObject, 'Enable', 'on'); 
        set(handles.startendflag, 'String', 'ready');
        set(handles.tipsbox, 'String', 'Stopped. Press Start to resume drawing ROIs');
        break
    end

    % Prepare for next ROI
    i = i + 1;
    
    handles.isRoipolyRunning = true;  % set flag for roipoly
    guidata(hObject, handles);
    % The magic is really all in this following line
    [roi(i).x, roi(i).y, roi(i).BW, roi(i).xi, roi(i).yi] = roipoly;

    handles.isRoipolyRunning = false;

    % Determing and illustrate ROI contours and numbered tags
    xmingrid = max(roi(i).x(1), floor(min(roi(i).xi)));
    xmaxgrid = min(roi(i).x(2), ceil(max(roi(i).xi)));
    ymingrid = max(roi(i).y(1), floor(min(roi(i).yi)));
    ymaxgrid = min(roi(i).y(2), ceil(max(roi(i).yi)));
    roi(i).xgrid = xmingrid : xmaxgrid;
    roi(i).ygrid = ymingrid : ymaxgrid;
    [X, Y] = meshgrid(roi(i).xgrid, roi(i).ygrid);
    inPolygon = inpolygon(X, Y, roi(i).xi, roi(i).yi);
    Xin = X(inPolygon);
    Yin = Y(inPolygon);

    roi(i).area = polyarea(roi(i).xi,roi(i).yi);
    roi(i).center = [mean(Xin(:)), mean(Yin(:))];

    hold on;  % will now draw contour and number tag
    plot(roi(i).xi,roi(i).yi,'Color','w','LineWidth',1);
    text(roi(i).center(1), roi(i).center(2), num2str(i),...
         'Color', 'w', 'FontWeight','Bold');

    handles.roi = roi; % better to "cache" the ROIs after each is done
    handles.nRoi = i;
end

guidata(hObject, handles); % update the "cache"



% --- Executes on button press in endbutton.
function endbutton_Callback(hObject, eventdata, handles)
% hObject    handle to endbutton (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

handles.isEndPressed = true;
set(handles.startendflag, 'String', 'end');
set(hObject, 'Enable', 'off'); 
set(handles.tipsbox, 'String', 'Will stop after current ROI');

guidata(hObject, handles);


% --- Executes during object creation, after setting all properties.
function endbutton_CreateFcn(hObject, eventdata, handles)
% hObject    handle to endbutton (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

set(hObject, 'Enable', 'off');


% --- Executes during object creation, after setting all properties.
function startbutton_CreateFcn(hObject, eventdata, handles)
% hObject    handle to startbutton (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called
set(hObject, 'Enable', 'off');


% --- Executes during object creation, after setting all properties.
function startendflag_CreateFcn(hObject, eventdata, handles)
% hObject    handle to startendflag (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% This textbox is used for set flag on the state of start/end, and used in
% the loop of roipoly as break condition. Very important.
%
% By design, there are 3 states of 'String'. As initialization,
% 'justbegun', 'end' for pressing 'End' button, and 'ready' after the
% roipoly is actually ended or ROI loaded.

set(hObject, 'Visible', 'off');
set(hObject, 'String', 'justbegun');
