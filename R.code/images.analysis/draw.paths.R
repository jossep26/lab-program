### Preparations ###
# install.packages('ggplot2', repos='http://mirror.bjtu.edu.cn/cran/')
######
library(ggplot2)

readPointsCsv <- function(file="")
{
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

    # check filename integrity
    basefnInput <- basename(file)
    if (grepl("^[.~]", basefnInput) | !grepl("[.]csv$", basefnInput))
    {
        print("Wrong filename. Filename should end with '.srt' and not start with '.' or '~'.")
        return(NULL)
    }

    df <- read.csv(file, header=TRUE, sep=",")

    if (ncol(df) != 2)
    {
        return(NULL)
    }

    return(df)
}

readPaths <- function(dir="")
{
    # initializing directory selection
    if (dir=="" | !file.exists(dir))
    {
        file <- choose.files(caption="Select Directory For Paths")
        if ( is.na(file) )
        {
            print("Directory selection has been canceled.")
            return(NULL)
        }

        dir <- dirname(file)
    }

    flist <- list.files(path=dir, pattern="*.csv", full.names=TRUE)
    if ( identical(flist, character(0)) ) 
    {
        print("No .srt file detected.")
        return(NULL)
    }
    nFile <- length(flist)
    
    plist <- list()
    nPaths <- 0
    for ( iFile in 1:nFile )
    {
        points <- readPointsCsv(flist[iFile])
        if (!is.null(points))
        {
            plist[[nPaths + 1]] <- points
            nPaths = nPaths + 1
        }
    }

    return(plist)
}

plotPaths <- function(paths)
{
    library(ggplot2)
    p <- ggplot()

    nPaths <- length(paths)
    for (iPath in 1:nPaths)
    {
        points <- paths[[iPath]]
        points[, 1] <- points[, 1] - points[1, 1]
        points[, 2] <- points[, 2] - points[1, 2]
        p <- p + geom_path(data=points, aes(x, -y), size=2, alpha=0.5)
    }

    return(p)
}

p <- plotPaths(readPaths())
p
