echo OFF
echo NOTE: 
echo Run this in its own dedicated terminal! 
echo Print Control C to stop the web server.
echo -------------------------------------------

echo $env:BSB_DEV_TOOLS_UI='True' turns on DEV TOOLS (='False' for off)
REM python bsbetl\index.py
REM use below command when bsbetl is installed as a package
python .\venv\Lib\site-packages\bsbetl\index.py