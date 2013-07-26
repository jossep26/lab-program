createCourtshipDf <- function(nRows)
{# tool function

    # createCourtshipDf will create an empty data frame for holding courtship summary
    df <- data.frame(filename = rep("", nRows), category = rep("", nRows), 
                total_time = rep("", nRows), occurrence = rep(as.integer(NA), nRows), 
                time_percent = rep(NA, nRows), time = rep(as.integer(NA), nRows), 
                time_percent_nc = rep(NA, nRows), time_nc = rep(as.integer(NA), nRows), 
                stringsAsFactors=FALSE)
    
    return(df)
}

barename <- function(fn)
{# tool function

    # barename returns stripped filename without extension
    # strip all extensions, e.g. base.ext.ension --> base
    return(sub("[.].*$", "\\1", basename(fn), perl=T))

}

readCourtshipFile <- function(file)
{# tool function

    # readCourtshipFile returns a data frame from .srt or .csv file that contains courtship analysis data

    basefnInput <- basename(file)

    if(grepl("[.]srt$", basefnInput))
    {
        if(!exists("read.srt", mode="function"))
        {
            print("Requires 'csv_from_srt.R'. Do source('full\\path\\to\\csv_from_srt.R')")
            return(NULL)
        }

        data<-read.srt(file=file)
    }
    else if(grepl("[.]csv$", basefnInput))
    {
        data<-read.csv(file=file, header=T)
    }
    else
    {
        print("Cannot read file other than .srt or .csv")
        return(NULL)
    }
    
    return(data)
}

getCourtshipFileList <- function(dir="", readSrt=TRUE)
{# tool function
    #  getCourtshipFileList will return a list of courtship analysis files in specified directory. Will try to read .srt files by default; if not found any, will try to read .srt.csv files. Or when readSrt=FALSE will try to read .srt.csv first.
    #  NOTE: When readSrt=TRUE (default), even if one .srt file exist, will not try to read any .srt.csv files.

    # initializing directory selection
    if (dir=="")
    {
        dir <- choose.dir(default=getwd(), caption="Select Folder containing courtship files")
        if ( is.na(dir) ) 
        {
            print("Directory selection has been canceled.")
            return(NULL)
        }
    }

    if (readSrt)
    {# attempt to read .srt, if none exists, read .srt.csv. 
        if(!exists("read.srt", mode="function"))
        {
            print("Requires 'csv_from_srt.R'. Do source('full\\path\\to\\csv_from_srt.R')")
            return(NULL)
        }

        listFile <- list.files(path=dir, pattern="*[.]srt$", full.names=TRUE)
        if ( identical(listFile, character(0)) ) 
        {
            listFile <- list.files(path=dir, pattern="[.]srt.csv$", full.names=TRUE)
            if ( identical(listFile, character(0)) ) 
            {
                warning("No .srt.csv or .srt files detected.")
            }
        }
    }
    else
    {# attempt to read .srt.csv, if none exists, read .srt
        listFile <- list.files(path=dir, pattern="[.]srt.csv$", full.names=TRUE)
        if ( identical(listFile, character(0)) ) 
        {
            listFile <- list.files(path=dir, pattern="[.]csv$", full.names=TRUE)
            if ( identical(listFile, character(0)) ) 
            {
                warning("No .srt.csv or .csv files detected.")
            }
        }
    }

    return(listFile)
}

sumDfCourtshipByTL <- function(TL, textCatg, dfCourtship)
{#  sumDfCourtshipByTL will return summary about the given behavior category and occurrence of _A_ given 'category' within _A_ given time length in a courtship data frame
    #  IMPORTANT: assumes start time(i.e. offset) = 0
    #  IMPORTANT: if event's end time > TL, the end time is set to TL

    if(!is.integer(TL))
    {
        print("TL must be an integer indicating mili-seconds!")
        return(NULL)
    }

    if(!is.character(textCatg))
    {
        print("textCatg must be a string indicating behavioral category!")
        return(NULL)
    }

    # prepare output data frame
    sumDf <- data.frame(category = textCatg, total_time = TL, time_percent = NA, time = NA, occurrence = NA, stringsAsFactors=FALSE)

    # if category does not exist, all the summary should be NA
    ckCatg <- dfCourtship$text==textCatg
    if (sum(ckCatg, na.rm=TRUE)==0) 
        return(sumDf)

    # select relevant columns, for the given category and time length
    courtshipTextCatg <- dfCourtship[(dfCourtship$text==textCatg)&(dfCourtship$start_miliSec<TL), c('start_miliSec', 'end_miliSec')]
    
    # truncate if any 'end' time exceeds the given time length
    if (sum(courtshipTextCatg$end_miliSec>TL, na.rm=TRUE)!=0)
    {
        courtshipTextCatg[courtshipTextCatg$end_miliSec>TL, 'end_miliSec'] <- TL
    }
    
    # re-calculate all the intervals
    courtshipTextCatg[, 'interval_miliSec'] <- courtshipTextCatg[, 'end_miliSec'] - courtshipTextCatg[, 'start_miliSec']

    # calculate the fraction of time of this category, in this time length
    sumDf$time <- as.integer(sum(courtshipTextCatg[, 'interval_miliSec']))
    sumDf$time_percent <- sumDf$time / TL

    # calculate the occurrence of this behavior category (namely the number of rows)
    sumDf$occurrence <- length(courtshipTextCatg[, 'interval_miliSec'])
  
    return(sumDf)
}

