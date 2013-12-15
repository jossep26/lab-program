minDistanceOnLayer <- function(nodeA, nodeB, layer)
{
# minDistanceOnLayer will calculate minimun distance for all the points on the same layer
# nodeA and nodeB must be data farmes with columns ("X", "Y", "Layer") present

    Ai <- nodeA[nodeA$Layer==layer,]
    Bi <- nodeB[nodeB$Layer==layer,]
    nA <- nrow(Ai)
    nB <- nrow(Bi)

    if (nA<1 | nB<1)
    {
        distance <- NA
    }
    else 
    {
        d <- c()
        for (ia in 1:nA)
        {
            curAi <- Ai[ia,]
            for (ib in 1:nB)
            {
                curBi <- Bi[ib,]
                d[1+length(d)] <- sqrt((curAi$X-curBi$X)^2 + (curAi$Y-curBi$Y)^2)
            }
        }
        distance <- min(d)
    }

    return(distance)
}
