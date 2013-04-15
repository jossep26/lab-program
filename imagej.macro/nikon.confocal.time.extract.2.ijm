// Extract time from time series stack, of nikon nd2 files

// BY ZBY
// Last update at 2010 Aug 25

// Tested under ver 4.2 LOCI plugins, ver 1.44f ImageJA

// List of written functions:
//   extractTimeToFile(fullFilename, outFullFilename)
//   printArray(array)
//   getFilenameFromFull(fullFilename)
//   getDirFromFull(fullFilename)
//   getExtension(filename)
//   getFromFileList(ext, fileList)

// --- Main procedures begin ---

dir = getDirectory("-------INPUT: Choose a Directory------- ");
list = getFileList(dir);
list = getFromFileList("nd2", list); // Implemented below
outDir = getDirectory("-----OUTPUT: Choose the Destination Directroy-----");

// Checkpoint: get file list of *.nd2 files
print("Below is a list of files to be extracted:");
printArray(list); // Implemented below

for (i=0; i<list.length; i++) 
{
  fullname = dir + list[i];
  outFullname = outDir + list[i] + ".time.txt";
  print("Extracting from",list[i]); // Checkpoint: Indicating progress
  
  extractTimeToFile(fullname, outFullname); // Implemented below

  print("...done."); //Checkpoint: Done one.
}

print("--- All Done ---");
// --- Main procedures end. ---

function extractTimeToFile(fullFilename, outFullFilename)
{
// Modified from planeTimings.txt
// By ZBY
// Originally written by Curtis Rueden

// Last updated on 2010 Aug 20

// Uses Bio-Formats to print the chosen file's plane timings to files.

  run("Bio-Formats Macro Extensions");

  Ext.setId(fullFilename);
  Ext.getImageCount(imageCount);

  deltaT = newArray(imageCount);

  hFile = File.open(outFullFilename);
  for (no=0; no<imageCount; no++) 
    {
      Ext.getPlaneTimingDeltaT(deltaT[no], no);
      if (deltaT[no] == deltaT[no]) // not NaN
        { 
          s = "" + (no + 1) + "\t" + deltaT[no];
        }
      print(hFile, s);
    }
    File.close(hFile);  
    Ext.close();
}

function printArray(array)
{ 
  // Print array elements recursively 
  for (i=0; i<array.length; i++)
    print(array[i]);
}

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

//test="e:\\data\\zby\\nikon.confocal.analysis\\20100810\\a01-001.tif";
//print(getExtension(test));
function getExtension(filename)
{
  ext = substring( filename, lastIndexOf(filename, ".") + 1 );
  return ext;
}
  
function getFromFileList(ext, fileList)
{
  // Select from fileList array the filenames with specified extension
  // and return a new array containing only the selected ones.

  // By ZBY
  // Last update at 2010 Aug 25

  selectedFileList = newArray(fileList.length);
  ext = toLowerCase(ext);
  j = 0;
  for (i=0; i<fileList.length; i++)
    {
      extHere = toLowerCase(getExtension(fileList[i]));
      if (extHere == ext)
        {
          selectedFileList[j] = fileList[i];
          j++;
        }
    }
  selectedFileList = Array.trim(selectedFileList, j);
  return selectedFileList;
}