sumCourtshipFile <- function(file, listTL=as.integer(c(60000, 120000, 180000, 240000, 300000)), listCatg=c('wing_extension', 'orientation', 'courtship'), failOnStartTime=TRUE)
{# sumCourtshipSrt will analyze a .srt(.csv) file for a summary of each provided category by each provided time length 
    # IMPORTANT: expects one and only one 'latency'(or 'start') event indicating true start(not video start, rather experiment start)

    if(!is.numeric(listTL))
    {
        print("listTL must be an array of integers, indicating mili-seconds.")
        return(NULL)
    }
    listTL <- sort(as.integer(listTL), decreasing=FALSE)

    if(!is.character(listCatg))
    {
        print("listCatg must be an array of strings, indicating behavioral categories")
        return(NULL)
    }

    courtshipData <- readCourtshipFile(file)
    
    if (is.null(courtshipData))
        return(NULL)
 
    # strip all extensions, e.g. base.ext.ension --> base
    fn <- barename(file)

   # get start time
    if (sum(courtshipData$text=='latency') == 1)
    {# exactly one "latency" event indicate true start of the experiment
        TS <- courtshipData[courtshipData$text=='latency', 'start_miliSec']
    } 
    else if (sum(courtshipData$text=='start') == 1)
    {# one "start" event also indicate true start of the experiment
        TS <- courtshipData[courtshipData$text=='start', 'start_miliSec']
    }
    else 
    {# otherwise assume start time = 0
        if(failOnStartTime)
        {
            stop("Cannot find session start time: one and only one 'latency' or 'start' event required\nUse 0 instead by setting failOnStartTime=FALSE")
        }
        else 
        {
            TS <- 0
            warning("Cannot find 'latency' or 'start' event, true experiment start is guessed as 0")
        }
    }
    
    # re-calibrate(offset) time using start time
    courtshipData$start_miliSec <- courtshipData$start_miliSec - TS
    courtshipData$end_miliSec <- courtshipData$end_miliSec - TS
    
    nTL <- length(listTL)
    nCatg <- length(listCatg) 
    # initialize summary data frame use tool function
    dfCatg <- createCourtshipDf(nCatg*nTL)
    
    fn <- barename(file)
    # iterate through each time length and each category, putting info. one by one
    for ( iCatg in 1:nCatg) 
        {
        for ( iTL in 1:nTL)
            {
                dfCatg[(iCatg-1)*nTL+iTL, 'filename'] <- fn
                
                tmpDfCatg <- sumDfCourtshipByTL(listTL[iTL], listCatg[iCatg], courtshipData)
                dfCatg[(iCatg-1)*nTL+iTL, 'category'] <- tmpDfCatg[, 'category']
                dfCatg[(iCatg-1)*nTL+iTL, 'total_time'] <- tmpDfCatg[, 'total_time']
                dfCatg[(iCatg-1)*nTL+iTL, 'occurrence'] <- tmpDfCatg[, 'occurrence']
                dfCatg[(iCatg-1)*nTL+iTL, 'time'] <- tmpDfCatg[, 'time']
                dfCatg[(iCatg-1)*nTL+iTL, 'time_percent'] <- tmpDfCatg[, 'time_percent']
                dfCatg[(iCatg-1)*nTL+iTL, 'time_nc'] <- tmpDfCatg[, 'time']
                dfCatg[(iCatg-1)*nTL+iTL, 'time_percent_nc'] <- tmpDfCatg[, 'time_percent']
                
                if (iTL >= 2)
                {# non-cumulative time = current - previous time(data frame line)
                    dfCatg[(iCatg-1)*nTL+iTL, 'time_nc'] <- tmpDfCatg[, 'time'] - dfCatg[(iCatg-1)*nTL+iTL-1, 'time']
                    dfCatg[(iCatg-1)*nTL+iTL, 'time_percent_nc'] <- dfCatg[(iCatg-1)*nTL+iTL, 'time_nc']/(listTL[iTL] - listTL[iTL-1])
                }

                tmpDfCatg <- NULL
            }
        }
     
    return(dfCatg)
}

