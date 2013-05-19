splitCourtshipFile <- function(file, startText="start", preName="", postName="")
{# Will split file into 2 separate ones, with split time = start time in startText

    if(!exists("readCourtshipFile", mode="function"))
    {
        print("Requires 'summaryForCourtship.R'. Do source('full\\path\\to\\summaryForCourtship.R')")
        return(NULL)
    }

    data <- readCourtshipFile(file)

    if (sum(data$text==startText) != 1)
    {
        warning(paste("Require 1 and only 1 '", startText, "' event."))
        return(NULL)
    }

    split_time <- data[data$text==startText, 'start_miliSec']

    # get the first part by checking start time
    data_pre <- data[data$start_miliSec < split_time, ]

    # truncate end time in the first part
    if (sum(data_pre$end_miliSec>split_time, na.rm=TRUE)!=0)
    {
        data_pre[data_pre$end_miliSec>split_time, 'end_miliSec'] <- split_time
    }

    # get the second part by checking end time
    data_post <- data[data$end_miliSec >= split_time, ]

    # truncate start time in the second part
    if (sum(data_post$start_miliSec<split_time, na.rm=TRUE)!=0)
    {
        data_post[data_post$start_miliSec<split_time, 'start_miliSec'] <- split_time
    }

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