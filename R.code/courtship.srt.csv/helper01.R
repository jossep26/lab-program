# From
# http://wiki.stdout.org/rcookbook/Graphs/Plotting%20means%20and%20error%20bars%20(ggplot2)/#helper-functions

# The summarySE function is also defined on this page. If you only are working with between-subjects variables, that is the only function you will need in your code. If you have within-subjects variables and want to adjust the error bars so that inter-subject variability is removed as in Loftus and Masson (1994), then the other two functions, normDataWithin and summarySEwithin must also be added to your code; summarySEwithin will then be the function that you call.

## Summarizes data.
## Gives count, mean, standard deviation, standard error of the mean, and confidence interval (default 95%).
##   data: a data frame.
##   measurevar: the name of a column that contains the variable to be summariezed
##   groupvars: a vector containing names of columns that contain grouping variables
##   na.rm: a boolean that indicates whether to ignore NA's
##   conf.interval: the percent range of the confidence interval (default is 95%)
summarySE <- function(data=NULL, measurevar, groupvars=NULL, na.rm=FALSE,
                      conf.interval=.95, .drop=TRUE) {
    require(plyr)

    # New version of length which can handle NA's: if na.rm==T, don't count them
    length2 <- function (x, na.rm=FALSE) {
        if (na.rm) sum(!is.na(x))
        else       length(x)
    }

    # This is does the summary; it's not easy to understand...
    datac <- ddply(data, groupvars, .drop=.drop,
                   .fun= function(xx, col, na.rm) {
                           c( N    = length2(xx[,col], na.rm=na.rm),
                              mean = mean   (xx[,col], na.rm=na.rm),
                              sd   = sd     (xx[,col], na.rm=na.rm)
                              )
                          },
                    measurevar,
                    na.rm
             )

    # Rename the "mean" column    
    datac <- rename(datac, c("mean"=measurevar))

    datac$se <- datac$sd / sqrt(datac$N)  # Calculate standard error of the mean

    # Confidence interval multiplier for standard error
    # Calculate t-statistic for confidence interval: 
    # e.g., if conf.interval is .95, use .975 (above/below), and use df=N-1
    ciMult <- qt(conf.interval/2 + .5, datac$N-1)
    datac$ci <- datac$se * ciMult

    return(datac)
}

## Norms the data within specified groups in a data frame; it normalizes each
## subject (identified by idvar) so that they have the same mean, within each group
## specified by betweenvars.
##   data: a data frame.
##   idvar: the name of a column that identifies each subject (or matched subjects)
##   measurevar: the name of a column that contains the variable to be summariezed
##   betweenvars: a vector containing names of columns that are between-subjects variables
##   na.rm: a boolean that indicates whether to ignore NA's
normDataWithin <- function(data=NULL, idvar, measurevar, betweenvars=NULL,
                           na.rm=FALSE, .drop=TRUE) {
    require(plyr)

    # Measure var on left, idvar + between vars on right of formula.
    data.subjMean <- ddply(data, c(idvar, betweenvars), .drop=.drop,
                           .fun = function(xx, col, na.rm) {
                                      c(subjMean = mean(xx[,col], na.rm=na.rm))
                                  },
                           measurevar,
                           na.rm
                     )

    # Put the subject means with original data
    data <- merge(data, data.subjMean)

    # Get the normalized data in a new column
    measureNormedVar <- paste(measurevar, "Normed", sep="")
    data[,measureNormedVar] <- data[,measurevar] - data[,"subjMean"] +
                               mean(data[,measurevar], na.rm=na.rm)

    # Remove this subject mean column
    data$subjMean <- NULL

    return(data)
}

## Summarizes data, handling within-subjects variables by removing inter-subject variability.
## It will still work if there are no within-S variables.
## Gives count, mean, standard deviation, standard error of the mean, and confidence interval (default 95%).
## If there are within-subject variables, calculate adjusted values using method from Morey (2008).
##   data: a data frame.
##   measurevar: the name of a column that contains the variable to be summariezed
##   betweenvars: a vector containing names of columns that are between-subjects variables
##   withinvars: a vector containing names of columns that are within-subjects variables
##   idvar: the name of a column that identifies each subject (or matched subjects)
##   na.rm: a boolean that indicates whether to ignore NA's
##   conf.interval: the percent range of the confidence interval (default is 95%)
summarySEwithin <- function(data=NULL, measurevar, betweenvars=NULL, withinvars=NULL,
                            idvar=NULL, na.rm=FALSE, conf.interval=.95, .drop=TRUE) {

    # Ensure that the betweenvars and withinvars are factors
    factorvars <- sapply(data[, c(betweenvars, withinvars), drop=FALSE], FUN=is.factor)
    if (!all(factorvars)) {
        nonfactorvars <- names(factorvars)[!factorvars]
        message("Automatically converting the following non-factors to factors: ",
                paste(nonfactorvars, collapse = ", "))
        data[nonfactorvars] <- lapply(data[nonfactorvars], factor)
    }

    # Norm each subject's data    
    data <- normDataWithin(data, idvar, measurevar, betweenvars, na.rm, .drop=.drop)

    # This is the name of the new column
    measureNormedVar <- paste(measurevar, "Normed", sep="")

    # Replace the original data column with the normed one
    data[,measurevar] <- data[,measureNormedVar]

    # Collapse the normed data - now we can treat between and within vars the same
    datac <- summarySE(data, measurevar, groupvars=c(betweenvars, withinvars), na.rm=na.rm,
                       conf.interval=conf.interval, .drop=.drop)

    # Apply correction from Morey (2008) to the standard error and confidence interval
    #  Get the product of the number of conditions of within-S variables
    nWithinGroups    <- prod(sapply(datac[,withinvars, drop=FALSE], FUN=nlevels))
    correctionFactor <- sqrt( nWithinGroups / (nWithinGroups-1) )

    # Apply the correction factor
    datac$sd <- datac$sd * correctionFactor
    datac$se <- datac$se * correctionFactor
    datac$ci <- datac$ci * correctionFactor

    return(datac)
}


##
# multiplot function
# http://wiki.stdout.org/rcookbook/Graphs/Multiple%20graphs%20on%20one%20page%20(ggplot2)/
# This is the definition of multiplot. It can take any number of plot objects as arguments, or if it can take a list of plot objects passed to plotlist.

multiplot <- function(..., plotlist=NULL, cols) {
    require(grid)

    # Make a list from the ... arguments and plotlist
    plots <- c(list(...), plotlist)

    numPlots = length(plots)

    # Make the panel
    plotCols = cols                          # Number of columns of plots
    plotRows = ceiling(numPlots/plotCols) # Number of rows needed, calculated from # of cols

    # Set up the page
    grid.newpage()
    pushViewport(viewport(layout = grid.layout(plotRows, plotCols)))
    vplayout <- function(x, y)
        viewport(layout.pos.row = x, layout.pos.col = y)

    # Make each plot, in the correct location
    for (i in 1:numPlots) {
        curRow = ceiling(i/plotCols)
        curCol = (i-1) %% plotCols + 1
        print(plots[[i]], vp = vplayout(curRow, curCol ))
    }

}