sumCourtshipSrt <- function(srtfile, listTL=as.integer(c(60000, 120000, 180000, 240000, 300000)), listCatg=c('wing_extension', 'orientation'), failOnStartTime=TRUE)
{# sumCourtshipSrt will analyze a .srt file for a summary of each provided category by each provided time length 
    # IMPORTANT: expects one and only one 'latency' event indicating true start(not video start)
    # DEPRECATED: use sumCourtshipFile instead
    
    return(sumCourtshipFile(file=srtfile, listTL=listTL, listCatg=listCatg, failOnStartTime=failOnStartTime))

    # nTL <- length(listTL)
    # nCatg <- length(listCatg)  
    # # strip all extensions, e.g. base.ext.ension --> base
    # fn <- barename(srtfile)

    # if(!exists("read.srt", mode="function"))
    # {
    #     warning("Requires 'csv_from_srt.R'. Do source('full\\path\\to\\csv_from_srt.R')")
    # }
    # b<-read.srt(file=srtfile)
    
    # # get start time
    # if (sum(b$text=='latency') == 1)
    # {# exactly one "latency" event indicate true start of the experiment
    #     TS <- b[b$text=='latency', 'start_miliSec']
    # } 
    # else 
    # {# otherwise assume start time = 0
    #     TS <- 0

    #     if(failOnStartTime)
    #         stop("Cannot find session start time: one and only one 'latency' event required\n\tUse first event instead by setting failOnStartTime=FALSE")
    #     else 
    #         warning("'latency' event not valid, true start was gussesd as 0")
    # }
    
    # # re-calibrate(offset) time using start time
    # b$start_miliSec <- b$start_miliSec - TS
    # b$end_miliSec <- b$end_miliSec - TS
    
    # # initialize summary data frame use tool function
    # # dfCatg <- data.frame(filename = rep(fn, nCatg*nTL), category = rep("", nCatg*nTL), total_time = rep("", nCatg*nTL), time_percent = rep(NA, nCatg*nTL), occurrence = rep(NA, nCatg*nTL), stringsAsFactors=FALSE)
    # dfCatg <- createCourtshipDf(nCatg*nTL)
    
    # # iterate through each time lenght and each category, putting info. one by one
    # for ( iCatg in 1:nCatg) 
    #     {
    #     for ( iTL in 1:nTL)
    #         {
    #             dfCatg[(iCatg-1)*nTL+iTL, 'filename'] <- fn
                
    #             tmpDfCatg <- sumDfCourtshipByTL(listTL[iTL], listCatg[iCatg], b)
    #             dfCatg[(iCatg-1)*nTL+iTL, 'category'] <- tmpDfCatg[, 'category']
    #             dfCatg[(iCatg-1)*nTL+iTL, 'total_time'] <- tmpDfCatg[, 'total_time']
    #             dfCatg[(iCatg-1)*nTL+iTL, 'time_percent'] <- tmpDfCatg[, 'time_percent']
    #             dfCatg[(iCatg-1)*nTL+iTL, 'occurrence'] <- tmpDfCatg[, 'occurrence']
                
    #             tmpDfCatg <- NULL
    #         }
    #     }
     
    # return(dfCatg)
}

sumCourtshipCsv <- function(csvfile, listTL=as.integer(c(60000, 120000, 180000, 240000, 300000)), listCatg=c('wing_extension', 'orientation'), failOnStartTime=TRUE)
{# sumCourtshipCsv will analyze a .srt.csv file for a summary of each provided category by each provided time length 
    # IMPORTANT: expects one and only one 'latency' event indicating true start(not video start)
    # DEPRECATED: use sumCourtshipFile instead
    
    return(sumCourtshipFile(file=csvfile, listTL=listTL, listCatg=listCatg, failOnStartTime=failOnStartTime))

    # nTL <- length(listTL)
    # nCatg <- length(listCatg)  
    # # strip all extensions, e.g. base.ext.ension --> base
    # fn <- barename(csvfile)
    
    # b<-read.csv(file=csvfile, header=T)
    
    # # get start time
    # if (sum(b$text=='latency') == 1)
    # {# exactly one "latency" event indicate true start of the experiment
    #     TS <- b[b$text=='latency', 'start_miliSec']
    # } 
    # else 
    # {# otherwise assume start time = 0
    #     TS <- 0

    #     if(failOnStartTime)
    #         stop("Cannot find session start time: one and only one 'latency' event required\n\tUse first event instead by setting failOnStartTime=FALSE")
    #     else 
    #         warning("'latency' event not valid, true start was gussesd as 0")
    # }
    
    # # re-calibrate(offset) time using start time
    # b$start_miliSec <- b$start_miliSec - TS
    # b$end_miliSec <- b$end_miliSec - TS
    
    # # initialize summary data frame use tool function
    # # dfCatg <- data.frame(filename = rep(fn, nCatg*nTL), category = rep("", nCatg*nTL), total_time = rep("", nCatg*nTL), time_percent = rep(NA, nCatg*nTL), occurrence = rep(NA, nCatg*nTL), stringsAsFactors=FALSE)
    # dfCatg <- createCourtshipDf(nCatg*nTL)
    
    # # iterate through each time lenght and each category, putting info. one by one
    # for ( iCatg in 1:nCatg) 
    #     {
    #     for ( iTL in 1:nTL)
    #         {
    #             dfCatg[(iCatg-1)*nTL+iTL, 'filename'] <- fn
                
    #             tmpDfCatg <- sumDfCourtshipByTL(listTL[iTL], listCatg[iCatg], b)
    #             dfCatg[(iCatg-1)*nTL+iTL, 'category'] <- tmpDfCatg[, 'category']
    #             dfCatg[(iCatg-1)*nTL+iTL, 'total_time'] <- tmpDfCatg[, 'total_time']
    #             dfCatg[(iCatg-1)*nTL+iTL, 'time_percent'] <- tmpDfCatg[, 'time_percent']
    #             dfCatg[(iCatg-1)*nTL+iTL, 'occurrence'] <- tmpDfCatg[, 'occurrence']
                
    #             tmpDfCatg <- NULL
    #         }
    #     }
     
    # return(dfCatg)
}

