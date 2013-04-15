#!/bin/bash
DATE=`date +%d_%b_%y_%R`
CD=`pwd`
subject=/media/data/zby/document/ugene.project/ple.and.flank.fa
outfile=seq.result.htm
FILES=*.seq

echo \<html\> > $outfile
echo \<head\> >> $outfile
echo \<title\> Results $DATE \<\/title\> >> $outfile
echo \<\/head\> >> $outfile
echo \<body\> >> $outfile

echo \<h1\> Results for files in $CD \<\/h1\> >> $outfile
echo \<table border="0" \> >> $outfile

shopt -s nullglob
for f in $FILES
do
  echo "Processing $f file..."

  # write table in html
  echo \<tr\> >> $outfile
  echo \<th\> >> $outfile
  
  #table header
  echo $f >> $outfile
  echo \<\/th\> >> $outfile
  echo \<\/tr\> >> $outfile

  echo \<tr\> >> $outfile
  echo \<td style="background-color:#ccccff;"\> >> $outfile
  echo \<pre\> >> $outfile
  
  # do the blast
   blastn -task 'megablast' -query $f -subject $subject -outfmt 0 >> $outfile
   
  echo \<\/pre\> >> $outfile
  echo \<\/td\> >> $outfile
  echo \<\/tr\> >> $outfile

done

echo \<\/table\> >> $outfile
echo \<\/body\> >> $outfile
echo \<\/html\> >> $outfile


