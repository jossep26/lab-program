splitCourtshipFile <- function(file, startText="start", preName="", postName="")
{# Will split file into 2 separate ones, with split time = start time in startText

    if(!exists("readCourtshipFile", mode="function"))
    {
        print("Requires 'summaryForCourtship.R'. Do source('full\\path\\to\\summaryForCourtship.R')")
        return(NULL)
    }

    data <- readCourtshipFile(file)

    if (sum(data$text==startText) > 1)
    {
        warning(paste(file, ": Require 0 or 1 '", startText, "' event.", sep=""))
        return(NULL)
    }

    if (sum(data$text==startText) == 0)
    {
        print(paste(file, ": No '", startText, "' detected.", sep=""))

        write.csv(format(data, scientific=FALSE), file=preName, row.names=FALSE)

        print(paste("Saved as first part to", preName))
        return()
    }

    split_time <- data[data$text==startText, 'start_miliSec']

    # get the first part by checking start time
    data_pre <- data[data$start_miliSec < split_time, ]

    # truncate end time in the first part
    if (sum(data_pre$end_miliSec>split_time, na.rm=TRUE)!=0)
    {
        data_pre[data_pre$end_miliSec>split_time, 'end_miliSec'] <- split_time
    }

    data_pre <- data_pre[with(data_pre, order(start_miliSec, end_miliSec)), ]

    # get the second part by checking end time
    data_post <- data[data$end_miliSec >= split_time, ]
    data_post[data_post$text==startText, 'text'] <- "start"

    # truncate start time in the second part
    if (sum(data_post$start_miliSec<split_time, na.rm=TRUE)!=0)
    {
        data_post[data_post$start_miliSec<split_time, 'start_miliSec'] <- split_time
    }

    data_post <- data_post[with(data_post, order(start_miliSec, end_miliSec)), ]

    dir_in <- dirname(file)
    barefnInput <- sub("[.][^.]*$", "\\1", basename(file), perl=T)
    ext_full <- sub("[^.]+", "\\1", basename(file), perl=T)

    if (preName == "")
    {
        preName <- paste(dir_in, "/", barefnInput, "_pre", ".csv", sep="")
    }

    if (postName == "")
    {
        postName <- paste(dir_in, "/", barefnInput, "_post", ".csv", sep="")
    }

    if (!file.exists(preName))
    {
        write.csv(format(data_pre, scientific=FALSE), file=preName, row.names=FALSE)
        print(paste("Output first part of", file, "to", preName))
    } else {
        print(paste("WARNING:", preName, " NOT saved -- file already exists!"))
    }

    if (!file.exists(postName))
    {
        write.csv(format(data_post, scientific=FALSE), file=postName, row.names=FALSE)
        print(paste("Output second part of", file, "to", postName))
    } else {
        print(paste("WARNING:", postName, " NOT saved -- file already exists!"))
    }
}


batchSplitCourtshipFile <- function(dir="", startText="start", addToPre="", addToPost="")
{# will do batch split files on a directory
    # initializing directory selection
    if (dir=="")
    {
        dir <- choose.dir(default=getwd(), caption="Select Directory of courtship files")
        if ( is.na(dir) )
        {
            print("Directory selection has been canceled.")
            return(NULL)
        }
    }

    listFile <- getCourtshipFileList(dir=dir, readSrt=TRUE)

    if (is.null(listFile))
        return(NULL)

    nFile <- length(listFile)

    # iterate through each file, calculating each summary, then inject them to blocks(rows) of previously prepared data frame
    for ( iFile in 1:nFile )
    {
        print(paste("Begin splitting", listFile[iFile], "..."))

        barefnInput <- sub("[.][^.]*$", "\\1", basename(listFile[iFile]), perl=T)

        preName <- paste(dir, "/", barefnInput, addToPre, ".csv", sep="")
        postName <- paste(dir, "/", barefnInput, addToPost, ".csv", sep="")        
        
        splitCourtshipFile(file=listFile[iFile], startText=startText, preName=preName, postName=postName)
    }

}