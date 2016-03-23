#Created By: Mike Grue
#Date: 02-08-2016
#Purposse:  This script is run to take the data that the city is giving us
# from their Y: drive and putting it on a local server that is running the
# CompassGIS application.
#Note: The first time that this script is run, you should make sure that
# you have a path all the way to where the script should create
# the SplashData_additional folder.  The CREATE FILES MODULE will run
# if it can't find the SplashData_additional folder and will create
# a few other files and folders in that SplashData_additional folder.


import os.path, arcpy, logging, smtplib
from datetime import datetime
from arcpy import env
env.overwriteOutput = True

#Set up logger.  If you need to debug, set the level=logging.INFO to logging.DEBUG
#(TODO Change the path when moving to another machine)
fileLog = r'E:\Data\PUD_CompassGIS\LocalExtractedFGDBs\Scripts\SplashData_additional.log'
logging.basicConfig(filename = fileLog, level=logging.DEBUG)

#Header for the log file
logging.info('--------------------------------------------------------------')
logging.info('                  ' + str(datetime.now()))
logging.info('                Running SplashData_additional.py')
logging.info('--------------------------------------------------------------')


#--------------------------------------------------------------
                             #SET VARIABLES

#Set the path to the folder of the FGDB that contains the NEW data you want to copy over
newData_file_gdb = r"\\ad\pubutil\PUMGMT\zPUMGMT_PublicShare\StrategicPrograms\AssetManagement\CompassGIS\Stage3\DataToQuartic\SplashData_additional.gdb"

#Set the FGDB name of the CURRENTLY used data, path to the folder it lives in
#(TODO Change the path when moving to another machine), and the full path to the FGDB in that folder.
currentFGDB = "SplashData_additional.gdb"
currentData_file_loc = r"E:\Data\PUD_CompassGIS\LocalExtractedFGDBs\Infrastructure_Extract\SplashData_additional"
currentData_gdb_loc = currentData_file_loc + "\\" + currentFGDB


#Set the FGDB name of the BACKUP data, path to the folder it lives in, and the full path to the FGDB in that folder.
backupFGDB = "SplashData_additional_backup.gdb"
backupData_file_loc = currentData_file_loc + "\\Backup"
backupData_gdb_loc = backupData_file_loc + "\\" + backupFGDB

#Set the Feature Class names in a list to cycle through in the COPY NEW DATA TO CURRENT DATA
fcList = ['CP_ANODE_BED', 'cpFitting', 'CP_SITE', 'cpRectifier',
                  'cpTestStation', 'cpWire', 'pudEasement', 'pudFuelLine',
                  'S_MAIN_ALL', 'pudFiber', 'TC_STATION', 'W_PIPE_ALL',
                  'W_SERVICE', 'COMFORT_STOP', 'pudJumpOver']

#Set the error handler for the email service
error = 0

#--------------------------------------------------------------
                         #CREATE FILES MODULE

#Tests to see if Current Data folder exists if not, this module creates it.
#This will happen the first time that this script is run in a new location.
#Flag controling if we need to run the BACKUP MODULE
needBackup = True

try:
    logging.info('Starting Create Files Module')
    exists = os.path.exists(currentData_file_loc)
    if exists == False:
        needBackup = False  #We don't need to make a backup if we have just created the currentFGDB
        logging.info("Folder at: \n   %s \nDoesn't exist.  \nMaking folder and currentFGDB." % currentData_file_loc)
        os.mkdir(currentData_file_loc)
        os.mkdir(backupData_file_loc)
        #Make the Current FGDB
        arcpy.CreateFileGDB_management(currentData_file_loc, currentFGDB , "CURRENT")
        logging.info('Finished making folders')
    else:
        logging.info('Folder at: \n  %s \nExists..Do not need to Create Files\n' % currentData_file_loc)
except Exception as e:
    logging.error('Create Files Failed')
    logging.error('Error: ' + str(e))
    error = 1
#-------------------------------------------------------------
                       #BACKUP CURRENT DATA MODULE

#If needBackup is True, then that means that there was already a folder
#called SplashData_additional at the currentData_file_loc and thus,
#needs to be backed up before we import over the new data to the current data