sumCourtshipDir <- function(dir="", readSrt=TRUE, csvDir="", out=TRUE, outfile="", listTL=as.integer(c(60000, 120000, 180000, 240000, 300000)), listCatg=c('wing_extension', 'orientation'), na.zero=FALSE, failOnStartTime=TRUE)
{# sumCourtshipDir will calculate and return a summary of analysed srt files (the csvs)
    # it also output csv summary files
    
    # compatibility to older versions
    if (dir=="")
    {
        dir = csvDir
    }

    listFile <- getCourtshipFileList(dir=dir, readSrt=readSrt)

    if (is.null(listFile))
        return(NULL)

    nFile <- length(listFile)

    # preparing Time Length list (a vector of time points) and Category list (a vector of behavioral tags)
    if(!is.numeric(listTL))
    {
        print("listTL must be an array of integers, indicating mili-seconds.")
        return(NULL)
    }
    listTL <- sort(as.integer(listTL), decreasing=FALSE)

    if(!is.character(listCatg))
    {
        print("listCatg must be an array of strings, indicating behavioral categories")
        return(NULL)
    }
    nTL= length(listTL)
    nCatg=length(listCatg)
    
    # initialize and prepare the output data frame
    sumCsv <- createCourtshipDf(nFile*nTL*nCatg)
    
    # iterate through each csv file, calculating each summary, then inject them to blocks(rows) of previously prepared data frame
    for ( iFile in 1:nFile )
    {
        print(paste("Begin processing", listFile[iFile], "..."))
        
        sumCsv[((iFile-1)*nTL*nCatg+1):(iFile*nTL*nCatg), ] <- sumCourtshipFile(listFile[iFile], listTL, listCatg, failOnStartTime=failOnStartTime)
        
        print("...done.")
    }
    
    # Copy a NA=0 version
    sumCsvNoNA <- sumCsv
    sumCsvNoNA[is.na(sumCsvNoNA$occurrence), 'occurrence'] <- 0L
    sumCsvNoNA[is.na(sumCsvNoNA$time), 'time'] <- 0L
    sumCsvNoNA[is.na(sumCsvNoNA$time_percent), 'time_percent'] <- 0L
    sumCsvNoNA[is.na(sumCsvNoNA$time_nc), 'time_nc'] <- 0L
    sumCsvNoNA[is.na(sumCsvNoNA$time_percent_nc), 'time_percent_nc'] <- 0L    
    
    # save to files
    if (out)
    {    
        if (outfile=="")
        {
            outfile <- paste(dir, "/summary.csv", sep="")
        }
    
        outfileNoNA <- paste(dir, "/summary_naIsZero.csv", sep="")
        write.csv(format(sumCsv, scientific=FALSE), file=outfile, row.names=FALSE)
        write.csv(format(sumCsvNoNA, scientific=FALSE), file=outfileNoNA, row.names=FALSE)
        print(paste("written to file", outfile, "and", outfileNoNA))
    }
    
    if (na.zero)
    {
        print("All NAs converted to 0.")
        return(sumCsvNoNA)
    }
    else
    {
        return(sumCsv)
    }
}

sumForOneCatg <- function(dfSumCourtship, catg='courtship')
{# DEPRECATED: use method summarySE in helper01.R instead

    # sumForOneCatg will do summary statistics on each experiment group for each time length
    # NOTE: Treat NA cautiously. This summary is based on ?mean(..., na.rm=FALSE)
    
    # first, get all the exp. groups and time lengths
    factoredSum <- dfSumCourtship[dfSumCourtship$category==catg,]
    # factoredSum$filename <- factor(factoredSum$filename)
    factoredSum$exp_group <- factor(factoredSum$exp_group)
    factoredSum$total_time <- factor(factoredSum$total_time)
    
    listGroup <- levels(factoredSum$exp_group)
    nGroup <- length(listGroup)
    
    # sort time length for a bit nicer-looking output
    listTL <- as.character(sort(as.integer(levels(factoredSum$total_time))))
    nTL <- length(listTL)
    
    # initialize data frame for summary, structure as follows
    # exp_group  total_time  mean_time_percent  sem_time_percent  mean_occurrence sem_occurrence
    nRow <- nGroup*nTL
    sumDf <- data.frame(exp_group=rep("",nRow), total_time=rep("",nRow), mean_time_percent=rep(NA, nRow), sem_time_percent=rep(NA,nRow), mean_occurrence=rep(NA,nRow), sem_occurrence=rep(NA, nRow), stringsAsFactors=FALSE)
    
    # inject the summaries one by one
    for ( iGroup in 1:nGroup )
    {
        for ( iTL in 1:nTL )
        {
            sumDf[(iGroup-1)*nTL+iTL, 'exp_group'] <- listGroup[iGroup]
            sumDf[(iGroup-1)*nTL+iTL, 'total_time'] <- listTL[iTL]
            
            tmpDfSum <- dfSumCourtship[(dfSumCourtship$exp_group==listGroup[iGroup])&(dfSumCourtship$total_time==listTL[iTL]), ]
            
            tmpTimePercent <- tmpDfSum$time_percent
            sumDf[(iGroup-1)*nTL+iTL, 'mean_time_percent'] <- mean(tmpTimePercent)
            sumDf[(iGroup-1)*nTL+iTL, 'sem_time_percent'] <- sd(tmpTimePercent)/sqrt(sum(!is.na(tmpTimePercent)))
            
            tmpOccurence <- tmpDfSum$occurrence
            sumDf[(iGroup-1)*nTL+iTL, 'mean_occurrence'] <- mean(tmpOccurence)
            sumDf[(iGroup-1)*nTL+iTL, 'sem_occurrence'] <- sd(tmpOccurence)/sqrt(sum(!is.na(tmpOccurence)))
            
            tmpDfSum <- NULL
            tmpTimePercent <- NULL
            tmpOccurence <- NULL
        }
    }
    
    return(sumDf)
}

