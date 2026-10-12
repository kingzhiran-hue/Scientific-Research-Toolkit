# Reload configured libraries after enabling UTF-8 path handling on Windows.
if(.Platform$OS.type=='windows')invisible(Sys.setlocale('LC_CTYPE','English_United States.utf8'))
toolkit_user_libraries<-Sys.getenv('R_LIBS_USER',unset='')
if(nzchar(toolkit_user_libraries)){
  toolkit_user_libraries<-strsplit(toolkit_user_libraries,.Platform$path.sep,fixed=TRUE)[[1]]
  toolkit_user_libraries<-toolkit_user_libraries[dir.exists(toolkit_user_libraries)]
  .libPaths(c(toolkit_user_libraries,.libPaths()))
}
