##################
## 20130528

# bar plot
source('e:\\experiment\\lab-program\\R.code\\courtship.srt.csv\\summaryForCourtship.R')
source('e:\\experiment\\lab-program\\R.code\\courtship.srt.csv\\helper01.R')
source("e:\\experiment\\lab-program\\R.code\\courtship.srt.csv\\csv_from_srt.R")
source("e:\\experiment\\lab-program\\R.code\\courtship.srt.csv\\rnc_ggplot2_border_themes.r")
library(ggplot2)

# read in, analyze data
ua1 <- sumAndUnblindCourtshipDir(csvDir='.', unblindFile="./unblind.csv", listCatg=c('courtship'), listTL=as.integer(c(300000)), out=FALSE, na.zero=TRUE)

# Wilcoxon test
ctrl_1 <- ua1[ua1$exp_group=='control', 'time_percent']
exp_1 <- ua1[ua1$exp_group=='experimental', 'time_percent']

test_1 <- wilcox.test(ctrl_1, exp_1)
pv1 <- test_1$p.value

sink("test_wilcox.txt")
wilcox.test(ctrl_1, exp_1)
sink()

# prepare plotting data 
t1 <- summarySE(ua1, measurevar="time_percent", groupvars=c("exp_group","category","total_time"))

# select a subset of plotting data
sel <- c("control", "experimental")
t_sub <- t1[t1$exp_group %in% sel, ]
gptext <- c("Control", "Experiment")

# plot the bar plot
pd <- position_dodge(.1)
p1 <- ggplot(t_sub, aes(y=time_percent, x=exp_group)) +
      geom_errorbar(aes(ymin=time_percent-se, ymax=time_percent+se), position=pd, width=0.2) + 
      geom_bar(stat="identity", width=0.5) +
      scale_x_discrete("", labels=gptext) +
      scale_y_continuous("Courtship Index (5 min)", expand=c(0,0), limits=c(0,1)) +
      geom_text(aes(label=paste("n=", N,sep="")), color="white", vjust=1.2) +
      theme_bw() +
      theme(axis.title.x = element_blank(), 
            axis.text.x  = element_text(angle=0, hjust=0.5, vjust=0.5, size=20, color="black"),
            axis.title.y = element_text(angle=90, size=20, vjust=0.3),
            axis.text.y  = element_text(size=16),
            strip.text.x = element_text(size=20),
            panel.grid.major = element_blank(), 
            panel.grid.minor = element_blank(),
            panel.border = element_blank(),
            axis.line = element_line(color = 'black'))

p1


################
## 20130403 latency

## unblind contains 2 col of grouping data
## mod facet title text appearance

source("e:\\experiment\\courtship.srt.csv\\summaryForCourtship.R")
source("e:\\experiment\\courtship.srt.csv\\helper01.R")
library(ggplot2)

ul <- readAndUnblindCourtshipLatency(csvDir='.', unblindFile='unblind.csv', latencyText="latency",no.na=T,na.to=0L)

t3 <- summarySE(ul, measurevar="latency", groupvar=c("genotype","group"))

# for th-flp
sel <- c("cs_x_m1406",
        "cs_x_m1407",
        "th_gal4/+",
        "th_x_m1406", 
        "th_x_m1407")
 
t33 <- t3[t3$genotype %in% sel,]
t33$latency <- t33$latency/1000
t33$sd <- t33$sd/1000
t33$se <- t33$se/1000
t33$ci <- t33$se/1000
t33[t33$group=="c",'group'] <- "Ctrl"
t33[t33$group=="e",'group'] <- "Exp"


pd <- position_dodge(.1)
p3 <- ggplot(t33, aes(x=group, y=latency)) +
      facet_grid(. ~ genotype) +
      geom_errorbar(aes(ymin=latency-se, ymax=latency+se), position=pd, width=0.6) +
      geom_bar() +
      geom_text(aes(label=paste("n=", N,sep="")), color="white", vjust=1.2) +
      opts(axis.title.x = theme_blank(), 
           axis.text.x  = theme_text(angle=60, hjust=1, vjust=1, size=20),
           axis.title.y = theme_text(angle=90, size=20),
           axis.text.y  = theme_text(size=16),
           strip.text.x = theme_text(size=20))
    
p3

pdf("latency.pdf", width=15, height=6.2)
p3
dev.off()


# for TNT lines
sel2 <- c("uas_tnte/+;th_gal4/+",
        "uas_tntin/+;th_gal4/+",
        "uas_tntin/+",
        "uas_tnte/+", 
        "th_gal4/+")
 
t34 <- t3[t3$genotype %in% sel2,]
t34$latency <- t34$latency/1000
t34$sd <- t34$sd/1000
t34$se <- t34$se/1000
t34$ci <- t34$se/1000
t34[t34$group=="c",'group'] <- "Ctrl"
t34[t34$group=="e",'group'] <- "Exp"


