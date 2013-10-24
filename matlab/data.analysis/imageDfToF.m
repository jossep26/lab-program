function data = imageDfToF(inputFullname, outputFullname, baseRange)
%   Will calculate delta F to F zero for a stack of images, pixel by pixel.
%   inputFullname points to an image stack which can be read by 'load1p'. 
%   outpuuFullname is a filename with full path.
%   baseRange specifies indexes for calculation of F zero, e.g. (1:40) for first 40 slices.

imageData = load1p(inputFullname);
nImages = size(imageData,3);

if any((baseRange > nImages)|(baseRange < 1))
    data = [];
    return
end

baseF = mean(imageData(:,:,baseRange),3);
dFtoF = zeros(size(imageData));

hw = waitbar(0,sprintf('Calculating dF/F\n'));
for i = 1:nImages
    dFtoF(:,:,i) = double(imageData(:,:,i)) ./ baseF - 1;
    waitbar(i/nImages, hw);
end
delete(hw);

data = dFtoF;

hw = waitbar(0,sprintf('Writing image to\n%s', outputFullname));
for j=1:length(dFtoF(1, 1, :))
   imwrite(dFtoF(:, :, j), outputFullname, 'WriteMode', 'append', 'Compression','none');
   waitbar(j/length(dFtoF(1, 1, :)), hw);
end
delete(hw);

end