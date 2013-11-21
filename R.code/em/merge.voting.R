
idCols <- c('type', 'parentId', 'nodeDegree', 'layer', 'x', 'y')

duplicatedVote <- function(voteDf)
{
    checkDf <- voteDf[, idCols]
    dupRow <- duplicated(checkDf) | duplicated(checkDf, fromLast=T)

    return(dupRow)
}

voteFiles <- data.frame("voter"=c('zjj','zby','wsx','wgx'), "filename"=c('zjj.20131115.vote.csv','zby.20131110.vote.csv','wsx.20131110.vote.csv','wgx.20131110.vote.csv'), stringsAsFactors=F)

nVoteFiles <- nrow(voteFiles)

vlog <- data.frame(voter=rep("", nVoteFiles), n_all_tags=rep(NA, nVoteFiles), n_vote_tags=rep(NA, nVoteFiles), n_votable=rep(NA, nVoteFiles), n_duplicates=rep(NA, nVoteFiles),stringsAsFactors=F)

voteDfList <- list()
dupVoteList <- list()

for (iVoteFile in 1:nVoteFiles)
{
    voter <- voteFiles[iVoteFile,'voter']
    v <- read.csv(voteFiles[iVoteFile,'filename'], header=T, stringsAsFactors=F)
    vlog[iVoteFile, 'voter'] <- voter
    vlog[iVoteFile, 'n_all_tags'] <- nrow(v)
    vlog[iVoteFile, 'n_votable'] <- sum(with(v, grepl("E[CT]-", tag)))

    v <- v[with(v, grepl("VOTE-", tag)),]
    vlog[iVoteFile, 'n_vote_tags'] <- nrow(v)
    vlog[iVoteFile, 'n_duplicates'] <- sum(duplicatedVote(v))
    dupVoteList[[iVoteFile]] <- duplicatedVote(v)

    colnames(v)[colnames(v)=='tag'] <- paste0(voter,'_tag')

    voteDfList[[iVoteFile]] <- v
}

# vzjj <- read.csv('zjj.20131115.vote.csv', header=T, stringsAsFactors=F)
# vlog[1, 'voter'] <- 'zjj'
# vlog[1, 'n_all_tags'] <- nrow(vzjj)
# vlog[1, 'n_votable'] <- sum(with(vzjj, grepl("E[CT]-", tag)))
# vzjj <- vzjj[with(vzjj, grepl("VOTE", tag)),]
# vlog[1, 'n_vote_tags'] <- nrow(vzjj)
# colnames(vzjj)[6] <- 'zjj_tag'

# check consistency manually
vlog

# check duplicates manually

# acquire votable
vall <- read.csv('zby.20131110.mergea.csv', header=T, stringsAsFactors=F)
vall <- vall[with(vall, grepl("E[CT]-", tag)),]

voteDfList[[length(voteDfList)+1]] <- vall

vm <- Reduce(function(...) merge(..., all=T), voteDfList)

write.csv(vm, 'merged.vote.csv', row.names=F)
