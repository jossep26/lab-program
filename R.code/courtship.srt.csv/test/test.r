# include all the functions
source('../csv_from_event.R')
source('../csv_from_srt.R')
source('../summaryForCourtship.R')
source('../helper01.R')

###########################
## test read in files
a <- readCourtshipFile(file='20120322-CH5-03.srt')
b <- readCourtshipFile(file='20120322-CH6-03.srt')
aa <- readCourtshipFile(file='20120322-CH5-03.srt.csv')
bb <- readCourtshipFile(file='20120322-CH6-03.srt.csv')

# should all be 'TRUE'
a$text == aa$text
a$start_miliSec == aa$start_miliSec
a$end_miliSec == aa$end_miliSec

b$text == bb$text
b$start_miliSec == bb$start_miliSec
b$end_miliSec == bb$end_miliSec

#########################
## test summary of one file
sum_a <- sumCourtshipFile(file='20120322-CH5-03.srt', listTL=as.integer(c(60000, 300000)), listCatg=c('wing_extension', 'courtship'), failOnStartTime=TRUE)
sum_aa <- sumCourtshipFile(file='20120322-CH5-03.srt.csv', listTL=as.integer(c(60000, 300000)), listCatg=c('wing_extension', 'courtship'), failOnStartTime=TRUE)

########################
## test summary of a dir
sum_d_a <- sumCourtshipDir(dir='.', out=FALSE, listTL=as.integer(c(60000, 300000)), listCatg=c('courtship', 'orientation'))
