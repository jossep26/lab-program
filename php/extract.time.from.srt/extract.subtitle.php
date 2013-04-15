<?php


    /**
     * Parse a .srt file to a variable in php.
     * 
     * Ref. http://www.talkphp.com/vbarticles.php?do=article&articleid=39&title=walkthrough-parsing-a-srt-subtitle-file
     */
	function parse_srt($szSRTFile)
	{
		$szSRT 		= 	file_get_contents($szSRTFile);
		$szBreak 	= 	strstr($szSRT, chr(13)) !== false ? "\r\n" : "\n";
		$aData 		= 	explode(str_repeat($szBreak, 2), $szSRT);
		
		for($iIndex = 0, $iDataLen = count($aData), $aSubtitles = array(); $iIndex <= $iDataLen; $iIndex++)
		{
			$szItem =& $aData[$iIndex];
			
			if(empty($szItem))
			{
				break;
			}
			
			$aLine = explode($szBreak, $szItem, 3);
			$aTime = explode('-->', $aLine[1]);
			
			$aSubtitles[] = array	(	
										'index' => (int) $aLine[0],
										'time_start' => trim($aTime[0]),
										'time_end' => trim($aTime[1]),
										'text' => $aLine[2]
									);
		}
		
		return $aSubtitles;
	}

    /**
    * Generatting CSV formatted string from an array.
    * By Sergey Gurevich.
    * Ref. http://www.codehive.net/PHP-Array-to-CSV-1.html
    */
    function array_to_csv($array, $header_row = true, $col_sep = ",", $row_sep = "\n", $qut = '"')
    {
        if (!is_array($array) or !is_array($array[0])) return false;
        
        //Header row.
        if ($header_row)
        {
            foreach ($array[0] as $key => $val)
            {
                //Escaping quotes.
                $key = str_replace($qut, "$qut$qut", $key);
                $output .= "$col_sep$qut$key$qut";
            }
            $output = substr($output, 1)."\n";
        }
        //Data rows.
        foreach ($array as $key => $val)
        {
            $tmp = '';
            foreach ($val as $cell_key => $cell_val)
            {
                //Escaping quotes.
                $cell_val = str_replace($qut, "$qut$qut", $cell_val);
                $tmp .= "$col_sep$qut$cell_val$qut";
            }
            $output .= substr($tmp, 1).$row_sep;
        }
        
        return $output;
    }


    function srtTime_to_miliSec($srtTime)
    {
        $times = explode(':', $srtTime);
        $secs = explode(',', $times[2]);
        
        $miliSec = (int)$secs[1] + (int)$secs[0]*1000 + (int)$times[1]*60*1000
                     + (int)$times[0]*60*60*1000;
        
        return $miliSec;
    }
     
    function srt_to_csv($srtFile, $csvFile)
    {
        /**
         * Convert a subtitle file to a csv file, with time info and text.
         * 
         * Written by Bangyu Zhou.
         * Many functions are found in web.
         * Last update: 12.02.2012
         */
            
        $aSrt = parse_srt($srtFile);
        
        foreach ($aSrt as &$subtitle)
        {
            $miliSecStart = srtTime_to_miliSec($subtitle['time_start']);
            $miliSecEnd = srtTime_to_miliSec($subtitle['time_end']);
            $interval = $miliSecEnd - $miliSecStart;
            $subtitle['start_miliSec'] = $miliSecStart;
            $subtitle['end_miliSec'] = $miliSecEnd;
            $subtitle['interval_miliSec'] = $interval;
         }
        unset($subtitle);
        
        $csv_srt = array_to_csv($aSrt);
    
        file_put_contents($csvFile, $csv_srt);
    }    
  

/**
 * For all the srt files in current the directory, convert them to csv.
 * 
 */
  
$dir = "./";
$srtFiles = glob($dir . "*.srt");

foreach($srtFiles as $srtFile)
{
    $outCsv = $srtFile.".csv";
    
    echo $srtFile." to ".$outCsv."\n\r";
    srt_to_csv($srtFile, $outCsv);
}