sumCatgForAll <- function(dfSumCourtship)
{# DEPRECATED: use method summarySE in helper01.R instead

    # sumCatgForAll will do summary statistics on each category for each time length
    # NOTE: Treat NA cautiously. This summary is based on ?mean(..., na.rm=FALSE)
    
    # first, get all the categories and time lengths
    factoredSum <- dfSumCourtship
    # factoredSum$filename <- factor(factoredSum$filename)
    factoredSum$category <- factor(factoredSum$category)
    factoredSum$total_time <- factor(factoredSum$total_time)
    
    listCatg <- levels(factoredSum$category)
    nCatg <- length(listCatg)
    
    # sort time length for a bit nicer-looking output
    listTL <- as.character(sort(as.integer(levels(factoredSum$total_time))))
    nTL <- length(listTL)
    
    # initialize data frame for summary, structure as follows
    # category  total_time  mean_time_percent  sem_time_percent  mean_occurrence sem_occurrence
    nRow <- nCatg*nTL
    sumDf <- data.frame(category=rep("",nRow), total_time=rep("",nRow), mean_time_percent=rep(NA, nRow), sem_time_percent=rep(NA,nRow), mean_occurrence=rep(NA,nRow), sem_occurrence=rep(NA,nRow), stringsAsFactors=FALSE)
    
    # inject the summaries one by one
    for ( iCatg in 1:nCatg)
    {
        for ( iTL in 1:nTL )
        {
            sumDf[(iCatg-1)*nTL+iTL, 'category'] <- listCatg[iCatg]
            sumDf[(iCatg-1)*nTL+iTL, 'total_time'] <- listTL[iTL]
            
            tmpDfSum <- dfSumCourtship[(dfSumCourtship$category==listCatg[iCatg])&(dfSumCourtship$total_time==listTL[iTL]), ]
            
            tmpTimePercent <- tmpDfSum$time_percent
            sumDf[(iCatg-1)*nTL+iTL, 'mean_time_percent'] <- mean(tmpTimePercent)
            sumDf[(iCatg-1)*nTL+iTL, 'sem_time_percent'] <- sd(tmpTimePercent)/sqrt(sum(!is.na(tmpTimePercent)))
            
            tmpOccurence <- tmpDfSum$occurrence
            sumDf[(iCatg-1)*nTL+iTL, 'mean_occurrence'] <- mean(tmpOccurence)
            sumDf[(iCatg-1)*nTL+iTL, 'sem_occurrence'] <- sd(tmpOccurence)/sqrt(sum(!is.na(tmpOccurence)))
            
            tmpDfSum <- NULL
            tmpTimePercent <- NULL
            tmpOccurence <- NULL
        }
    }
    
    return(sumDf)
}

readCourtshipLatency <- function(latencyText="latency", dir="", csvDir="", readSrt=TRUE, out=TRUE, outfile="")
{# readCourtshipLatency returns a data frame of 'latency' interval of all valid files in a directory.
    # IMPORTANT: assumes 1 and only 1 'latency' event per file, otherwise produces NA

    # compatibility to older versions
    if (dir=="")
    {
        dir = csvDir
    }

    listFile <- getCourtshipFileList(dir=dir, readSrt=readSrt)

    if (is.null(listFile))
        return(NULL)

    nFile <- length(listFile)
    
    # prepare output
    latencyDf <- data.frame(filename=rep("", nFile), latency=rep(NA, nFile), stringsAsFactors=FALSE)
    colnames(latencyDf)[2] <- latencyText
    
    # calculate 'latency' interval, don't terminate when wrong
    for ( iFile in 1:nFile )
    {
        print(paste("Reading", listFile[iFile], "..."))
        
        tmpDf <- readCourtshipFile(file=listFile[iFile])
        tmpDf <- tmpDf[tmpDf$text==latencyText, c('start_miliSec', 'end_miliSec')]
        
        latencyDf[iFile, 'filename'] <- barename(listFile[iFile])
        
        if ( (!is.null(tmpDf))&(nrow(tmpDf)==as.integer(1)) )
        {
            latencyDf[iFile, latencyText] <- tmpDf[, 'end_miliSec'] - tmpDf[, 'start_miliSec']
            print("...done.")
        }
        else
        {
            print("...wrong!")
        }

        tmpDf <- NULL
    }
    
    if (out)
    {
        if (outfile=="")
        {
            outfile <- paste(dir, "/", latencyText, ".csv", sep="")
        }
        write.csv(format(latencyDf, scientific=FALSE), file=outfile, row.names=FALSE)
        print(paste("Written results to file", outfile))
    }
    
    return(latencyDf)
}

