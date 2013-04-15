createCourtshipDf <- function(nRows)
{# tool function

    # createCourtshipDf will create an empty data frame for holding courtship summary
    df <- data.frame(filename = rep("", nRows), category = rep("", nRows), total_time = rep("", nRows), time_percent = rep(NA, nRows), occurence = rep(NA, nRows), stringsAsFactors=FALSE)
    
    return(df)
}

barename <- function(fn)
{# tool function

    # barename returns stripped filename without extension
    # strip all extensions, e.g. base.ext.ension --> base
    return(sub("[.].*$", "\\1", basename(fn), perl=T))

}

sumDfCourtshipByTL <- function(TL, textCatg, dfCourtship)
{
    #  sumDfCourtshipByTL will return summary about the given behavior category and occurence of _A_ given 'category' for _A_ given time length in a courtship data frame
    #  IMPORTANT: assumes start time(i.e. offset) = 0
    #  IMPORTANT: if event's end time > TL, the end time is set to TL

    # if category does not exist, all the summary should be NA
    ckCatg <- dfCourtship$text==textCatg
    if (sum(ckCatg, na.rm=TRUE)==0) 
    {
        sumDf <- data.frame(category = textCatg, total_time = TL, time_percent = NA, occurence = NA, stringsAsFactors=FALSE)
    }
    else
    {
    # if category do exist, calculate interval for the time length provided
    
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
        textCatgTime <- sum(courtshipTextCatg[, 'interval_miliSec'])/TL
        # calculate the occurence of this behavior category (namely the number of rows)
        textCatgOccurence <- length(courtshipTextCatg[, 'interval_miliSec'])
      
        # re-structure and return the summary
        sumDf <- data.frame(category = textCatg, total_time = TL, time_percent = textCatgTime, occurence = textCatgOccurence, stringsAsFactors=FALSE)
    }

    return(sumDf)
}

sumCourtshipFile <- function(file, listTL=as.integer(c(60000, 120000, 180000, 240000, 300000)), listCatg=c('wing_extension', 'orientation', 'courtship'), failOnStartTime=TRUE)
{
    # sumCourtshipSrt will analyze a .srt file for a summary of each provided category by each provided time length 
    # IMPORTANT: expects one and only one 'latency' event indicating true start(not video start)

    basefnInput <- basename(file)

    if(grepl("[.]srt$", basefnInput))
    {
        if(!exists("read.srt", mode="function"))
        {
            warning("Requires 'csv_from_srt.R'. Do source('full\\path\\to\\csv_from_srt.R')")
        }

        b<-read.srt(file=file)
    }
    else if(grepl("[.]csv$", basefnInput))
    {
        b<-read.csv(file=file, header=T)
    }
    else
    {
        print(".srt or .csv file only")
        return(NULL)
    }
    
    nTL <- length(listTL)
    nCatg <- length(listCatg)  
    # strip all extensions, e.g. base.ext.ension --> base
    fn <- barename(file)

   # get start time
    if (sum(b$text=='latency') == 1)
    {# exactly one "latency" event indicate true start of the experiment
        TS <- b[b$text=='latency', 'start_miliSec']
    } 
    else 
    {# otherwise assume start time = 0
        TS <- 0

        if(failOnStartTime)
            stop("Cannot find session start time: one and only one 'latency' event required\n\tUse first event instead by setting failOnStartTime=FALSE")
        else 
            warning("'latency' event not valid, true start was gussesd as 0")
    }
    
    # re-calibrate(offset) time using start time
    b$start_miliSec <- b$start_miliSec - TS
    b$end_miliSec <- b$end_miliSec - TS
    
    # initialize summary data frame use tool function
    dfCatg <- createCourtshipDf(nCatg*nTL)
    
    # iterate through each time lenght and each category, putting info. one by one
    for ( iCatg in 1:nCatg) 
        {
        for ( iTL in 1:nTL)
            {
                dfCatg[(iCatg-1)*nTL+iTL, 'filename'] <- fn
                
                tmpDfCatg <- sumDfCourtshipByTL(listTL[iTL], listCatg[iCatg], b)
                dfCatg[(iCatg-1)*nTL+iTL, 'category'] <- tmpDfCatg[, 'category']
                dfCatg[(iCatg-1)*nTL+iTL, 'total_time'] <- tmpDfCatg[, 'total_time']
                dfCatg[(iCatg-1)*nTL+iTL, 'time_percent'] <- tmpDfCatg[, 'time_percent']
                dfCatg[(iCatg-1)*nTL+iTL, 'occurence'] <- tmpDfCatg[, 'occurence']
                
                tmpDfCatg <- NULL
            }
        }
     
    return(dfCatg)
}

