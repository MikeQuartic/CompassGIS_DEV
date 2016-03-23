# Name: BuildBasemapCache.py
# Description: The following stand-alone script demonstrates how to Recreate all
#               cache tiles for the scales in the cache tiling scheme.
# Requirements: os, sys, time and traceback modules

# Any line that begins with a pound sign is a comment and will not be executed
# Empty quotes take the default value.
# To accept arguments from the command line replace values of variables to
#                                                       "sys.argv[]"

# Import system modules
import arcpy
from arcpy import env
import os, sys, time, datetime, traceback, string, logging, smtplib

# Set environment settings
env.workspace = "E:/data/PUD_CompassGIS"
isOK = True

# List of input variables for map service properties
connectionFile = r"C:\Users\SDGIS\AppData\Roaming\ESRI\Desktop10.3\ArcCatalog"
server = "sdgis@vmgisdev04_6443 (admin)"#TODO Change: this connection file to prod when moving script to prod
folderToService = 'PUD_CompassGIS'
serviceName = "PUD_Basemap_Cache.MapServer"
inputService = connectionFile + "\\" + server + "\\" + folderToService + '\\' + serviceName
# all scales
scales = [1155581.108577, 577790.554289, 288895.277144,144447.638572,72223.819286,36111.909643,18055.954822,9027.977411,4513.988705]
#The scales variable below is for debugging purposes
##scales = [1155581.108577, 577790.554289]
numOfCachingServiceInstances = 2
updateMode = "RECREATE_ALL_TILES"
areaOfInterest = ""
waitForJobCompletion = "WAIT"
updateExtents = ""

#Set up logger.  If you need to debug, set the level=logging.INFO to logging.DEBUG
#(TODO Change the path when moving to another machine)
logging.basicConfig(filename = r'E:\Data\PUD_CompassGIS\LocalExtractedFGDBs\Scripts\BuildBasemapCache.log', level=logging.DEBUG)

#Set up time stamp
currentTime = datetime.datetime.now()
arg1 = currentTime.strftime("%H-%M")
arg2 = currentTime.strftime("%Y-%m-%d %H:%M")

#Header for the log file
logging.info('--------------------------------------------------------------')
logging.info('                  ' + arg2)
logging.info('                Running BuildBasemapCache.py')
logging.info('--------------------------------------------------------------')

try:
    logging.info("ServiceStr: " + str(inputService))
    logging.debug("Starting ManageMapServerCacheTiles_server")

    result = arcpy.ManageMapServerCacheTiles_server(inputService, scales,
                                                    updateMode,
                                                    numOfCachingServiceInstances,
                                                    areaOfInterest, updateExtents,
                                                    waitForJobCompletion)
    #print messages to a file
    while result.status < 4:
        time.sleep(0.2)
    resultValue = result.getMessages()
    logging.info("Completed: \n" +'   '+str(resultValue))
    logging.info("Created cache tiles for given schema successfully for "
    + serviceName)

except Exception, e:
    # If an error occurred, print line number and error message
    tb = sys.exc_info()[2]
    logging.error("Failed at step 1 \n" "Line %i " % tb.tb_lineno)
    logging.error(e.message)
    msg = e.message
    isOK = False




# Setup Email notification
#TODO change: the sender to prod when moved to prod
sender = 'vmgisdev04@sannet.gov'
receivers = ['mike@quarticsolutions.com'] #'chris@quarticsolutions.com','tyler@quarticsolutions.com','drew@quarticsolutions.com', 'rob@quarticsolutions.com', 'timo@quarticsolutions.com']

if isOK == False:
    Subject = "ERROR in BuildBasemapCache.py"
    EmailText = ("ERROR in BuildBasemapCache.py: \n %s" % msg)
else:
    EmailText = "BuildBasemapCache.py ran successfully"
    Subject = "BuildBasemapCache.py ran successfully"

message = """\
From: %s
To: %s
Subject: %s

%s
""" % (sender, ", ".join(receivers), Subject, EmailText)

try:
    smtpObj = smtplib.SMTP('smtp-out.sannet.gov')
    smtpObj.sendmail(sender,receivers, message)
except Exception as e:
    logging.error('Email NOT sent!' + str(e))

logging.info('--------------------------------------------------------------')
logging.info('                  ' + arg2)
logging.info('                Finished BuildBasemapCache.py')
logging.info('--------------------------------------------------------------\n\n')