readFirstCourtshipBout <- function(boutText="courtship bout", dir="", csvDir="", readSrt=TRUE, out=TRUE, outfile="")
{# readCourtshipBout returns a data frame of first 'courtship bout' intervals of all valid files in a directory.
    # IMPORTANT: assumes at least 1 'courtship bout' event per file, otherwise produces NA

    # compatibility to older versions
    if (dir=="")
    {
        dir = csvDir
    }

    listFile <- getCourtshipFileList(dir=dir, readSrt=readSrt)

    if (is.null(listFile))
        return(NULL)

    nFile <- length(listFile)
    
    # prepare output
    boutDf <- data.frame(filename=rep("", nFile), duration=rep(NA, nFile), stringsAsFactors=FALSE)
    # colnames(boutDf)[2] <- boutText
    
    # calculate first 'bout' interval, don't terminate when wrong
    for ( iFile in 1:nFile )
    {
        print(paste("Reading", listFile[iFile], "..."))
        
        tmpDf <- readCourtshipFile(file=listFile[iFile])
        tmpDf <- tmpDf[tmpDf$text==boutText, c('start_miliSec', 'end_miliSec')]
        tmpDf <- tmpDf[with(tmpDf, order('start_miliSec')), ]
        
        boutDf[iFile, 'filename'] <- barename(listFile[iFile])
        
        if ( (!is.null(tmpDf))&(nrow(tmpDf)>=as.integer(1)) )
        {
            boutDf[iFile, 'duration'] <- tmpDf[1, 'end_miliSec'] - tmpDf[1, 'start_miliSec']
            print("...done.")
        }
        else
        {
            print("...wrong!")
        }

        tmpDf <- NULL
    }
    
    if (out)
    {
        if (outfile=="")
        {
            outfile <- paste(dir, "/", boutText, ".csv", sep="")
        }
        write.csv(format(boutDf, scientific=FALSE), file=outfile, row.names=FALSE)
        print(paste("Written results to file", outfile))
    }
    
    return(boutDf)
}

unblindCourtshipCsv <- function(summaryCsv="", unblindCsv="")
{# This will translate filename into experiment categories for existing summary csv file

    # initializing file selection
    if (summaryCsv=="")
    {
        summaryCsv <- choose.files(caption="Select SUMMARY csv file")
        if ( identical(summaryCsv, character(0)) ) 
        {
            print("File selection has been canceled.")
            return(NULL)
        }
    }
    
    if (unblindCsv=="")
    {
        unblindCsv <- choose.files(caption="Select UNBLIND csv file")
        if ( identical(unblindCsv, character(0)) ) 
        {
            print("File selection has been canceled.")
            return(NULL)
        }
    }
    
    sumDf <- read.csv(file=summaryCsv, stringsAsFactors=F)
    sumDf <- transform(sumDf, filename = barename(filename))
    unblind <- read.csv(file=unblindCsv, stringsAsFactors=F)
    unblind <- transform(unblind, filename = barename(filename))
    
    unblind_data <- merge(sumDf, unblind, by='filename')
    if ('total_time' %in% colnames(unblind_data) )
    {# there must be a reason for this, but i have forgotten
        unblind_data <- transform(unblind_data, total_time = as.character(as.integer(total_time)))
    }
    #unblind_data <- transform(unblind_data, total_time = as.character(total_time))
    
    return(unblind_data)
}

unblindCourtshipDf <- function(data, unblind="")
{# This will translate filename into experiment categories for existing summary csv file

    #
    if (is.null(data))
    {
        print("Invalid input data frame!")
        return()
    }

    # initializing file selection
    if (unblind=="")
    {
        unblind <- choose.files(caption="Select UNBLIND csv file")
        if ( identical(unblind, character(0)) ) 
        {
            print("File selection has been canceled.")
            return(NULL)
        }
    }
    
    sumDf <- data
    sumDf <- transform(sumDf, filename = barename(filename))
    ubDf <- read.csv(file=unblind, stringsAsFactors=F)
    ubDf <- transform(ubDf, filename = barename(filename))
    
    unblind_data <- merge(sumDf, ubDf, by='filename')

    if ('total_time' %in% colnames(unblind_data) )
    {# there must be a reason for this, but i have forgotten :(
        unblind_data <- transform(unblind_data, total_time = as.character(as.integer(total_time)))
    }
    #unblind_data <- transform(unblind_data, total_time = as.character(total_time))
    
    return(unblind_data)
}

