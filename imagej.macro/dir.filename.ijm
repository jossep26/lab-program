
fullFilename = "e:\\data\\zby\\nikon.confocal.analysis\\20100810\\a01-001.tif";
dir = getDirFromFull(fullFilename);
filename = getFilenameFromFull(fullFilename);
print(dir);
print(filename);

function getFilenameFromFull(fullFilename)
{
  filename = substring(fullFilename, lastIndexOf(fullFilename, "\\") + 1 );
  return filename;
}

function getDirFromFull(fullFilename)
{
  dir = substring(fullFilename, 0, lastIndexOf(fullFilename, "\\") + 1 );
  return dir;
}