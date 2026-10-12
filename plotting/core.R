# Configurable, data-driven figures; this module does not refit statistical models.
library(grid)
plot_options <- function(cfg=list()) {
  defaults<-list(title='Scientific analysis',xlab='Effect estimate',font='sans',font_size=10,width=9,height=NULL,dpi=600,primary='#426D7A',secondary='#A67550',show_CI=TRUE,show_PI=TRUE,show_I2=TRUE,legend=TRUE,legend_labels=list(CI='CI: solid line',PI='PI: dashed line'),formats=c('pdf','svg','png'))
  modifyList(defaults,cfg)
}
save_plot <- function(stem,draw,cfg=list(),height=6) {
  o<-plot_options(cfg);if(is.null(o$height))o$height<-height
  if(o$width<4||o$height<3||o$dpi<72||o$font_size<6)stop('Invalid dimensions, font size or DPI')
  dir.create(dirname(stem),recursive=TRUE,showWarnings=FALSE)
  if(any(!o$formats%in%c('pdf','svg','png')))stop('Formats must be pdf, svg, png')
  for(fmt in o$formats){
    path<-paste0(stem,'.',fmt)
    switch(fmt,pdf=grDevices::cairo_pdf(path,width=o$width,height=o$height,family=o$font,onefile=FALSE),svg=grDevices::svg(path,width=o$width,height=o$height,family=o$font,onefile=FALSE),png=grDevices::png(path,width=o$width,height=o$height,units='in',res=o$dpi,type='cairo',bg='white'))
    tryCatch(draw(o),finally=dev.off())
  }
}
ptxt<-function(s,x,y,o,size=o$font_size,bold=FALSE,col='#25343B',just='left')grid.text(s,x=x,y=y,just=just,gp=gpar(fontfamily=o$font,fontsize=size,fontface=if(bold)'bold'else'plain',col=col))
pline<-function(x,y,col='#8F9DA5',lwd=1,lty=1)grid.lines(x=x,y=y,gp=gpar(col=col,lwd=lwd,lty=lty))
fmt_num<-function(v)ifelse(is.finite(v),formatC(v,format='f',digits=3),'NA')
interval_string<-function(lo,hi)ifelse(is.finite(lo)&is.finite(hi),paste0('[',fmt_num(lo),', ',fmt_num(hi),']'),'not estimable')
plot_title<-function(o)ptxt(paste(strwrap(o$title,width=75),collapse='\n'),.035,.958,o,size=o$font_size+3,bold=TRUE)
valid_intervals<-function(z){
  for(n in c('estimate','ci_low','ci_high'))if(!n%in%names(z)||!is.numeric(z[[n]]))stop('Required numeric columns: estimate, ci_low, ci_high')
  if(!nrow(z)||any(!is.finite(z$estimate))||any(xor(is.na(z$ci_low),is.na(z$ci_high)))||any(z$ci_low>z$ci_high,na.rm=TRUE))stop('Invalid confidence intervals')
  if(any(!is.finite(z$ci_low)&!is.na(z$ci_low))||any(!is.finite(z$ci_high)&!is.na(z$ci_high)))stop('Infinite interval endpoints are invalid')
  if(all(c('pi_low','pi_high')%in%names(z))&&(any(xor(is.na(z$pi_low),is.na(z$pi_high)))||any(z$pi_low>z$pi_high,na.rm=TRUE)||any(!is.finite(z$pi_low)&!is.na(z$pi_low))||any(!is.finite(z$pi_high)&!is.na(z$pi_high))))stop('Invalid prediction intervals')
  if(any(z$estimate<z$ci_low|z$estimate>z$ci_high,na.rm=TRUE))stop('Estimate outside confidence interval')
}
interval_plot <- function(z,stem,cfg=list(),pooled=NULL) {
  valid_intervals(z);if(!'label'%in%names(z))z$label<-as.character(seq_len(nrow(z)))
  rows<-nrow(z)+if(is.null(pooled))0 else 2
  draw<-function(o){
    grid.newpage();plot_title(o)
    values<-c(z$estimate,if(o$show_CI)c(z$ci_low,z$ci_high),if(o$show_PI)c(z$pi_low,z$pi_high))
    if(!is.null(pooled))values<-c(values,pooled$estimate,unlist(pooled$CI),if(o$show_PI)unlist(pooled$PI))
    bounds<-range(c(0,values),finite=TRUE);if(diff(bounds)==0)bounds<-bounds+c(-1,1);pad<-.08*diff(bounds);bounds<-bounds+c(-pad,pad)
    xx<-function(x).38+(x-bounds[1])/diff(bounds)*.32
    yy<-function(i).82-(i-1)*(.61/max(1,rows-1))
    ptxt('Comparison',.035,.88,o,bold=TRUE);ptxt('Estimate / interval',.73,.88,o,bold=TRUE)
    pline(rep(xx(0),2),c(.19,.85),col='#BFC6CB',lty=2)
    for(i in seq_len(nrow(z))){
      y<-yy(i);label<-paste(strwrap(z$label[i],width=37),collapse='\n');ptxt(label,.035,y,o,size=o$font_size-1)
      if(o$show_PI&&all(c('pi_low','pi_high')%in%names(z))&&all(is.finite(c(z$pi_low[i],z$pi_high[i]))))pline(xx(c(z$pi_low[i],z$pi_high[i])),rep(y,2),col=o$secondary,lwd=1.3,lty=2)
      if(o$show_CI&&all(is.finite(c(z$ci_low[i],z$ci_high[i]))))pline(xx(c(z$ci_low[i],z$ci_high[i])),rep(y,2),col=o$primary,lwd=1.5)
      grid.points(unit(xx(z$estimate[i]),'npc'),unit(y,'npc'),pch=15,size=unit(2,'mm'),gp=gpar(col=o$primary))
      text<-fmt_num(z$estimate[i]);if(o$show_CI)text<-paste(text,interval_string(z$ci_low[i],z$ci_high[i]));ptxt(text,.73,y,o,size=o$font_size-1)
    }
    if(!is.null(pooled)){
      y<-yy(nrow(z)+1);ptxt(if(pooled$k==1)'Single effect (not pooled)'else'Pooled estimate',.035,y,o,bold=TRUE)
      ci<-unlist(pooled$CI);if(o$show_CI&&all(is.finite(ci)))grid.polygon(x=xx(c(ci[1],pooled$estimate,ci[2],pooled$estimate)),y=c(y,y+.01,y,y-.01),gp=gpar(fill=o$primary,col=o$primary))else grid.points(unit(xx(pooled$estimate),'npc'),unit(y,'npc'),pch=18,gp=gpar(col=o$primary))
      ptxt(paste(fmt_num(pooled$estimate),if(o$show_CI)interval_string(ci[1],ci[2])else''),.73,y,o,size=o$font_size-1,bold=TRUE)
      pi<-unlist(pooled$PI);if(o$show_PI&&length(pi)==2&&all(is.finite(pi))){y<-yy(nrow(z)+2);ptxt('Prediction interval',.035,y,o);pline(xx(pi),rep(y,2),col=o$secondary,lty=2);ptxt(interval_string(pi[1],pi[2]),.73,y,o,size=o$font_size-1)}
      stat<-paste0('k=',pooled$k,'; method=',pooled$method);if(o$show_I2&&is.finite(pooled$I2))stat<-paste0(stat,'; I2=',formatC(pooled$I2,digits=1,format='f'),'%');ptxt(stat,.035,.03,o,size=o$font_size-1)
    }
    ticks<-pretty(bounds,4);ticks<-ticks[ticks>=bounds[1]&ticks<=bounds[2]];pline(c(.38,.70),c(.13,.13))
    for(t in ticks){pline(rep(xx(t),2),c(.13,.12));ptxt(format(t,trim=TRUE),xx(t),.10,o,size=o$font_size-1,just='centre')}
    ptxt(o$xlab,.54,.066,o,just='centre')
    legends<-c(if(o$show_CI)o$legend_labels$CI,if(o$show_PI)o$legend_labels$PI)
    if(o$legend&&length(legends))ptxt(paste(legends,collapse='; '),.73,.05,o,size=o$font_size-2)
  }
  save_plot(stem,draw,cfg,height=max(5,3+rows*.32))
}
validate_rob<-function(z){
  if(!all(c('study','domain','judgment')%in%names(z))||!nrow(z))stop('RoB input requires study, domain, judgment')
  if(anyNA(z[c('study','domain','judgment')])||anyDuplicated(paste(z$study,z$domain,sep='|')))stop('Missing/duplicate RoB records')
  if(any(!z$judgment%in%c('LOW','UNCLEAR','HIGH','NR')))stop('RoB judgments: LOW, UNCLEAR, HIGH, NR');z
}
rob_plot <- function(z,stem,cfg=list(),matrix=FALSE) {
  z<-validate_rob(z);domains<-unique(z$domain);studies<-unique(z$study)
  draw<-function(o){
    grid.newpage();plot_title(o);colors<-if(is.null(o$rob_colors))c(LOW=o$primary,UNCLEAR='#C9BA92',HIGH=o$secondary,NR='#E8ECEF')else unlist(o$rob_colors)
    if(!all(c('LOW','UNCLEAR','HIGH','NR')%in%names(colors)))stop('rob_colors requires all four categories')
    if(matrix){
      cw<-.68/length(domains);rh<-.64/length(studies)
      for(j in seq_along(domains))ptxt(paste(strwrap(domains[j],width=15),collapse='\n'),.29+(j-.5)*cw,.84,o,size=o$font_size-1,just='centre')
      for(i in seq_along(studies)){
        y<-.76-(i-.5)*rh;ptxt(studies[i],.035,y,o,size=o$font_size-1)
        for(j in seq_along(domains)){
          found<-z$judgment[z$study==studies[i]&z$domain==domains[j]];if(!length(found))found<-'NR'
          grid.rect(x=.29+(j-.5)*cw,y=y,width=cw*.95,height=rh*.92,gp=gpar(fill=colors[found],col='white'));ptxt(switch(found,LOW='L',UNCLEAR='?',HIGH='H',NR='.'),.29+(j-.5)*cw,y,o,just='centre',size=o$font_size-1)
        }
      }
    }else{
      for(i in seq_along(domains)){
        y<-.77-(i-1)*(.60/max(1,length(domains)-1));ptxt(paste(strwrap(domains[i],width=29),collapse='\n'),.035,y,o,size=o$font_size-1)
        counts<-table(factor(z$judgment[z$domain==domains[i]],levels=names(colors)));start<-.34
        for(n in names(colors)){w<-.60*counts[n]/sum(counts);if(w>0){grid.rect(x=start+w/2,y=y,width=w,height=.055,gp=gpar(fill=colors[n],col='white'));ptxt(as.character(counts[n]),start+w/2,y,o,just='centre',size=o$font_size-1);start<-start+w}}
      }
      ptxt('Counts shown; bar widths are percentages of reported assessments',.035,.085,o,size=o$font_size-2)
    }
    if(o$legend)for(i in seq_along(colors)){x<-.13+(i-1)*.23;grid.rect(x=x,y=.045,width=.018,height=.018,gp=gpar(fill=colors[i],col=NA));ptxt(if(is.null(o$legend_labels[[names(colors)[i]]]))names(colors)[i]else o$legend_labels[[names(colors)[i]]],x+.018,.045,o,size=o$font_size-1)}
  }
  save_plot(stem,draw,cfg,height=max(5,3+if(matrix)length(studies)*.24 else length(domains)*.4))
}
evidence_plot <- function(z,stem,cfg=list()) {
  if(!'id'%in%names(z)||ncol(z)<2||!nrow(z)||anyDuplicated(z$id)||anyNA(z))stop('Evidence input requires unique id and complete explicitly coded cells')
  codes<-c('UP','DOWN','NO_CHANGE','QUALITATIVE_UP','QUALITATIVE_DOWN','NR')
  if(any(!unlist(z[-1])%in%codes))stop('Unsupported evidence code')
  draw<-function(o){
    grid.newpage();plot_title(o);colors<-c(UP=o$primary,DOWN=o$secondary,NO_CHANGE='#C9BA92',QUALITATIVE_UP='#E7F0F2',QUALITATIVE_DOWN='#F3EAE3',NR='#EDF0F2');cw<-.71/(ncol(z)-1);rh<-.61/nrow(z)
    for(j in seq_len(ncol(z)-1))ptxt(paste(strwrap(names(z)[j+1],width=12),collapse='\n'),.26+(j-.5)*cw,.82,o,size=o$font_size-1,just='centre')
    for(i in seq_len(nrow(z))){y<-.75-(i-.5)*rh;ptxt(z$id[i],.035,y,o,size=o$font_size-1)
      for(j in seq_len(ncol(z)-1)){code<-z[i,j+1];grid.rect(x=.26+(j-.5)*cw,y=y,width=cw*.95,height=rh*.92,gp=gpar(fill=colors[code],col='white'));label<-switch(code,UP='+',DOWN='-',NO_CHANGE='0',QUALITATIVE_UP='Q+',QUALITATIVE_DOWN='Q-',NR='.');ptxt(label,.26+(j-.5)*cw,y,o,just='centre')}
    }
    if(o$legend)ptxt(if(is.null(o$legend_labels$evidence))'+: higher; -: lower; 0: no clear change; Q: qualitative; .: not reported'else o$legend_labels$evidence,.035,.07,o,size=o$font_size-2)
    ptxt('Directions are user-supplied observations; no causal interpretation is inferred.',.035,.035,o,size=o$font_size-2)
  };save_plot(stem,draw,cfg,height=max(5,3+nrow(z)*.3))
}
prisma_plot <- function(c,stem,cfg=list()) {
  fields<-c('identified','duplicates','screened','title_excluded','sought','not_retrieved','assessed','fulltext_excluded','included')
  if(!all(fields%in%names(c))||any(!is.finite(unlist(c[fields])))||any(unlist(c[fields])<0)||any(unlist(c[fields])!=floor(unlist(c[fields]))))stop('PRISMA counts must be supplied nonnegative integers')
  if(c$identified-c$duplicates!=c$screened||c$screened-c$title_excluded!=c$sought||c$sought-c$not_retrieved!=c$assessed||c$assessed-c$fulltext_excluded!=c$included)stop('Inconsistent study-selection arithmetic')
  draw<-function(o){
    grid.newpage();plot_title(o)
    box<-function(text,x,y,w=.40,h=.095){grid.roundrect(x=x,y=y,width=w,height=h,r=unit(.02,'npc'),gp=gpar(fill='#F1F5F7',col=o$primary));ptxt(text,x,y,o,size=o$font_size,just='centre')}
    ys<-c(.83,.68,.53,.38,.20);texts<-c(paste0('Records identified\n(n=',c$identified,')'),paste0('Records screened\n(n=',c$screened,')'),paste0('Reports sought\n(n=',c$sought,')'),paste0('Full-text reports assessed\n(n=',c$assessed,')'),paste0('Reports included\n(n=',c$included,')'))
    for(i in seq_along(ys)){box(texts[i],.27,ys[i]);if(i<length(ys))grid.lines(x=c(.27,.27),y=c(ys[i]-.05,ys[i+1]+.05),arrow=arrow(length=unit(2,'mm')),gp=gpar(col=o$primary))}
    exclusions<-c(paste0('Duplicates removed\n(n=',c$duplicates,')'),paste0('Title/abstract excluded\n(n=',c$title_excluded,')'),paste0('Not retrieved\n(n=',c$not_retrieved,')'),paste0('Full-text reports excluded\n(n=',c$fulltext_excluded,')'))
    for(i in 1:4){box(exclusions[i],.76,ys[i]);grid.lines(x=c(.48,.55),y=rep(ys[i],2),arrow=arrow(length=unit(2,'mm')),gp=gpar(col=o$primary))}
    if(o$legend)ptxt(if(is.null(o$legend_labels$prisma))'PRISMA-style figure; counts supplied by the user. Complete reporting remains the reviewer responsibility.'else o$legend_labels$prisma,.035,.065,o,size=o$font_size-2)
  };save_plot(stem,draw,cfg,height=8)
}