sumCourtshipSrt <- function(srtfile, listTL=as.integer(c(60000, 120000, 180000, 240000, 300000)), listCatg=c('wing_extension', 'orientation'), failOnStartTime=TRUE)
{
    # sumCourtshipSrt will analyze a .srt file for a summary of each provided category by each provided time length 
    # IMPORTANT: expects one and only one 'latency' event indicating true start(not video start)
    
    nTL <- length(listTL)
    nCatg <- length(listCatg)  
    # strip all extensions, e.g. base.ext.ension --> base
    fn <- barename(srtfile)

    if(!exists("read.srt", mode="function"))
    {
        warning("Requires 'csv_from_srt.R'. Do source('full\\path\\to\\csv_from_srt.R')")
    }
    b<-read.srt(file=srtfile)
    
    # get start time
    if (sum(b$text=='latency') == 1)
    {# exactly one "latency" event indicate true start of the experiment
        TS <- b[b$text=='latency', 'start_miliSec']
    } 
    else 
    {# otherwise assume start time = 0
        TS <- 0

        if(failOnStartTime)
            stop("Cannot find session start time: one and only one 'latency' event required\n\tUse first event instead by setting failOnStartTime=FALSE")
        else 
            warning("'latency' event not valid, true start was gussesd as 0")
    }
    
    # re-calibrate(offset) time using start time
    b$start_miliSec <- b$start_miliSec - TS
    b$end_miliSec <- b$end_miliSec - TS
    
    # initialize summary data frame use tool function
    # dfCatg <- data.frame(filename = rep(fn, nCatg*nTL), category = rep("", nCatg*nTL), total_time = rep("", nCatg*nTL), time_percent = rep(NA, nCatg*nTL), occurence = rep(NA, nCatg*nTL), stringsAsFactors=FALSE)
    dfCatg <- createCourtshipDf(nCatg*nTL)
    
    # iterate through each time lenght and each category, putting info. one by one
    for ( iCatg in 1:nCatg) 
        {
        for ( iTL in 1:nTL)
            {
                dfCatg[(iCatg-1)*nTL+iTL, 'filename'] <- fn
                
                tmpDfCatg <- sumDfCourtshipByTL(listTL[iTL], listCatg[iCatg], b)
                dfCatg[(iCatg-1)*nTL+iTL, 'category'] <- tmpDfCatg[, 'category']
                dfCatg[(iCatg-1)*nTL+iTL, 'total_time'] <- tmpDfCatg[, 'total_time']
                dfCatg[(iCatg-1)*nTL+iTL, 'time_percent'] <- tmpDfCatg[, 'time_percent']
                dfCatg[(iCatg-1)*nTL+iTL, 'occurence'] <- tmpDfCatg[, 'occurence']
                
                tmpDfCatg <- NULL
            }
        }
     
    return(dfCatg)
}

