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

function bfImport(path,channels,zs,times)
{
// Import image from "path", in specified ranges. Return the image ID.
// From dvSplitTimePoints.txt
// Originally written by Sebastien Huart. Modified by Bangyu Zhou.

//  Example:
//    coptions=newArray(2,2,1); // the second channel, (start from 0)
//    toptions=newArray(5,5,1); // the 5th time slice, (start from 1)
//    zoptions=newArray(1,20,1); // from 1st to 20th z plane, every plane (step is 1)
//    srcId=bfImport(path,coptions,zoptions,toptions);

  run("Bio-Formats Macro Extensions");
  Ext.setId(path);
//  bfDimOrders=newArray("XYZCT","XYZTC","XYCZT","XYCTZ","XYTZC","XYTCZ");
  dimOrder = "";
  Ext.getDimensionOrder(dimOrder);
  Ext.getSizeT(numT);
  Ext.getSizeZ(numZ);
  Ext.getSizeC(numC);
  print("Image " + path + " has: "); 
  print(numC + " channel(s), " + 
        numZ + " z plane(s), " + 
        numT + " time point(s)." );
  
  options = "open=[" + path + "] view=[Standard ImageJ] stack_order=" + dimOrder + " specify_range ";
  cOpts = "c_begin=" + channels[0] + " c_end=" + channels[1] + " c_step=" + channels[2];
  zOpts = "z_begin=" + zs[0]       + " z_end=" + zs[1]       + " z_step=" + zs[2];
  tOpts = "t_begin=" + times[0]    + " t_end=" + times[1]    + " t_step=" + times[2];
  options = options + cOpts + " " + zOpts + " " + tOpts;
  
  run("Bio-Formats Importer", options);
  id=getImageID();
  return id;
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