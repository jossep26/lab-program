function [sroi iRoi_num] = RoiI2M(ref,path)
    % Load ROI created in ImageJ to Matlab. 
    % The ROI type surpported currently is Oval.
    % Completed 20120309
    
  % get ROIs in '*.roi' file or '*.zip'. 
  if nargin<2
      [FileName,PathName] = uigetfile('.zip','Select the roi file','F:\03 COD\0Registed\');
      path = strcat(PathName,FileName);
  else
      path = strcat(path,'.zip');
  end
  
  iRoi = ReadImageJROI(path);
  iRoi_num = length(iRoi);
  [nrows ncols] = size(ref);
  mRoi = cell(1,iRoi_num);
  
  % Create Matlab ROI in the structure of:
    % xi: curve position in x axis
    % yi: curve position in y axis
    % x: range of image in x axis
    % y: range of image in y axis
    % BW: mask of the ROI
    % xgrid: quantumnized curve position in x axis
    % ygrid: quantumnized curve position in y axis
    % area: area of the ROI
    % center: center of the ROI
  
  % create mRoi.
    for i=1:iRoi_num
        if strcmp(iRoi(i).strType,'Oval') % check the iROI type 
                       
        % get position of the oval
            tem_bon = iRoi(i).vnRectBounds;
            ry = (tem_bon(1)+tem_bon(3))./2;
            rx = (tem_bon(2)+tem_bon(4))./2;
            rb = (tem_bon(3)-tem_bon(1))./2;
            ra = (tem_bon(4)-tem_bon(2))./2;
            
        % calculate parameter of mRoi
            [xi yi] = createEllipse(rx,ry,ra,rb,0,16);
            roi.xi = xi;
            roi.yi = yi;
            roi.area = polyarea(roi.xi,roi.yi);
            roi.center = [rx ry];
            roi.x = [1 ncols];
            roi.y = [1 nrows];
                    
            % mask of the roi
%             roix = axes2pix(ncols, roi.x, roi.xi);
%             roiy = axes2pix(nrows, roi.y, roi.yi);
            roi.BW = poly2mask(roi.xi, roi.yi,nrows,ncols);
        
            % Determing and illustrate roi contours and numbered tags
            xmingrid = max(roi.x(1), floor(min(roi.xi)));
            xmaxgrid = min(roi.x(2), ceil(max(roi.xi)));
            ymingrid = max(roi.y(1), floor(min(roi.yi)));
            ymaxgrid = min(roi.y(2), ceil(max(roi.yi)));
            roi.xgrid = xmingrid : xmaxgrid;
            roi.ygrid = ymingrid : ymaxgrid;     
            
            % save current roi into cells.
            mRoi{i} = roi;

        else
            
            error('wrong ROI type');

        end
        
        
    end
    
    sroi=[mRoi{1:end}];
    
  % plot mRoi
    figure;imagesc(ref);axis image; axis off;%colormap gray;
    for i=1:iRoi_num
        hold on;
        plot(sroi(i).xi,sroi(i).yi,'Color','k','LineWidth',1);
        text(sroi(i).center(1), sroi(i).center(2), num2str(i),...
            'Color', 'k', 'FontWeight','Bold');
    end

return


    