pd <- position_dodge(.1)
p34 <- ggplot(t34, aes(x=group, y=latency)) +
      facet_grid(. ~ genotype) +
      geom_errorbar(aes(ymin=latency-se, ymax=latency+se), position=pd, width=0.6) +
      geom_bar() +
      geom_text(aes(label=paste("n=", N,sep="")), color="white", vjust=1.2) +
      opts(axis.title.x = theme_blank(), 
           axis.text.x  = theme_text(angle=60, hjust=1, vjust=1, size=20),
           axis.title.y = theme_text(angle=90, size=20),
           axis.text.y  = theme_text(size=16),
           strip.text.x = theme_text(size=20))
           
p34

pdf("latency2.pdf", width=15, height=6.2)
p34
dev.off()



################
## 2012 Mar
## Analysis of wing extension and courtship bout. 

## Wing extension. 
## 1. wing extension occurence
## 2. wing extension average duration.

# load all the tools
source("e:\\experiment\\courtship.srt.csv\\summaryForCourtship.R")
source("e:\\experiment\\courtship.srt.csv\\helper01.R")
library(ggplot2)

# use convenient method "sumAndUnblindCourtshiopDir"
# to get occurence and total duration
udfWingExtension <- sumAndUnblindCourtshipDir(csvDir='.', listCatg=c("wing extension"), listTL=as.integer(c(300000)), out=FALSE, na.zero=TRUE)

# re-caculate average_duration
udfWingExtension$average_duration_ms <- udfWingExtension$time_percent * udfWingExtension$total_time / udfWingExtension$occurence

# TODO: plot occurance and average duration
# t1 <- summarySE(ua1, measurevar="time_percent", groupvars=c("exp_group","category","total_time"))

# p1<-ggplot(t1, aes(y=time_percent, x=exp_group))
# pd <- position_dodge(.1)
# pp <- p1 + geom_errorbar(aes(ymin=time_percent-se, ymax=time_percent+se), position=pd) + geom_bar()
# pp + opts(axis.title.x = theme_text(face="bold", colour="#990000", size=20), axis.text.x  = theme_text(angle=90, hjust=1.2, size=6))

## Courtship bout

# load all tools
source("e:\\experiment\\courtship.srt.csv\\summaryForCourtship.R")
source("e:\\experiment\\courtship.srt.csv\\helper01.R")
library(ggplot2)

# use convenient method "sumAndUnblindCourtshiopDir"
# to get occurence and total duration in the first 5 min
udfBout <- sumAndUnblindCourtshipDir(csvDir='.', listCatg=c("courtship bout"), listTL=as.integer(c(300000)), out=FALSE, na.zero=TRUE)

# re-caculate average_duration
udfBout$average_duration_ms <- udfBout$time_percent * udfBout$total_time / udfBout$occurence

# TODO: plot 

################
### Convert .event file to .srt.csv

# load the tool
source("e:\\experiment\\courtship.srt.csv\\csv_from_event.R")

# current dir
csvFromEventBatch(indir=".")

# pick a dir
csvFromEventBatch()

###


################
# e:\WGX\data\2012-04-04~2012-04-19

source("e:\\experiment\\R.code\\summaryForCourtship.R")
source("e:\\experiment\\R.code\\helper01.R")
library(ggplot2)

ua1 <- sumAndUnblindCourtshipDir(csvDir='.', listCatg=c('courtship'), listTL=as.integer(c(300000)), out=FALSE, na.zero=TRUE)

t1 <- summarySE(ua1, measurevar="time_percent", groupvars=c("exp_group","category","total_time"))

p1<-ggplot(t1, aes(y=time_percent, x=exp_group))
pd <- position_dodge(.1)
pp <- p1 + geom_errorbar(aes(ymin=time_percent-se, ymax=time_percent+se), position=pd) + geom_bar()
pp + opts(axis.title.x = theme_text(face="bold", colour="#990000", size=20), axis.text.x  = theme_text(angle=90, hjust=1.2, size=6))

## 
source("e:\\experiment\\R.code\\summaryForCourtship.R")
source("e:\\experiment\\R.code\\helper01.R")
library(ggplot2)

ua <- sumAndUnblindCourtshipDir(csvDir='.', listCatg=c('courtship'), listTL=as.integer(c(60000, 120000, 180000, 240000, 300000)), out=FALSE, na.zero=TRUE)

t <- summarySE(ua, measurevar="time_percent", groupvars=c("exp_group","category","total_time"))

p<-ggplot(t, aes(x=total_time, y=time_percent, colour=exp_group))
pd <- position_dodge(.1)
p + geom_errorbar(aes(ymin=time_percent-se, ymax=time_percent+se), position=pd) +
   geom_line(position=pd) +
   geom_point(position=pd)