sumCourtshipCsv <- function(csvfile, listTL=as.integer(c(60000, 120000, 180000, 240000, 300000)), listCatg=c('wing_extension', 'orientation'), failOnStartTime=TRUE)
{
    # sumCourtshipCsv will analyze a .srt.csv file for a summary of each provided category by each provided time length 
    # IMPORTANT: expects one and only one 'latency' event indicating true start(not video start)
    
    nTL <- length(listTL)
    nCatg <- length(listCatg)  
    # strip all extensions, e.g. base.ext.ension --> base
    fn <- barename(csvfile)
    
    b<-read.csv(file=csvfile, header=T)
    
    # get start time
    if (sum(b$text=='latency') == 1)
    {# exactly one "latency" event indicate true start of the experiment
        TS <- b[b$text=='latency', 'start_miliSec']
    } 
    else 
    {# otherwise assume start time = 0
        TS <- 0

        if(failOnStartTime)
            stop("Cannot find session start time: one and only one 'latency' event required\n\tUse first event instead by setting failOnStartTime=FALSE")
        else 
            warning("'latency' event not valid, true start was gussesd as 0")
    }
    
    # re-calibrate(offset) time using start time
    b$start_miliSec <- b$start_miliSec - TS
    b$end_miliSec <- b$end_miliSec - TS
    
    # initialize summary data frame use tool function
    # dfCatg <- data.frame(filename = rep(fn, nCatg*nTL), category = rep("", nCatg*nTL), total_time = rep("", nCatg*nTL), time_percent = rep(NA, nCatg*nTL), occurence = rep(NA, nCatg*nTL), stringsAsFactors=FALSE)
    dfCatg <- createCourtshipDf(nCatg*nTL)
    
    # iterate through each time lenght and each category, putting info. one by one
    for ( iCatg in 1:nCatg) 
        {
        for ( iTL in 1:nTL)
            {
                dfCatg[(iCatg-1)*nTL+iTL, 'filename'] <- fn
                
                tmpDfCatg <- sumDfCourtshipByTL(listTL[iTL], listCatg[iCatg], b)
                dfCatg[(iCatg-1)*nTL+iTL, 'category'] <- tmpDfCatg[, 'category']
                dfCatg[(iCatg-1)*nTL+iTL, 'total_time'] <- tmpDfCatg[, 'total_time']
                dfCatg[(iCatg-1)*nTL+iTL, 'time_percent'] <- tmpDfCatg[, 'time_percent']
                dfCatg[(iCatg-1)*nTL+iTL, 'occurence'] <- tmpDfCatg[, 'occurence']
                
                tmpDfCatg <- NULL
            }
        }
     
    return(dfCatg)
}