#We don't want to try to backup the data if the CREATE FILES MODULE failed
if error == 0:
    try:
        logging.info('Starting Backup Current Data Module')
        if needBackup == True: #Backup existing FGDB

            #Overwrite the backup FGDB in the "backupData_file_loc" location
            arcpy.CreateFileGDB_management(backupData_file_loc, backupFGDB , "CURRENT")

            #Loop through all of the FC's in the "currentData_gdb_loc" and copy them to the "backupData_gdb_loc"
            env.workspace = currentData_gdb_loc  #Needed for ListFeatureClasses()

            featureClasses = arcpy.ListFeatureClasses()
            for fcIn in featureClasses:
                logging.debug("Backing up %s" % fcIn)
                fcOut = backupData_gdb_loc + "\\" + fcIn
                arcpy.CopyFeatures_management(fcIn, fcOut)
            logging.info('Finished Backing up Current Data')
        else:
            logging.debug('Backup not needed')

    except Exception as e:
        logging.error('Backup Current Data Failed')
        logging.error('Error: ' + str(e))
        error = 2
else:
    pass
#--------------------------------------------------------------
                  #COPY NEW DATA TO CURRENT DATA MODULE
#We don't want to copy over new data if the BACKUP CURRENT DATA
#or CREATE FILES MODULE failed
if error == 0:
    try:
        logging.info('Starting Copy New Data to Current Data Module')
        #Overwrite the new FGDB in the "CurrentData_file_loc" location
        logging.debug("Creating FGDB to load new data into")
        arcpy.CreateFileGDB_management(currentData_file_loc, currentFGDB, "CURRENT")

        #Loop through all of the FC's in the "newData_file_gdb" and copy them to the currentData_gdb_loc
        env.workspace = newData_file_gdb  #Needed for ListFeatureClasses()

        #Count the number of FC's in the FGDB the City gave us.  If it is less than 15, give a warning
        NewFC_count = len(arcpy.ListFeatureClasses())
        if NewFC_count != 15:
            logging.error('There are %s FC\'s in the New FGDB' % NewFC_count)
            logging.error('There are supposed to be 15 FC\'s in the New FGDB')
            logging.error('New Data has not been imported to Current Data')
        else:
            #The Number of FC's was correct and we are now going to import the new data
            logging.info('There should be 15 FC\'s in the New FGDB: \n   There are %s FC\'s in the New FGDB' % NewFC_count)
            for fcIn in fcList:
                logging.debug("Copying %s" % fcIn)
                fcOut = currentData_gdb_loc + "\\" + fcIn
                arcpy.CopyFeatures_management(fcIn, fcOut)

            #Check to make sure that the correct number of FC's were imported from the City
            #If this number !=15 (but the number of FC's in the New FGDB was correct) it means
            #that we were not given the same list of data that we were expecting in the FcList
            #Talk to the city...
            env.workspace = currentData_gdb_loc
            CurrentFC_count = len(arcpy.ListFeatureClasses())
            if CurrentFC_count != 15:
                logging.error('There are not the correct number of FC\'s in the Current FGDB')
            else:
                logging.info('Finished Copying %s New FC\'s to Current Data' % CurrentFC_count)

    except Exception as e:
        logging.error('Copy New Data to Current Data Failed')
        logging.error('Error: ' + str(e))
        error = 3
else:
    pass

logging.info('--------------------------------------------------------------')
logging.info('                  ' + str(datetime.now()))
logging.info('                   Finished running script')
logging.info('--------------------------------------------------------------')


# Setup Email notification
#TODO change: the sender to prod when moved to prod
try:
    sender = 'vmgisdev04@sannet.gov'
    receivers = ['mike@quarticsolutions.com'] #'chris@quarticsolutions.com','tyler@quarticsolutions.com','drew@quarticsolutions.com', 'rob@quarticsolutions.com', 'timo@quarticsolutions.com']

    if error == 0:
        Subject = "SplashData_additional.py ran successfully"
        EmailText = ("SplashData_additional.py ran successfully")
    elif error == 1:
        Subject= "ERROR with SplashData_additional.py"
        EmailText  = "CREATE FILES MODULE Failed. \n Please check log at " + fileLog
    elif error == 2:
        Subject= "ERROR with SplashData_additional.py"
        EmailText  = "BACKUP CURRENT DATA MODULE Failed. \n Please check log at " + fileLog
    elif error == 3:
        Subject= "ERROR with SplashData_additional.py"
        EmailText  = "COPY NEW DATA TO CURRENT DATA MODULE Failed. \n Please check log at " + fileLog
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


#raw_input("Press ENTER to continue")

