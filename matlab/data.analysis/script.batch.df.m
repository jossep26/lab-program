clear;
indir = pwd;
outdir = indir;
baseRange = (1:40);
fileList = dir(fullfile (indir, '/*.tif'));
nFile = length(fileList);
for i = 1:nFile
    fullpath = fullfile(indir, fileList(i).name);
    [ptmp, basename, ext] = fileparts(fileList(i).name);
    outTiff = fullfile(outdir, strcat(basename, '_df.tif'));
    outMat = fullfile(outdir, strcat(basename, '_df.mat'));
    dfToF = imageDfToF(fullpath, outTiff, baseRange);
    save(outMat, 'dfToF', '-mat');
end;
