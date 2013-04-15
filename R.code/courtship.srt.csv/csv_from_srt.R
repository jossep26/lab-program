read.srt <- function(file="", encoding="unknown")
{## reads in and parse .srt subtitles to a data frame

    # initializing input file selection
    if (file=="")
    {
        file <- choose.files()
        if ( is.na(file) )
        {
            print("File selection has been canceled.")
            return(NULL)
        }
    }
    
    # check filename integrety
    basefnInput <- basename(file)
    if (grepl("^[.~]", basefnInput) | !grepl("[.]srt$", basefnInput))
    {
        print("Wrong filename. Filename should end with '.srt' and not start with '.' or '~'.")
        return(NULL)
    }
    
    # assumes appropriate encoding
    lines <- readLines(file, encoding=encoding, warn=FALSE)

    # append at the end an "empty line" to compensate for those not having one already
    lines <- c(lines, "")

    idTimeLines <- grep("^[0-9][0-9]:[0-9][0-9]:[0-9][0-9],[0-9][0-9][0-9] --> [0-9][0-9]:[0-9][0-9]:[0-9][0-9],[0-9][0-9][0-9]", lines)
    idEmptyLines <- grep("^$", lines)

    # one time line correspond to one subtitle
    nSubtitles <- length(idTimeLines)
    
    if (!nSubtitles) return(NULL)

    # initiate subtitle data holder, a data frame
    dfSubtitles <- data.frame(text = rep("", nSubtitles), start_miliSec = rep(NA, nSubtitles), end_miliSec = rep(NA, nSubtitles), stringsAsFactors=FALSE)

    for (iSubtitle in 1:nSubtitles)
    {
        # get the start and end time
        thisTimeLine <- lines[idTimeLines[iSubtitle]]
        mixedTime <- unlist(strsplit(thisTimeLine, " --> "))
        
        dfSubtitles[iSubtitle, "start_miliSec"] <- msFromSrtTime(mixedTime[1])
        dfSubtitles[iSubtitle, "end_miliSec"] <- msFromSrtTime(mixedTime[2])
        
        # get the text, i.e. from the next line to just before the first empty line
        idTextStartLine <- idTimeLines[iSubtitle] + 1
        idTextEndLine <- min(idEmptyLines[idEmptyLines > idTimeLines[iSubtitle]]) - 1
        if (idTextStartLine == idTextEndLine)
        {
            dfSubtitles[iSubtitle, "text"] <- lines[idTextStartLine]
        } else if (idTextStartLine < idTextEndLine) {
            dfSubtitles[iSubtitle, "text"] <- paste(lines[(idTextStartLine:idTextEndLine)],sep="",collapse="\n")
        }
    }
    
    return(dfSubtitles)
}

msFromSrtTime <- function(srtTime = "")
{
    miliSec <- NULL
    
    if (grepl("^[0-9][0-9]:[0-9][0-9]:[0-9][0-9],[0-9][0-9][0-9]$", srtTime))
    {
        timeVector <- unlist(strsplit(srtTime, "[:,]"))
        miliSec <- as.integer(timeVector[4]) + 
                   as.integer(timeVector[3])*1000 + 
                   as.integer(timeVector[2])*60*1000 +
                   as.integer(timeVector[1])*60*60*1000
    }
    
    return(miliSec)
}

csvFromSrt <- function(ffnInput="", ffnOutput="")
{# TODO: wrong output for multi-line text

    # initializing input file selection
    if (ffnInput=="")
    {
        ffnInput <- choose.files()
        if ( is.na(ffnInput) )
        {
            print("File selection has been canceled.")
            return(NULL)
        }
    }
    
    # check filename integrety
    basefnInput <- basename(ffnInput)
    if (grepl("^[.~]", basefnInput) | !grepl("[.]srt$", basefnInput))
    {
        print("Wrong filename. Filename should end with '.srt' and not start with '.' or '~'.")
        return(NULL)
    }
    
    dfSubtitles <- read.srt(ffnInput)
    
    # prepare output file, write to .srt.csv file
    # get bare filename from input(base filename), i.e. strip the last .*
    barefnInput <- sub("[.][^.]*$", "\\1", basefnInput, perl=T)
    
    ffnOutput <- paste("./", barefnInput, ".srt.csv", sep="")
    if (!file.exists(ffnOutput))
    {
        write.csv(dfSubtitles, file=ffnOutput, row.names=FALSE)
        print(paste("Output done for", barefnInput))
    } else {
        print(paste("WARNING:", barefnInput, " not saved -- CSV file already exists!"))
    }
}

csvFromSrtBatch <- function(indir = "", outdir = "")
{
    # initializing directory selection
    if (indir=="")
    {
        indir <- choose.dir()
        if ( is.na(indir) )
        {
            print("Directory selection has been canceled.")
            return(NULL)
        }
    }
    
    if (outdir=="")
    {
        outdir <- indir
    }
    
    # reading file list
    flistSrtFile <- list.files(path=indir, pattern="*.srt", full.names=TRUE)
    if ( identical(flistSrtFile, character(0)) ) 
    {
        print("No .srt file detected.")
        return(NULL)
    }
    nFile <- length(flistSrtFile)
    
    
    for ( iFile in 1:nFile )
    {
        csvFromSrt(ffnInput=flistSrtFile[iFile])
    }
}