sumCourtshipDir <- function(dir="", csvDir="", out=TRUE, outfile="", listTL=as.integer(c(60000, 120000, 180000, 240000, 300000)), listCatg=c('wing_extension', 'orientation'), na.zero=FALSE, failOnStartTime=TRUE)
{
    # sumCourtshipDir will calculate and return a summary of analysed srt files (the csvs)
    # it also output csv summary files
    
    # compatibility
    if (dir=="")
    {
        dir = csvDir
    }

    # initializing directory selection
    if (dir=="")
    {
        dir <- choose.dir()
        if ( is.na(dir) ) 
        {
            print("Directory selection has been canceled.")
            return(NULL)
        }
    }

    # reading file list
    listFile <- list.files(path=dir, pattern="*.srt.csv", full.names=TRUE)
    if ( identical(listFile, character(0)) ) 
    {
        listFile <- list.files(path=dir, pattern="*.srt", full.names=TRUE)
        if ( identical(listFile, character(0)) ) 
        {
            warning("No .srt.csv or .srt files detected.")
        }
    }

    nFile <- length(listFile)

    # preparing Time Length list (a vector of time points) and Category list (a vector of behaviorial tags)
    nTL= length(listTL)
    nCatg=length(listCatg)
    
    # initialize and prepare the output data frame
    sumCsv <- createCourtshipDf(nFile*nTL*nCatg)
    
    # iterate through each csv file, calculating each summary, then inject them to blocks of previously prepared data frame
    for ( iFile in 1:nFile )
    {
        print(paste("Begin processing", listFile[iFile], "..."))
        
        sumCsv[((iFile-1)*nTL*nCatg+1):(iFile*nTL*nCatg), ] <- sumCourtshipFile(listFile[iFile], listTL, listCatg, failOnStartTime=failOnStartTime)
        
        print("...done.")
    }
    
    # Copy a NA=0 version
    sumCsvNoNA <- sumCsv
    sumCsvNoNA[is.na(sumCsvNoNA$time_percent), 'time_percent'] <- 0L
    sumCsvNoNA[is.na(sumCsvNoNA$occurence), 'occurence'] <- 0L
    
    # save to files
    if (out)
    {    
        if (outfile=="")
        {
            outfile <- paste(dir, "/summary.csv", sep="")
        }
    
        outfileNoNA <- paste(dir, "/summary_naIsZero.csv", sep="")
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
    # exp_group  total_time  mean_time_percent  sem_time_percent  mean_occurence sem_occurence
    nRow <- nGroup*nTL
    sumDf <- data.frame(exp_group=rep("",nRow), total_time=rep("",nRow), mean_time_percent=rep(NA, nRow), sem_time_percent=rep(NA,nRow), mean_occurence=rep(NA,nRow), sem_occurence=rep(NA, nRow), stringsAsFactors=FALSE)
    
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
            
            tmpOccurence <- tmpDfSum$occurence
            sumDf[(iGroup-1)*nTL+iTL, 'mean_occurence'] <- mean(tmpOccurence)
            sumDf[(iGroup-1)*nTL+iTL, 'sem_occurence'] <- sd(tmpOccurence)/sqrt(sum(!is.na(tmpOccurence)))
            
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
    # category  total_time  mean_time_percent  sem_time_percent  mean_occurence sem_occurence
    nRow <- nCatg*nTL
    sumDf <- data.frame(category=rep("",nRow), total_time=rep("",nRow), mean_time_percent=rep(NA, nRow), sem_time_percent=rep(NA,nRow), mean_occurence=rep(NA,nRow), sem_occurence=rep(NA,nRow), stringsAsFactors=FALSE)
    
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
            
            tmpOccurence <- tmpDfSum$occurence
            sumDf[(iCatg-1)*nTL+iTL, 'mean_occurence'] <- mean(tmpOccurence)
            sumDf[(iCatg-1)*nTL+iTL, 'sem_occurence'] <- sd(tmpOccurence)/sqrt(sum(!is.na(tmpOccurence)))
            
            tmpDfSum <- NULL
            tmpTimePercent <- NULL
            tmpOccurence <- NULL
        }
    }
    
    return(sumDf)
}

readCourtshipLatency <- function(latencyText="latency", csvDir="", out=TRUE, outfile=paste(csvDir, "/", latencyText, ".csv", sep=""))
{
    # initializing directory selection
    if (csvDir=="")
    {
        csvDir <- choose.dir()
        if ( is.na(csvDir) )
        {
            print("Directory selection has been canceled.")
            return(NULL)
        }
        outfile <- paste(csvDir, "/", latencyText, ".csv", sep="")
    }
    
    # reading file list
    listCsv <- list.files(path=csvDir, pattern="*.srt.csv", full.names=TRUE)
    if ( identical(listCsv, character(0)) ) 
    {
        print("No .srt.csv file detected.")
        return(NULL)
    }
    nFile <- length(listCsv)
    
    # prepare output
    latencyDf <- data.frame(filename=rep("", nFile), latency=rep(NA, nFile), stringsAsFactors=FALSE)
    colnames(latencyDf)[2] <- latencyText
    
    
    for ( iFile in 1:nFile )
    {
        print(paste("Reading", listCsv[iFile], "..."))
        
        tmpDf <- read.csv(file=listCsv[iFile], header=TRUE)
        tmpDf <- tmpDf[tmpDf$text==latencyText, c('start_miliSec', 'end_miliSec')]
        
        latencyDf[iFile, 'filename'] <- barename(listCsv[iFile])
        
        if ( (!is.null(tmpDf))&(nrow(tmpDf)==as.integer(1)) )
        {
            latencyDf[iFile, latencyText] <- tmpDf[, 'end_miliSec'] - tmpDf[, 'start_miliSec']
        }
        
        print("...done.")
    }
    
    if (out)
    {
        write.csv(latencyDf, file=outfile, row.names=FALSE)
        print(paste("Written results to file", outfile))
    }
    
    return(latencyDf)
    
}

