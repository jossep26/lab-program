
//open("e:\\data\\zby\\nikon.confocal.analysis\\20100810\\a01-001.tif");
//info = getImageInfo();
//print(info);

array[0] = 1;
array[1] = 2;
printArray(array);

function printArray(array)
{ 
  // Print array elements recursively 
  for (i=0; i<array.length; i++)
    print(array[i]);
}
