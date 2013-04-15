// Batch convert Nikon nd2 files to tiff files under one selected dir,
// sub directories are ignored.

// List of written functions here:
//    getFromFileList(ext, fileList)
//    convertBioFormatToTif(inFullname, outFullname)
//    printArray(array)
//    getExtension(filename)

// By ZBY
// Tested under ...
// Last update at 2010 Aug 25

// --- Main procedures begin ---

ext ="nd2";
inDir = getDirectory("--> INPUT: Choose Directory Containing " + ext + "Files <--");
outDir = getDirectory("--> OUTPUT: Choose Directory for TIFF Output <--");
inList = getFileList(inDir);
list = getFromFileList(ext, inList);

// Checkpoint: get file list of *.nd2 files
print("Below is a list of files to be converted:");
printArray(list); // Implemented below

setBatchMode(true);

for (i=0; i<list.length; i++) 
{
  inFullname = inDir + list[i];
  outFullname = outDir + list[i] + ".tif";
  print("Converting",list[i]); // Checkpoint: Indicating progress
  
  convertBioFormatToTif(inFullname, outFullname); // Implemented below

  print("...done."); //Checkpoint: Done one.
}

print("--- All Done ---");

// --- Main procedures end ---

function convertBioFormatToTif(inFullname, outFullname)
{
  run("Bio-Formats Importer", "open='" + inFullname + "' autoscale color_mode=Default view=[Standard ImageJ] stack_order=Default virtual");
  saveAs("Tiff", outFullname);
  close();
}

function convertBioFormatTo8BitTif(inFullname, outFullname)
{
  run("Bio-Formats Importer", "open='" + inFullname + "' autoscale color_mode=Default view=[Standard ImageJ] stack_order=Default virtual");
  run("8-bit");
  saveAs("Tiff", outFullname);
  close();
}

function getFromFileList(ext, fileList)
{
  // Select from fileList array the filenames with specified extension
  // and return a new array containing only the selected ones.

  // Depends on:
  //  getExtension(filename)

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

function printArray(array)
{ 
  // Print array elements recursively 
  for (i=0; i<array.length; i++)
    print(array[i]);
}

function getExtension(filename)
{
  ext = substring( filename, lastIndexOf(filename, ".") + 1 );
  return ext;
}