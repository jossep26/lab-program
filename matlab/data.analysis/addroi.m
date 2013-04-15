function newroi=addroi(roi)

% [a b]=size(im);
% figure(999);
% imHandle = imagesc(im);colorbar;axis image;axis off;

prompt = {'Total ROI Number:', 'Perform ROI selection on which image (Figure No. XX):'};
dlg_title = 'Inputs for mmROI function';
num_lines = 1;
def = {'1','1'};
inputs  = str2num(char(inputdlg(prompt, dlg_title, num_lines, def)));
roiNumber = inputs(1);
workingImage = inputs(2);
roiNo=length(roi);

% generate a jet colormap according to roiNumber
% clrMap = jet(roiNumber);
% rndprm = randperm(roiNumber);

hold on;

for i=1:roiNo
    figure(workingImage);
    newroi(i)=roi(i);
    hold on; 
%     plot(roi(i).xi,roi(i).yi,'Color',clrMap(rndprm(i), :),'LineWidth',1);
%     text(roi(i).center(1), roi(i).center(2), num2str(i),...
%          'Color', clrMap(rndprm(i), :), 'FontWeight','Bold');
    plot(roi(i).xi,roi(i).yi,'Color','k','LineWidth',1);
    text(roi(i).center(1), roi(i).center(2), num2str(i),...
         'Color', 'k', 'FontWeight','Bold');
end

clear roi;

if roiNumber ~= 0
    for i=1:roiNumber
        figure(workingImage);
        [roi.x, roi.y, roi.BW, roi.xi, roi.yi] = roipoly;
        xmingrid = max(roi.x(1), floor(min(roi.xi)));
        xmaxgrid = min(roi.x(2), ceil(max(roi.xi)));
        ymingrid = max(roi.y(1), floor(min(roi.yi)));
        ymaxgrid = min(roi.y(2), ceil(max(roi.yi)));
        roi.xgrid = xmingrid : xmaxgrid;
        roi.ygrid = ymingrid : ymaxgrid;
        [X, Y] = meshgrid(roi.xgrid, roi.ygrid);
        inPolygon = inpolygon(X, Y, roi.xi, roi.yi);
        Xin = X(inPolygon);
        Yin = Y(inPolygon);

        roi.area = polyarea(roi.xi,roi.yi);
        roi.center = [mean(Xin(:)), mean(Yin(:))];
        newroi(i+roiNo)=roi;

        figure(workingImage);
        hold on; 
    %     plot(roi(i).xi,roi(i).yi,'Color',clrMap(rndprm(i), :),'LineWidth',1);
    %     text(roi(i).center(1), roi(i).center(2), num2str(i),...
    %          'Color', clrMap(rndprm(i), :), 'FontWeight','Bold');
        plot(roi.xi,roi.yi,'Color','k','LineWidth',1);
        text(roi.center(1), roi.center(2), num2str(i+roiNo),...
             'Color', 'k', 'FontWeight','Bold');
    end
end

return