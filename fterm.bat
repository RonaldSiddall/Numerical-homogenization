@echo off
SET cdir=\%CD:~0,1%\%CD:~3,256%
SET L=%CD:~0,1%
docker run -ti --rm -v "%L%:\:/%L%/" -v "c:\:/c/" -w "%cdir:\=/%" flow123d/flow123d-gnu:3.9.0 %*
pause
