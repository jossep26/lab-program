function roi = getroi(nRoi, handleFig)

% [a b]=size(im);
% figure(999);
% imHandle = imagesc(im);colorbar;axis image;axis off;

if (nargin == 0)
    prompt = {'Total ROI Number:', 'Perform ROI selection on which image (Figure No. XX):'};
    dlg_title = 'Inputs for mmROI function';
    num_lines = 1;
    def = {'1','1'};
    inputs  = str2num(char(inputdlg(prompt, dlg_title, num_lines, def)));
    nRoi = inputs(1);
    handleFig = inputs(2);
end
% generate a jet colormap according to nRoi
% clrMap = jet(nRoi);
% rndprm = randperm(nRoi);

hold on;

for i=1:nRoi
    figure(handleFig);
    [roi(i).x, roi(i).y, roi(i).BW, roi(i).xi, roi(i).yi] = roipoly;
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
    
    figure(handleFig);
    hold on; 
%     plot(roi(i).xi,roi(i).yi,'Color',clrMap(rndprm(i), :),'LineWidth',1);
%     text(roi(i).center(1), roi(i).center(2), num2str(i),...
%          'Color', clrMap(rndprm(i), :), 'FontWeight','Bold');
    plot(roi(i).xi,roi(i).yi,'Color','w','LineWidth',1);
    text(roi(i).center(1), roi(i).center(2), num2str(i),...
         'Color', 'w', 'FontWeight','Bold');
end

return