#####
## latency to copulation
source("e:\\experiment\\R.code\\summaryForCourtship.R")
source("e:\\experiment\\R.code\\helper01.R")
library(ggplot2)

ulc <- readAndUnblindCourtshipLatency(csvDir='.', latencyText="latency to copulation",no.na=T,na.to=300000L)

t2 <- summarySE(ulc, measurevar="latency to copulation", groupvar=c("exp_group"))
colnames(t2)[colnames(t2)=="latency to copulation"] <- "latency_to_copulation"

p2 <- ggplot(t2, aes(x=exp_group, y=latency_to_copulation))
pd <- position_dodge(.1)
pp2 <- p2 + geom_errorbar(aes(ymin=latency_to_copulation-se, ymax=latency_to_copulation+se), position=pd) + geom_bar()
pp2 + opts(axis.title.x = theme_text(face="bold", colour="#990000", size=20), axis.text.x  = theme_text(angle=90, hjust=1, size=10))

# latency
source("e:\\experiment\\R.code\\summaryForCourtship.R")
source("e:\\experiment\\R.code\\helper01.R")
library(ggplot2)

ul <- readAndUnblindCourtshipLatency(csvDir='.', latencyText="latency",no.na=T,na.to=0L)

t3 <- summarySE(ul, measurevar="latency", groupvar=c("exp_group"))

p3 <- ggplot(t3, aes(x=exp_group, y=latency))
pd <- position_dodge(.1)
pp3 <- p3 + geom_errorbar(aes(ymin=latency-se, ymax=latency+se), position=pd) + geom_bar()
pp3 + opts(axis.title.x = theme_text(face="bold", colour="#990000", size=20), axis.text.x  = theme_text(angle=90, hjust=1, size=10))

#####
# Non-cumulative
# smaller bins

source("e:/experiment/courtship.srt.csv/summaryForCourtship.R")
source("e:/experiment/courtship.srt.csv/helper01.R")
library(ggplot2)

binSizeMs <- 5000
nBin <- 20
l <- c((1:nBin)*binSizeMs)

ua0 <- sumAndUnblindCourtshipDir2(csvDir='./', listCatg=c('courtship'), listTL=l, out=FALSE, na.zero=TRUE)

t0 <- summarySE(ua0, measurevar="time_percent", groupvars=c("exp_group","category","total_time"))

# anova
# Tukey's Test
ua0c <- ua0
ua0c$exp_group <- as.factor(ua0$exp_group)

TukeyHSD(aov(time_percent~exp_group,data=ua0c[ua0c$total_time==l[3],]))

TukeyHSD(aov(time_percent~exp_group,data=ua0c[ua0c$total_time==l[2],]))

# plot
pd <- position_dodge(.1)
p0 <- ggplot(data=t0, aes(x=total_time, y=time_percent)) +
    facet_grid(. ~ exp_group) +
    geom_line(position=pd, size=1.15) +
    geom_errorbar(aes(ymin=time_percent-se, ymax=time_percent+se), position=pd, width=0.3*10000) +
    geom_point(position=pd, shape=21, colour="black", size=2.5) +
    scale_fill_manual(values=c("white","black")) +
#    scale_x_continuous(limits=c(0, 330000), breaks=c(60000,120000,180000,240000,300000), labels=c("1 min","2 min","3 min","4 min","5 min")) +
    scale_y_continuous("Non-Cumulative Courtship Index", limits=c(0,1)) +
    theme_bw() +
    opts(
        axis.title.x = theme_blank(),
        axis.title.y = theme_text(size=12, angle=90, vjust=0.3), 
        legend.title = theme_blank(),
        legend.key = theme_blank()
    )
# p0

pd <- position_dodge(.1)
p01 <- ggplot(data=t0, aes(x=total_time, y=time_percent, color=exp_group)) +
    geom_line(position=pd, size=1.15) +
    geom_errorbar(aes(ymin=time_percent-se, ymax=time_percent+se), position=pd, width=0.3*10000) +
    geom_point(position=pd, shape=21, size=2.5) +
#    scale_fill_manual(values=c("white","black")) +
#    scale_x_continuous(limits=c(0, 330000), breaks=c(60000,120000,180000,240000,300000), labels=c("1 min","2 min","3 min","4 min","5 min")) +
    scale_y_continuous("Non-Cumulative Courtship Index", limits=c(-0.05,1)) +
    theme_bw() +
    opts(
        axis.title.x = theme_blank(),
        axis.title.y = theme_text(size=12, angle=90, vjust=0.3), 
        legend.title = theme_blank(),
        legend.key = theme_blank()
    )
p01


