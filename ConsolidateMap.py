# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# ConsolidateMap.py
# Created on: 2014-07-08
#
# Description:  This is to extract the data layers needed from sde and
# place in a localfile.gdb for the CompassGIS Application.
# ---------------------------------------------------------------------------

# Import arcpy module
import os.path, arcpy, logging, smtplib, sys
from datetime import datetime
from arcpy import env
env.overwriteOutput = True

#Set up logger.  If you need to debug, set the level=logging.INFO to logging.DEBUG
#(TODO Change the path when moving to another machine)
fileLog = r'E:\Data\PUD_CompassGIS\LocalExtractedFGDBs\Scripts\ConsolidateMap.log'
logging.basicConfig(filename = fileLog, level=logging.DEBUG)

#Header for the log file
logging.info('--------------------------------------------------------------')
logging.info('                  ' + str(datetime.now()))
logging.info('                Running ConsolidateMap.py')
logging.info('--------------------------------------------------------------')

# Local variables:

# this is the where the data is coming from. In this case the infrastructure data is coming from SDE and the station data is coming from a query layer on atlasdev
CompassGIS_fgdb_source_mxd = arcpy.GetParameterAsText(0)
##CompassGIS_fgdb_source_mxd = sys.argv[0]
# this is where the data is going to.  This extract data will be used by the arcserver service
Extract = arcpy.GetParameterAsText(1)
##Extract = sys.argv[1]
# Process: Consolidate Map
arcpy.env.overwriteOutput = True
try:
    arcpy.ConsolidateMap_management(CompassGIS_fgdb_source_mxd, Extract, "CONVERT", "CONVERT_ARCSDE", "DEFAULT", "ALL")
    logging.info('ConsolidateMap_management ran successfully')
    Subject = 'ConsolidateMap_management ran successfully'
    EmailText = 'ConsolidateMap_management ran successfully'
except:
    logging.error(arcpy.GetMessages())
    Subject = 'ERROR with ConsolidateMap_management'
    EmailText = 'Check error log at E:\\Data\\PUD_CompassGIS\\LocalExtractedFGDBs\\Scripts \n ERROR: ' + arcpy.GetMessages()

# Setup Email notification
#TODO change: the sender to prod when moved to prod
try:
    sender = 'vmgisdev04@sannet.gov'
    receivers = ['mike@quarticsolutions.com'] #'chris@quarticsolutions.com','tyler@quarticsolutions.com','drew@quarticsolutions.com', 'rob@quarticsolutions.com', 'timo@quarticsolutions.com']

except Exception as e:
        logging.error('ERROR: Email not sent!')
        logging.error('ERROR: ' + str(e))

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
logging.info('                  ' + str(datetime.now()))
logging.info('                Finished ConsolidateMap.py')
logging.info('--------------------------------------------------------------')