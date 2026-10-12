source('environment/bootstrap.R')
cat(R.version.string,'\n')
for(p in c('jsonlite','metafor','Matrix','metadat','numDeriv','mathjaxr','pbapply','digest','nlme','lattice')){
 if(!requireNamespace(p,quietly=TRUE))stop(paste('Missing package:',p))
 cat(p,packageDescription(p)$Version,'\n')
}
