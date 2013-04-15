
dir = getDirectory("Choose a Directory ");
list = getFileList(dir);
listArray(list);
for (i=0; i<list.length; i++) 
{
  fullname = dir + list[i];
  extractTimeToFile(fullname);
}

//fullFilename = "e:\\data\\zby\\nikon.confocal.analysis\\20100810\\a01-001.tif";
//extractTimeToFile(fullFilename);
function extractTimeToFile(fullFilename) 
{
  open(fullFilename);
  name = getInfo("image.filename");
  dir = getInfo("image.directory");
  info = getImageInfo();
  close();

  // Find the start (index1) and the end (index2)
  // index1 is the first occurance of "timestamp"
  // index2 is the immediate "return" character following the last occurance of 
  //    "timestamp"
  index1 = indexOf(info, "timestamp 0");
  index2_1 = lastIndexOf(info, "timestamp ");
  index2 = indexOf(info, "\n", index2_1);
  string_time = substring(info, index1, index2);
  //print(string_time);
  //print(name);

  // Replace and reformat string for output
  new_string_time = replace(string_time, "\n", "\r\n");
  new_string_time = replace(new_string_time, "=", "\t");

  // Save to file
  hFile = File.open(dir+name+".txt");
  print(hFile, new_string_time);
  File.close(hFile);
}

function listArray(array)
{
  for (i=0; i<array.length; i++)
    print(array[i]+"\n");
}