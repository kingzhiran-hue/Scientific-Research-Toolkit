if(.Platform$OS.type=='windows')invisible(Sys.setlocale('LC_CTYPE','English_United States.utf8'))
args<-commandArgs(trailingOnly=TRUE);filearg<-grep('^--file=',commandArgs(),value=TRUE)[1];root<-dirname(dirname(normalizePath(sub('^--file=','',filearg))))
source(file.path(root,'environment/bootstrap.R'))
source(file.path(root,'plotting/core.R'))
if(!requireNamespace('jsonlite',quietly=TRUE))stop('jsonlite is required')
if(length(args)%%2)stop('Use --name value pairs');opt<-setNames(as.list(args[seq(2,length(args),2)]),sub('^--','',args[seq(1,length(args),2)]))
if(is.null(opt$type)||is.null(opt$input)||is.null(opt$out))stop('Required: --type --input --out')
cfg<-if(is.null(opt$config))list()else jsonlite::fromJSON(opt$config)
if(opt$type=='prisma')prisma_plot(jsonlite::fromJSON(opt$input),opt$out,cfg)else{
 z<-read.csv(opt$input,stringsAsFactors=FALSE,check.names=FALSE,na.strings=c('','NA'))
 if(opt$type=='forest'){
  if(!all(c('id','yi','ci_low','ci_high')%in%names(z)))stop('Forest requires id, yi, ci_low, ci_high')
  z$estimate<-z$yi;z$label<-z$id;a<-if(is.null(opt$results))NULL else jsonlite::fromJSON(opt$results)$results$primary;interval_plot(z,opt$out,cfg,a)
 }else if(opt$type%in%c('sensitivity','loo','comparison')){
  if('analysis'%in%names(z))z$label<-z$analysis;interval_plot(z,opt$out,cfg)
 }else if(opt$type=='rob-summary')rob_plot(z,opt$out,cfg)else if(opt$type=='rob-matrix')rob_plot(z,opt$out,cfg,TRUE)else if(opt$type=='evidence')evidence_plot(z,opt$out,cfg)else stop('Unknown plot type')
}
cat('Plot completed:',opt$type,'\n')