sumAndUnblindCourtshipDir <- function(dir="", readSrt=TRUE, csvDir="", unblindFile="", out=FALSE, listCatg=c('courtship'), listTL=as.integer(c(60000, 120000, 180000, 240000, 300000)), na.zero=TRUE)
{# sumAndUnblindCourtshipDir will summarize all the courtship files(*.srt / *.srt.csv), and add exp_group etc. info into all the lines in summary(unblinding). 
    
    # compatibility to older versions
    if (dir=="")
        dir <- csvDir

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

    if (unblindFile=="")
    {
        unblindFile <- choose.files(default=paste(dir, "/unblind.csv", sep=""), caption="Select UNBLIND csv file")
        if ( identical(unblindFile, character(0)) ) 
        {
            print("Ublind file selection has been canceled.")
            return(NULL)
        }
    }
    
    # do summary analysis on all courtship files
    sumDf <- sumCourtshipDir(dir=dir, readSrt=readSrt, out=out, listCatg=listCatg, listTL=listTL, na.zero=na.zero)
    sumDf <- transform(sumDf, filename = barename(filename))

    # prepare 'unblind' data
    unblind <- read.csv(file=unblindFile, stringsAsFactors=F)
    unblind <- transform(unblind, filename = barename(filename))
    
    print("Adding experimental group info (Unblinding)...")

    unblind_data <- merge(sumDf, unblind, by='filename')
    if ('total_time' %in% colnames(unblind_data) )
    {
        unblind_data <- transform(unblind_data, total_time = as.integer(total_time))
    }
    
    print("...added.")
    
    if (out)
    {
        outfile <- paste(dir, "/unblinded_summary.csv", sep="")
        write.csv(format(unblind_data, scientific=FALSE), file=outfile, row.names=FALSE)
        print(paste("Written results to file", outfile))
    }
    
    return(unblind_data)
}

readAndUnblindCourtshipLatency <- function(dir="", readSrt=TRUE, csvDir="", unblindFile="", out=FALSE, latencyText="latency", no.na=FALSE, na.to=0L)
{# readAndUnblindCourtshipLatency will summarize all the *.srt.csv files, and add exp_group etc. info into all the lines in summary(unblinding). 
    
    # compatibility to older versions
    if (dir=="")
        dir <- csvDir

    # initializing directory selection
    if (dir=="")
    {
        dir <- choose.dir(default=getwd(), caption="Select Directory of courtship files for latency")
        if ( is.na(dir) )
        {
            print("Directory selection has been canceled.")
            return(NULL)
        }
    }
    
    if (unblindFile=="")
    {
        unblindFile <- choose.files(default=paste(dir, "/unblind.csv", sep=""), caption="Select UNBLIND csv file")
        if ( identical(unblindFile, character(0)) ) 
        {
            print("Ublind file selection has been canceled.")
            return(NULL)
        }
    }
    
    latencyDf <- readCourtshipLatency(dir=dir, readSrt=readSrt, latencyText=latencyText, out=FALSE)
    latencyDf <- transform(latencyDf, filename = barename(filename))
    unblind <- read.csv(file=unblindFile, stringsAsFactors=F)
    unblind <- transform(unblind, filename = barename(filename))

    print("Adding experimental group info (Unblinding)...")
    unblind_data <- merge(latencyDf, unblind, by='filename')
    
    print("...added.")
    
    if (no.na && is.numeric(na.to) && (length(na.to)==1) )
    {# TODO: refactor converting NAs to a separate function
        print("Converting NAs...")
        noNA <- unblind_data

        naIds <- is.na(noNA[colnames(noNA)==latencyText])
        if (nrow(naIds) == 0L)
        {
            print("...No NA detected.")
        }
        else
        {
            noNA[naIds, latencyText] <- na.to
            print(paste("...all NAs are now converted to", na.to))
        
        }

        if (out)
        {
            noNAfile <- paste(dir, "/unblinded_", latencyText, "noNA.csv", sep="")
            write.csv(format(noNA, scientific=FALSE), file=noNAfile, row.names=FALSE)
            print(paste("Results written to file", noNAfile))            
        }

        return(noNA)
        
    }
    else
    {# don't convert NAs
        if (out)
        {
            outfile <- paste(dir, "/unblinded_", latencyText, ".csv", sep="")
            write.csv(format(unblind_data, scientific=FALSE), file=outfile, row.names=FALSE)
            print(paste("Results written to file", outfile))
        }

        return(unblind_data)
    }

    return(unblind_data)

}

###### non-cumulative time_percent #####
##  DEPRECATED: use functions above instead, already contained in output data frame

