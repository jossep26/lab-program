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
        print("Wrong filename. Filename should end with '.csv' 
               and not start with '.' or '~'.")
        return(NULL)
    }

    df <- read.csv(file, header=TRUE, sep=",")

    if (grepl("d[.]swc", basefnInput) & (df[1, 2] < df[nrow(df), 2]))
    {
        # dorsal dendrites, Y direction: large -> small
        # invert path if Y coords is small -> large
        df <- df[nrow(df):1, ]
        # print("Dorsal")
    }

    if (grepl("v[.]swc", basefnInput) & (df[1, 1] > df[nrow(df), 1]))
    {
        # dorsal dendrites, X direction: small -> large
        # invert path if X coords is large -> small
        df <- df[nrow(df):1, ]
        # print("Ventral")
    }

    if (ncol(df) != 2)
    {
        return(NULL)
    }

    return(df)
}

readPaths <- function(dir="", class="")
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

    if (class == "d" | class == "D" | class == "dorsal")
    {
        flist <- flist[grepl("d[.]swc", flist)]
    } else if (class == "v" | class == "V" | class == "ventral") {
        flist <- flist[grepl("v[.]swc", flist)]
    }

    if ( identical(flist, character(0)) ) 
    {
        print("No .csv file detected.")
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
        p <- p + geom_path(data=points, aes(x, -y), color='red', size=2, alpha=0.5)
    }

    return(p)
}

plotPaths2 <- function(dir="")
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
        print("No .csv file detected.")
        return(NULL)
    }
    nFile <- length(flist)

    library(ggplot2)
    p <- ggplot()

    for ( iFile in 1:nFile )
    {
        bfn <- basename(flist[iFile])
        # print(grep("^(.*?)[.]", basename(fn), value=T))
        points <- readPointsCsv(flist[iFile])
        if (!is.null(points))
        {
            points[, 1] <- points[, 1] - points[1, 1]
            points[, 2] <- points[, 2] - points[1, 2]
            labelP <- points[nrow(points)%/%2, ]
            labelP$bfn <- basename(flist[iFile])
            # print(labelP)
            p <- p + geom_path(data=points, aes(x, -y), 
                               color='red', size=2, alpha=0.5)
                 # geom_text(data=labelP, aes(x=x, y=-y, label=bfn))

        }
    }

    return(p)
}

readPathsAsNormalizedDf <- function(dir="")
{   # This version reads all points into a big data frame, 
    # with relavant information
    # Output data frame is in the format of:
    #   x       y           i             neuron      type
    #  coordinates    index in paths    neuron id    d or v 

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
        print("No .csv file detected.")
        return(NULL)
    }

    nFile <- length(flist)
    library(stringr)

    df <- data.frame()
    for ( iFile in 1:nFile )
    {
        fn <- flist[iFile]
        # get info from file name
        neuronId <- str_extract(fn, "[0-9][0-9][0-9]")
        neuriteType <- str_extract(str_extract(fn, "[dv][.]swc"), "[dv]")
        points <- readPointsCsv(fn)
        if (!is.null(points))
        {
            points <- normalizePath(points)
            n <- nrow(points)
            row.names(points) <- c(1:n)
            points$i <- c(1:n)
            points$neuron <- neuronId
            points$type <- neuriteType
            df <- rbind(df, points)
        }
    }

    return(df)
}

meanPathsFromAll <- function(allPaths)
{   # Calculate mean paths for each type (d or v) of paths,
    # from a big data frame with all points

    library(plyr)
    meanp <- ddply(allPaths, c("i", "type"), summarise, 
                   x = mean(x),
                   y = mean(y),
                   n = length(i) )

    maxNPaths <- max(meanp$n)
    return(meanp[meanp$n==maxNPaths, c('x', 'y', 'i', 'type')])
}

