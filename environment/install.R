source('environment/bootstrap.R')
# Install exact validated CRAN versions. Only jsonlite is needed for normal execution.
repos<-'https://cloud.r-project.org'
versions<-c(jsonlite='2.0.0',metafor='5.0-1',metadat='1.6-0',numDeriv='2016.8-1.1',mathjaxr='2.0-0',pbapply='1.7-4',digest='0.6.39')
for(p in names(versions))if(!requireNamespace(p,quietly=TRUE)||packageDescription(p)$Version!=versions[[p]]){
  if(!requireNamespace('remotes',quietly=TRUE))install.packages('remotes',repos=repos)
  remotes::install_version(p,version=versions[[p]],repos=repos,upgrade='never')
  if(packageDescription(p)$Version!=versions[[p]])stop(paste('Version installation failed:',p))
}
cat('Dependency installation completed\n')