sumCourtshipCsv2 <- function(csvfile, listTL=as.integer(c(60000, 120000, 180000, 240000, 300000)), listCatg=c('wing_extension', 'orientation'))
{#  DEPRECATED: use sumCourtshipFile instead
    # sumCourtshipCsv will analyze a .srt.csv file for a summary of 
    #   each provided category by each provided time length.
    #   IMPORTANT: time_percent is non-cumulative
    

    nTL <- length(listTL)
    nCatg <- length(listCatg) 
    
    d <- sumCourtshipCsv(csvfile, listTL, listCatg)
    dfCatg <- d
    
    # calculate non-cumulative time_pecent from cumulative time_percent
    for ( iCatg in 1:nCatg )
    {
        for ( iTL in 2:nTL )
        {
            dfCatg[(dfCatg$category==listCatg[iCatg])&(dfCatg$total_time==listTL[iTL]),]$time_percent <-
            (listTL[iTL] *
             d[(d$category==listCatg[iCatg])&(d$total_time==listTL[iTL]),]$time_percent -
             listTL[iTL-1] * 
             d[(d$category==listCatg[iCatg])&(d$total_time==listTL[iTL-1]),]$time_percent
             ) / (listTL[iTL] - listTL[iTL-1])
         }
    }
    
    return(dfCatg)
}

sumCourtshipDir2 <- function(csvDir="", out=TRUE, outfile=paste(csvDir, "/summary.csv", sep=""), listTL=as.integer(c(60000, 120000, 180000, 240000, 300000)), listCatg=c('wing_extension', 'orientation'), na.zero=FALSE)
{#  DEPRECATED: use sumCourtshipDir instead
    # sumCourtshipDir will calculate and return a summary of analysed srt files (the csvs)
    # it also output csv summary files
    
    # initializing directory selection
    if (csvDir=="")
    {
        csvDir <- choose.dir()
        if ( is.na(csvDir) ) 
        {
            print("Directory selection has been canceled.")
            return(NULL)
        }
        outfile <- paste(csvDir, "/summary.csv", sep="")
    }
    
    # reading file list
    listCsv <- list.files(path=csvDir, pattern="*.srt.csv", full.names=TRUE)
    if ( identical(listCsv, character(0)) ) 
    {
        print("No .srt.csv file detected.")
        return(NULL)
    }
    nFile <- length(listCsv)

    # preparing Time Length list (a vector of time points) and Category list (a vector of behavioral tags)
    nTL= length(listTL)
    nCatg=length(listCatg)
    
    # initialize and prepare the output data frame
    sumCsv <- createCourtshipDf(nFile*nTL*nCatg)
    
    # iterate through each csv file, calculating each summary, then inject them to blocks of previously prepared data frame
    for ( iFile in 1:nFile )
    {
        print(paste("Begin processing", listCsv[iFile], "..."))
        
        sumCsv[((iFile-1)*nTL*nCatg+1):(iFile*nTL*nCatg), ] <- sumCourtshipCsv2(listCsv[iFile], listTL, listCatg)
        
        print("...done.")
    }
    
    # Copy a NA=0 version
    sumCsvNoNA <- sumCsv
    sumCsvNoNA[is.na(sumCsvNoNA$time_percent), 'time_percent'] <- 0L
    sumCsvNoNA[is.na(sumCsvNoNA$occurrence), 'occurrence'] <- 0L
    
    # save to files
    if (out)
    {
        outfileNoNA <- paste(csvDir, "/summary_noNA.csv", sep="")
        write.csv(sumCsv, file=outfile, row.names=FALSE)
        write.csv(sumCsvNoNA, file=outfileNoNA, row.names=FALSE)
        print(paste("written to file", outfile, "and", outfileNoNA))
    }
    
    if (na.zero)
    {
        print("All NAs converted to 0.")
        return(sumCsvNoNA)
    }
    else
        return(sumCsv)
}

sumAndUnblindCourtshipDir2 <- function(csvDir="", unblindFile="", out=FALSE, listCatg=c('courtship'), listTL=as.integer(c(60000, 120000, 180000, 240000, 300000)), na.zero=TRUE)
{#  DEPRECATED: use sumAndUnblindCourtshipDir instead
    # sumAndUnblindCourtshipDir will summarize all the *.srt.csv files,
    #   and add exp_group info into all the lines in summary(unblinding). 
    #   IMPORTANT: time_percent is non-cumulative
    
    # initializing directory selection
    if (csvDir=="")
    {
        csvDir <- choose.dir()
        if ( is.na(csvDir) )
        {
            print("Directory selection has been canceled.")
            return(NULL)
        }
    }
    
    if (unblindFile=="")
    {
        unblindFile <- "unblind.csv"
    }

    unblindCsv <- paste(csvDir, "/", unblindFile, sep="")
    
    sumDf <- sumCourtshipDir2(csvDir=csvDir, out=out, listCatg=listCatg, listTL=listTL, na.zero=na.zero)
    sumDf <- transform(sumDf, filename = barename(filename))
    unblind <- read.csv(file=unblindCsv, stringsAsFactors=F)
    unblind <- transform(unblind, filename = barename(filename))
    
    print("Adding experimental group info (Unblinding)...")
    unblind_data <- merge(sumDf, unblind, by='filename')
    if ('total_time' %in% colnames(unblind_data) )
    {
        unblind_data <- transform(unblind_data, total_time = as.integer(total_time))
    }
    
    print("...added.")
    
    if (out)
    {
        outfile <- paste(csvDir, "/unblindedsummary.csv", sep="")
        write.csv(unblind_data, file=outfile, row.names=FALSE)
        print(paste("Written results to file", outfile))
    }
    
    return(unblind_data)
}
###### end non-cumulative time_percent #####