unblindCourtshipCsv <- function(summaryCsv="", unblindCsv="")
{# This will translate filename into experiment categories

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
#    unblind_data <- transform(unblind_data, total_time = as.character(total_time))
    
    return(unblind_data)
}

sumAndUnblindCourtshipDir <- function(csvDir="", unblindFile="", out=FALSE, listCatg=c('courtship'), listTL=as.integer(c(60000, 120000, 180000, 240000, 300000)), na.zero=TRUE)
{
    # sumAndUnblindCourtshipDir will summarize all the *.srt.csv files, and add exp_group etc. info into all the lines in summary(unblinding). 
    
    # initializing directory selection
    if (csvDir=="")
    {
        csvDir <- choose.dir(default=getwd(), caption="Select Directory of csv files")
        if ( is.na(csvDir) )
        {
            print("Directory selection has been canceled.")
            return(NULL)
        }
    }

    if (unblindFile=="")
    {
        unblindFile <- choose.files(default=paste(csvDir, "/unblind.csv", sep=""), caption="Select UNBLIND csv file")
        if ( identical(unblindFile, character(0)) ) 
        {
            print("File selection has been canceled.")
            return(NULL)
        }
    }
    
    # do summary analysis on all .srt.csv 
    sumDf <- sumCourtshipDir(csvDir=csvDir, out=out, listCatg=listCatg, listTL=listTL, na.zero=na.zero)

    # prepare 'unblind' data
    sumDf <- transform(sumDf, filename = barename(filename))
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
        outfile <- paste(csvDir, "/unblindedsummary.csv", sep="")
        write.csv(unblind_data, file=outfile, row.names=FALSE)
        print(paste("Written results to file", outfile))
    }
    
    return(unblind_data)
}

readAndUnblindCourtshipLatency <- function(csvDir="", unblindFile="", out=FALSE, latencyText="latency", no.na=FALSE, na.to=0L)
{
    # readAndUnblindCourtshipLatency will summarize all the *.srt.csv files, and add exp_group etc. info into all the lines in summary(unblinding). 
    
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
    
    latencyDf <- readCourtshipLatency(csvDir=csvDir, latencyText=latencyText, out=FALSE)
    latencyDf <- transform(latencyDf, filename = barename(filename))
    unblind <- read.csv(file=unblindCsv, stringsAsFactors=F)
    unblind <- transform(unblind, filename = barename(filename))

    print("Adding experimental group info (Unblinding)...")
    unblind_data <- merge(latencyDf, unblind, by='filename')
    
    print("...added.")
    
    if (no.na && is.numeric(na.to) && (length(na.to)==1) )
    {
        print("Converting NAs...")
        noNA <- unblind_data
        noNA[is.na(noNA[colnames(noNA)==latencyText]), latencyText] <- na.to
        print(paste("...all NAs are now converted to", na.to))
        
        if (!out)
        {
            return(noNA)
        }
        else
        {
            noNAfile <- paste(csvDir, "/unblinded", latencyText, "noNA.csv", sep="")
            write.csv(noNA, file=noNAfile, row.names=FALSE)
            print(paste("Written results to file", noNAfile))            
        }
        
    }
    else
    {
        if (out)
        {
            outfile <- paste(csvDir, "/unblinded", latencyText, ".csv", sep="")
            write.csv(unblind_data, file=outfile, row.names=FALSE)
            print(paste("Written results to file", outfile))
        }
    }
    
    return(unblind_data)
}

###### non-cumulative time_percent #####

sumCourtshipCsv2 <- function(csvfile, listTL=as.integer(c(60000, 120000, 180000, 240000, 300000)), listCatg=c('wing_extension', 'orientation'))
{
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
{
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

    # preparing Time Length list (a vector of time points) and Category list (a vector of behaviorial tags)
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
    sumCsvNoNA[is.na(sumCsvNoNA$occurence), 'occurence'] <- 0L
    
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
{
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
