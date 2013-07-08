// Batch register nd2 files, output tiff

// --- Main procedures begin ---

ext ="nd2";
inDir = getDirectory("--> INPUT: Choose Directory Containing " + ext + " Files <--");
outDir = getDirectory("--> OUTPUT: Choose Directory for TIFF Output <--");
inList = getFileList(inDir);
list = getFromFileList(ext, inList);

// Checkpoint: get file list of *.nd2 files
print("Below is a list of files to be converted:");
printArray(list); // Implemented below

for (i=0; i<list.length; i++) 
{
  inFullname = inDir + list[i];
  outFullname = outDir + list[i] + ".registered.tif";
  print("Registering...",list[i]); // Checkpoint: Indicating progress
  
  regNd2ToTiff(inFullname, outFullname, 1); // Implemented below

  print("...done."); //Checkpoint: Done one.
}

print("--- All Done ---");

// --- Main procedures end ---

function regNd2ToTiff(inFullname, outFullname, refSliceNo)
{
  setBatchMode(true);
  
  run("Bio-Formats Importer", "open='" + inFullname + "' autoscale color_mode=Default view=[Standard ImageJ] stack_order=Default virtual");
  rename("todo");
  width = getWidth();
  height = getHeight();
  nTodo = nSlices;
  
  selectImage("todo");
  setSlice(refSliceNo);
  run("Duplicate...", "title=ref");

  registeredStackName = "registeredStack-";
  for (i = 1; i <= nTodo; i++)
  {
    currentSliceName="Slice-"+i;
    currentRegisteredSliceName = "registeredSlice-" + i;
    previousRegisteredStackName = registeredStackName + (i-1);
    currentRegisteredStackName = registeredStackName + i;
    nextRegisteredStackName = registeredStackName + (i+1);
 
    selectImage("todo");
    setSlice(i);
    run("Duplicate...", "title='"+ currentSliceName  + "'");

    run("TurboReg ",
          "-align "
          + "-window " + currentSliceName + " "
          + "0 0 " + (width - 1) + " " + (height - 1) + " " // No cropping.
          + "-window " + "ref" + " "
          + "0 0 " + (width - 1) + " " + (height - 1) + " " // No cropping.
          + "-rigidBody "
          + (width / 2) + " " + (height / 2) + " " // Source translation landmark.
	  + (width / 2) + " " + (height / 2) + " " // Target translation landmark.
	  + "0 " + (height / 2) + " " // Source first rotation landmark.
	  + "0 " + (height / 2) + " " // Target first rotation landmark.
	  + (width - 1) + " " + (height / 2) + " " // Source second rotation landmark.
	  + (width - 1) + " " + (height / 2) + " " // Target second rotation landmark.
          + "-showOutput"
      );
    rename("turboRegCurrent");
    run("Duplicate...", "title='"+ currentRegisteredSliceName + "'");
    if (i == 1)
    {
    	selectImage(currentRegisteredSliceName);
    	run("Duplicate...", "title='" + currentRegisteredStackName + "'");
    	selectImage(currentRegisteredSliceName);  close();
    }
    else
    {
    	run("Concatenate...", "stack1='" + previousRegisteredStackName 
    	                       + "' stack2='" + currentRegisteredSliceName
    	                       + "' title='" + currentRegisteredStackName + "'");
    	//selectImage(previousRegisteredStackName);  close(); 
    	//selectImage(currentRegisteredSliceName);  close();
    }

    selectImage("turboRegCurrent");  close();
    selectImage(currentSliceName);   close();
  }

  selectImage(registeredStackName + nTodo);
  saveAs("tiff", outFullname);
  close();
  selectImage("ref");  close();
  selectImage("todo");  close();

  setBatchMode("exit and display");
}

function getFromFileList(ext, fileList)
{
  // Select from fileList array the filenames with specified extension ("" for directories)
  // and return a new array containing only the selected ones.

  // Depends on:
  //  getExtension(filename)

  // By ZBY
  // Last update at 2013 Jan 6

  selectedFileList = newArray(fileList.length);
  selectedDirList = newArray(fileList.length);
  ext = toLowerCase(ext);
  j = 0;
  iDir = 0;
  for (i=0; i<fileList.length; i++)
    {
      extHere = toLowerCase(getExtension(fileList[i]));
      if (endsWith(fileList[i], "/"))
        {
      	  selectedDirList[iDir] = fileList[i];
      	  iDir++;
        }
      else if (extHere == ext)
        {
          selectedFileList[j] = fileList[i];
          j++;
        }
    }
    
  selectedFileList = Array.trim(selectedFileList, j);
  selectedDirList = Array.trim(selectedDirList, iDir);
  if (ext == "")
    {
    	return selectedDirList;
    }
  else 
    {
    	return selectedFileList;
    }
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