plotPathsAll <- function(dir="")
{   # Plot paths using a big data frame with all points

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

    allPaths <- readPathsAsNormalizedDf(dir)
    neurons <- levels(as.factor(allPaths$neuron))
    nNeuron <- length(neurons)

    library(RColorBrewer)
    getPal <- colorRampPalette(brewer.pal(12, "Set3"))
    colors <- getPal(nNeuron)

    library(ggplot2)
    p <- ggplot()

    for (iNeuron in 1:nNeuron)
    {
        points <- allPaths[allPaths$neuron==neurons[iNeuron], ]
        dpoints <- points[points$type=='d', ]
        p <- p + geom_path(data=dpoints, aes(x, -y), 
                           color=colors[iNeuron], size=2, alpha=0.5)

        vpoints <- points[points$type=='v', ]
        p <- p + geom_path(data=vpoints, aes(x, -y), 
                           color=colors[iNeuron], size=2, alpha=0.5)

    }

    meanPaths <- meanPathsFromAll(allPaths)
    meanDp <- meanPaths[meanPaths$type=='d', ]
    meanVp <- meanPaths[meanPaths$type=='v', ]
    p <- p + geom_path(data=meanDp, aes(x, -y), color='red', size=3)
    p <- p + geom_path(data=meanVp, aes(x, -y), color='green', size=3)

    return(p)
}

calculateMeanPath <- function(paths)
{
    library(plyr)
    nPonits <- min(unlist(lapply(paths, nrow)))
    nPaths <- length(paths)
    bindPaths <- data.frame()
    for (i in 1:nPaths)
    {
        points <- paths[[i]][1:nPonits, ]
        points$i <- c(1:nPonits)
        row.names(points) <- c(1:nPonits)
        bindPaths <- rbind(bindPaths, points)
    }
    
    meanp <- ddply(bindPaths, c("i"), summarise, 
                   meanX = mean(x),
                   meanY = mean(y) )
    meanp <- meanp[, names(meanp)!="i"]
    return(meanp)
}

normalizePath <- function(points)
{
    points[, 1] <- points[, 1] - points[1, 1]
    points[, 2] <- points[, 2] - points[1, 2]
    return(points)
}

plotPathsDV <- function(dir="")
{   # Plot all paths using lists of paths

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

    dplist <- readPaths(dir=dir, class="d")
    vplist <- readPaths(dir=dir, class="v")
    if (length(dplist) != length(vplist))
    {
        warning("D & P neurite numbers do not match!")
    }

    meanDp <- calculateMeanPath(dplist)
    meanVp <- calculateMeanPath(vplist)

    meanDp <- normalizePath(meanDp)
    meanVp <- normalizePath(meanVp)

    library(RColorBrewer)
    getPal <- colorRampPalette(brewer.pal(12, "Set3"))
    pal <- getPal(length(dplist))

    library(ggplot2)
    p <- ggplot()

    nD <- length(dplist)
    for (iPath in 1:nD)
    {
        points <- dplist[[iPath]]
        points <- normalizePath(points)
        p <- p + geom_path(data=points, aes(x, -y), color=pal[iPath], size=2, alpha=0.2)
    }
    # p <- p + geom_path(data=meanDp, aes(meanX, -meanY), color='red', size=3)

    nV <- length(vplist)
    for (iPath in 1:nV)
    {
        points <- vplist[[iPath]]
        points[, 1] <- points[, 1] - points[1, 1]
        points[, 2] <- points[, 2] - points[1, 2]
        p <- p + geom_path(data=points, aes(x, -y), color=pal[iPath], size=2, alpha=0.2)
    }
    # p <- p + geom_path(data=meanVp, aes(meanX, -meanY), color='green', size=3)

    return(p)
}

selectDir <- function()
{
        file <- choose.files(caption="Select Directory For Paths")
        if ( is.na(file) )
        {
            print("Directory selection has been canceled.")
            return(NULL)
        }

        dir <- dirname(file)
        return(dir)
}

dir <- selectDir()
outfn <- file.path(dir, "out.pdf")
# p <- plotPaths(readPaths())
# print(p)

# p <- plotPathsDV(dir=dir)
p <- plotPathsAll(dir=dir)
print(p)

pdf(outfn, width=10, height=10)
print(p)
dev.off()
