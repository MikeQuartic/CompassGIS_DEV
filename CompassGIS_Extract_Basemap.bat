set log=E:\Data\PUD_CompassGIS\LocalExtractedFGDBs\Scripts\CompassGIS_Extract_Basemap.log

echo >>%log%
echo ----------------------[START %date% %time%]------------------- >>%log%
echo >>%log%


SET JOBDIR=E:\Data\PUD_CompassGIS\LocalExtractedFGDBs\Scripts\



echo Stopping Basemap and Infrastructure Map Services... >>%log%
D:\Programs\ServerAdminToolkit\TaskAutomation\agsAdmin.py vmgisdev04 6080 ArcGISServer101 101ServerArcGIS stop PUD_CompassGIS/PUD_Basemap_Dynamic.MapServer>> %log%
D:\Programs\ServerAdminToolkit\TaskAutomation\agsAdmin.py vmgisdev04 6080 ArcGISServer101 101ServerArcGIS stop PUD_CompassGIS/PUD_Infrastructure_Dynamic.MapServer >> %log%

echo Starting Consolidating Basemap Map ... >>%log%
Start /wait %JOBDIR%\ConsolidateMap.py E:\Data\PUD_CompassGIS\LocalExtractedFGDBs\PUD_Basemap_Dynamic_source.mxd E:\Data\PUD_CompassGIS\LocalExtractedFGDBs\Basemap_Dynamic_Extract >>%log%

timeout /T 5

echo Starting Basemap and Infrastructure Map Services... >>%log%
D:\Programs\ServerAdminToolkit\TaskAutomation\agsAdmin.py vmgisdev04 6080 ArcGISServer101 101ServerArcGIS start PUD_CompassGIS/PUD_Basemap_Dynamic.MapServer>> %log%
D:\Programs\ServerAdminToolkit\TaskAutomation\agsAdmin.py vmgisdev04 6080 ArcGISServer101 101ServerArcGIS start PUD_CompassGIS/PUD_Infrastructure_Dynamic.MapServer >> %log%

echo Starting BuildBasemapCache.py ... >>%log%
Start /wait %JOBDIR%\BuildBasemapCache.py

echo -----------------------[END %date% %time%]--------------------- >>%log%
