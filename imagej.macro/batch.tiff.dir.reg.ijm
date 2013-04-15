// --- Main procedure begin ---
// Tested on ImageJ 1.47h, Fiji 
//   at 2013 Jan 6

inDir = getDirectory("--> INPUT: Choose Directory <--");
outDir = getDirectory("--> OUTPUT: Choose Directory for TIFF Output <--");
inList = getFileList(inDir);
list = getFromFileList("", inList);  // select dirs only

// Checkpoint: get list of dirs
print("Below is a list of directories to be converted:");
printArray(list); // Implemented below

for (i=0; i<list.length; i++) 
{
  inFullname = inDir + list[i];
  outFullname = outDir + substring(list[i],0, lengthOf(list[i])-1) + ".registered.tif";
  print("Registering(",(i+1),"/",list.length,")...",list[i]); // Checkpoint: Indicating progress
  
  regTiffDirToTiff(inFullname, outFullname, 1); // Implemented below

  print("...done."); //Checkpoint: Done one.
}

print("--- All Done ---");

// --- Main procedure end ---

function regTiffDirToTiff(inFullname, outFullname, refSliceNo)
{
  setBatchMode(true);

  tifflist = getFileList(inFullname);
  tiffnames = getFromFileList("tif", tifflist);
  fn = substring(inFullname,0, lengthOf(inFullname)-1) + "/" + tiffnames[0];
  
  run("Image Sequence...", "open=[" + 
                             fn +
                             "] number=[] starting=1 increment=1 scale=100 file=[] or=[] sort");
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
  // Select from fileList array the filenames with specified extension
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