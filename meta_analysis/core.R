# General independent, continuous-outcome meta-analysis. No study-specific inputs.
options(stringsAsFactors=FALSE)
required_columns <- function(z, fields) {
  missing <- setdiff(fields,names(z)); if(length(missing))stop(paste('Missing columns:',paste(missing,collapse=', ')))
}
finite_numeric <- function(x, label) {
  if(!is.numeric(x)||any(!is.finite(x)))stop(paste(label,'must contain finite numeric values'))
}
as_flag <- function(x) {
  v<-toupper(trimws(as.character(x))); if(any(is.na(x)|!v%in%c('TRUE','FALSE')))stop('Boolean fields require TRUE or FALSE')
  v=='TRUE'
}
validate_independence <- function(z) {
  if(!nrow(z))stop('No effects available')
  required_columns(z,c('id','independence_id','independent'))
  if(any(is.na(z$id)|!nzchar(trimws(z$id)))||anyDuplicated(z$id))stop('Effect ids must be unique and nonmissing')
  if(any(is.na(z$independence_id)|!nzchar(trimws(z$independence_id)))||anyDuplicated(z$independence_id))stop('Repeated or missing independent cohort ids; dependent effects need another model')
  if(!all(as_flag(z$independent)))stop('Correlated/nonindependent comparisons are not supported')
  if('shared_control'%in%names(z)&&any(as_flag(z$shared_control)))stop('Shared controls require explicit dependence handling; not supported')
  if('control_id'%in%names(z)){
    known<-z$control_id[!is.na(z$control_id)&nzchar(trimws(z$control_id))]
    if(anyDuplicated(known))stop('Control cohort reused; ordinary independent pooling is inappropriate')
  }
  if('construct'%in%names(z)&&length(unique(z$construct))!=1)stop('Mixed outcome constructs; specify separate analyses')
}
validate_units <- function(z,measure) {
  if(measure=='MD'){
    required_columns(z,'unit')
    if(any(is.na(z$unit)|toupper(trimws(z$unit))%in%c('','NR','UNCLEAR'))||length(unique(trimws(z$unit)))!=1)stop('MD requires one declared, compatible measurement unit; no automatic conversion')
  }
}
effect_sizes <- function(z,measure='MD',input_type='groups',g_correction='approx',g_variance='df') {
  if(!measure%in%c('MD','Hedges_g'))stop('Supported measures: MD, Hedges_g')
  validate_independence(z);validate_units(z,measure)
  if(input_type=='effects'){
    if('effect_measure'%in%names(z)&&any(z$effect_measure!=measure))stop('Input effect-measure labels conflict with requested measure')
    if(any(c('n_t','n_c')%in%names(z))){
      required_columns(z,c('n_t','n_c'));finite_numeric(z$n_t,'n_t');finite_numeric(z$n_c,'n_c')
      if(any(z$n_t<2|z$n_c<2|z$n_t!=floor(z$n_t)|z$n_c!=floor(z$n_c)))stop('Supplied group sample sizes must be integers >=2')
    }
    required_columns(z,'yi');finite_numeric(z$yi,'yi')
    if(!'vi'%in%names(z)){
      required_columns(z,'se');finite_numeric(z$se,'se');if(any(z$se<=0))stop('se must be positive');z$vi<-z$se^2
    }else if('se'%in%names(z)){
      finite_numeric(z$se,'se');if(any(z$se<=0)||any(abs(z$se^2-z$vi)>1e-8*pmax(1,abs(z$vi))))stop('SE and variance conflict')
    }
    finite_numeric(z$vi,'vi');if(any(z$vi<=0))stop('Sampling variances must be strictly positive')
    z$effect_measure<-measure;return(z)
  }
  if(input_type!='groups')stop('input_type must be groups or effects')
  required_columns(z,c('mean_t','mean_c','error_t','error_c','error_type_t','error_type_c','n_t','n_c'))
  for(n in c('mean_t','mean_c','error_t','error_c','n_t','n_c'))finite_numeric(z[[n]],n)
  if(any(z$n_t<2|z$n_c<2|z$n_t!=floor(z$n_t)|z$n_c!=floor(z$n_c)))stop('Group sample sizes must be integers >=2')
  if(any(z$error_t<0|z$error_c<0))stop('SD/SEM cannot be negative')
  if(any(!z$error_type_t%in%c('SD','SEM'))||any(!z$error_type_c%in%c('SD','SEM')))stop('Error type must be explicitly SD or SEM')
  z$sd_t<-ifelse(z$error_type_t=='SEM',z$error_t*sqrt(z$n_t),z$error_t)
  z$sd_c<-ifelse(z$error_type_c=='SEM',z$error_c*sqrt(z$n_c),z$error_c)
  if(measure=='MD'){
    z$yi<-z$mean_t-z$mean_c;z$vi<-z$sd_t^2/z$n_t+z$sd_c^2/z$n_c
  }else{
    df<-z$n_t+z$n_c-2;sp<-sqrt(((z$n_t-1)*z$sd_t^2+(z$n_c-1)*z$sd_c^2)/df)
    if(any(sp<=0))stop('Hedges g requires a positive pooled SD')
    J<-switch(g_correction,approx=1-3/(4*df-1),exact=exp(lgamma(df/2)-.5*log(df/2)-lgamma((df-1)/2)),stop('Unknown g correction'))
    z$yi<-J*(z$mean_t-z$mean_c)/sp
    denominator<-switch(g_variance,df=df,LS=z$n_t+z$n_c,stop('Unknown g variance option'))
    z$vi<-(z$n_t+z$n_c)/(z$n_t*z$n_c)+z$yi^2/(2*denominator)
    z$g_correction<-g_correction;z$g_variance<-g_variance
  }
  if(any(!is.finite(z$yi)|!is.finite(z$vi)|z$vi<=0))stop('Nonpositive/nonfinite effect variance')
  z$effect_measure<-measure;z
}
fit_meta <- function(z,method='REML',level=.95) {
  if(!method%in%c('REML','PM','DL'))stop('Supported tau2 estimators: REML, PM, DL')
  if(length(level)!=1||!is.finite(level)||level<=0||level>=1)stop('level must lie between 0 and 1')
  validate_independence(z);required_columns(z,c('yi','vi'));finite_numeric(z$yi,'yi');finite_numeric(z$vi,'vi')
  if(any(z$vi<=0))stop('Variances must be positive')
  if('effect_measure'%in%names(z)){
    if(length(unique(z$effect_measure))!=1)stop('Mixed effect measures');validate_units(z,unique(z$effect_measure))
  }
  y<-z$yi;v<-z$vi;k<-length(y);df<-k-1
  if(any(abs(y)>1e150|v>1e150|v<1e-150))stop('Input scale risks floating-point overflow/underflow; rescale and justify units before analysis')
  N<-if(all(c('n_t','n_c')%in%names(z))&&!anyNA(z[c('n_t','n_c')]))sum(z$n_t+z$n_c) else NA_real_
  if(k==1)return(list(k=1,N=N,estimate=y,CI=c(NA_real_,NA_real_),PI=c(NA_real_,NA_real_),HK_SE=NA_real_,HK_variance=NA_real_,tau2=NA_real_,Q=NA_real_,I2=NA_real_,p=NA_real_,df=NA_integer_,PI_df=NA_integer_,method=method,status='SINGLE_EFFECT_NO_POOLED_INFERENCE',weights=100,ids=z$id,level=level))
  wf<-1/v;mf<-sum(wf*y)/sum(wf);Q<-sum(wf*(y-mf)^2);cc<-sum(wf)-sum(wf^2)/sum(wf)
  score<-function(t){w<-1/(v+t);m<-sum(w*y)/sum(w);if(method=='REML')sum(w^2*(y-m)^2)-(sum(w)-sum(w^2)/sum(w))else sum(w*(y-m)^2)-df}
  if(method=='DL')tau<-max(0,(Q-df)/cc) else if(score(0)<=0)tau<-0 else{
    upper<-max(1,var(y)*10,max(v));i<-0
    while(score(upper)>0){upper<-upper*2;i<-i+1;if(i>100||!is.finite(upper))stop('Tau2 root not bracketed')}
    tau<-uniroot(score,c(0,upper),tol=1e-12)$root
  }
  w<-1/(v+tau);mu<-sum(w*y)/sum(w);q<-sum(w*(y-mu)^2)/df;vhk<-q/sum(w);se<-sqrt(vhk)
  alpha<-1-level;ci<-mu+c(-1,1)*qt(1-alpha/2,df)*se
  pi<-if(k>=3)mu+c(-1,1)*qt(1-alpha/2,k-2)*sqrt(tau+vhk)else c(NA_real_,NA_real_)
  p<-if(se==0)NA_real_ else 2*pt(-abs(mu/se),df)
  list(k=k,N=N,estimate=mu,HK_SE=se,HK_variance=vhk,HK_q=q,CI=ci,p=p,df=df,tau2=tau,Q=Q,Q_df=df,Q_p=pchisq(Q,df,lower.tail=FALSE),I2=if(Q==0)0 else max(0,1-df/Q)*100,PI=pi,PI_df=if(k>=3)k-2 else NA_integer_,PI_status=if(k>=3)'ESTIMABLE'else'NOT_ESTIMABLE_K_LT_3',method=method,status=if(se==0)'ZERO_RESIDUAL_HK_INFERENCE_DEGENERATE'else'OK',weights=w/sum(w)*100,ids=z$id,level=level,inference='unmodified_HKSJ',prediction='Riley_t_k_minus_2')
}
select_rows <- function(z,conditions) {
  keep<-rep(TRUE,nrow(z))
  for(c in conditions){
    field<-c$field;required_columns(z,field);x<-z[[field]]
    rule<-switch(c$operator,eq=x==c$value,ne=x!=c$value,`in`=x%in%unlist(c$value),lt=x<c$value,le=x<=c$value,gt=x>c$value,ge=x>=c$value,stop('Unsupported filter operator'))
    if(anyNA(rule))stop('Missing filter values; cannot silently drop records')
    keep<-keep&rule
  }
  z[keep,,drop=FALSE]
}
run_specifications <- function(z,method='REML',level=.95,config=list()) {
  out<-list(primary=fit_meta(z,method,level),PM=fit_meta(z,'PM',level),DL=fit_meta(z,'DL',level))
  loo<-list()
  if(nrow(z)>1)for(i in seq_len(nrow(z)))loo[[z$id[i]]]<-fit_meta(z[-i,,drop=FALSE],method,level)
  out$leave_one_out<-loo;custom<-list()
  for(spec in config$subsets){
    if(is.null(spec$name)||!nzchar(spec$name)||spec$name%in%names(custom))stop('Unique subset names required')
    subset<-select_rows(z,spec$where);if(isTRUE(spec$exclude))subset<-z[!z$id%in%subset$id,,drop=FALSE]
    custom[[spec$name]]<-if(!nrow(subset))list(k=0,status='EMPTY_SUBSET_NOT_ESTIMABLE')else fit_meta(subset,method,level)
  }
  out$custom<-custom;out
}
summary_row <- function(a,name) {
  get<-function(x,default=NA_real_)if(is.null(a[[x]]))default else a[[x]]
  ci<-get('CI',c(NA,NA));pi<-get('PI',c(NA,NA))
  data.frame(analysis=name,k=get('k'),N=get('N'),estimate=get('estimate'),HK_SE=get('HK_SE'),ci_low=ci[1],ci_high=ci[2],pi_low=pi[1],pi_high=pi[2],p=get('p'),tau2=get('tau2'),Q=get('Q'),I2=get('I2'),df=get('df'),PI_df=get('PI_df'),method=get('method','not_fitted'),status=get('status',''),check.names=FALSE)
}
