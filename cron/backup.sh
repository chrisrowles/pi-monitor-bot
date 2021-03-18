#!/usr/bin/env bash

# Credit: https://www.raspberrypi.org/forums/viewtopic.php?p=136912
# Authors: Rasberry Pi community
# Slightly mofified to read env variables and add webhook trigger for discord notifications.

# if running as cron job, make sure variables are set in /etc/environment

# Load Environment Variables
if [ -f "/home/pi/pimonitor_bot/.env" ]; then
    export $(cat "/home/pi/pimonitor_bot/.env" | grep -v '#' | awk '/=/ {print $1}')
fi

# Setting up directories
SUBDIR=backup
DIR=/media/pi/$SUBDIR

echo "Starting backup process."

# First check if pv package is installed, if not, install it first
PACKAGESTATUS=`dpkg -s pv | grep Status`;

if [[ $PACKAGESTATUS == S* ]]
    then
        echo "pv is installed."
    else
        echo "pv is not installed."
        echo "Installing pv. Please wait..."
        apt-get -y install pv
fi

# Check if backup directory exists
if [ ! -d "$DIR" ];
    then
        echo "Backup directory $DIR does not exist, creating it now."
        mkdir $DIR
fi

# Create a filename with datestamp for current backup (without .img suffix)
OFILE="$DIR/backup_$(date +%Y%m%d_%H%M%S)"

# Create final filename, with suffix
OFILEFINAL=$OFILE.img

# First sync disks
sync; sync

# notify discord channel
discordnotification --webhook-url="$BACKUP_WEBHOOK" --text "**[backup]** to \`$OFILEFINAL\` started\nSuspending services for the duration.\n_See you on the other side Coop._"

# Shut down services before starting backup process
echo "Suspending services before backup."
systemctl stop apache2.service
systemctl stop mysql.service
systemctl stop cron.service

# Shutdown supervisord (run as user pi)
sudo -u pi supervisorctl shutdown

# Begin the backup process
echo "Backing up to destination."
echo "This will take some time depending on card size and read performance. Please wait..."
SDSIZE=`blockdev --getsize64 /dev/mmcblk0`;
pv -tpreb /dev/mmcblk0 -s $SDSIZE | dd of=$OFILE bs=1M conv=sync,noerror iflag=fullblock

# Wait for DD to finish and catch result
RESULT=$?

# notify discord channel
discordnotification --webhook-url="$BACKUP_WEBHOOK" --text "**[backup]** process has finished, verifying backup."

# If command has completed successfully, delete previous backups and exit
if [ $RESULT = 0 ];
    then
        echo "Backup success, previous backups will be deleted."
        discordnotification --webhook-url="$BACKUP_WEBHOOK" --text "**[backup]** verified. Removing previous backups and compressing archive."
        rm -f $DIR/backup_*.tar.gz
        mv $OFILE $OFILEFINAL
        echo "Tarring backup. Please wait..."
        tar zcf $OFILEFINAL.tar.gz $OFILEFINAL
        rm -rf $OFILEFINAL
        # notify discord channel
        discordnotification --webhook-url="$BACKUP_WEBHOOK" --text "**[backup]** complete. Archive compressed and available to download."

        echo "Backup process complete. File - $OFILEFINAL.tar.gz"
        # Start services again that where shutdown before backup process
        echo "Start the stopped services again."
        systemctl start apache2.service
        systemctl start mysql.service
        systemctl start cron.service
        # Restart supervisord
        cd /home/pi
        sudo -u pi supervisord
        sudo -u pi supervisorctl update

        exit 0
    # Else remove attempted backup file
    else
        echo "Backup error, previous backup files untouched."
        echo "Please check there is sufficient disk space."
        # notify discord channel
        discordnotification --webhook-url="$BACKUP_WEBHOOK" --text "**[backup]** error. Previous backups left untouched."
        rm -f $OFILE
        echo "Backup process failed."
        # Start services again that where shutdown before backup process
        echo "Start the stopped services again."
        systemctl start apache2.service
        systemctl start mysql.service
        systemctl start cron.service
        # Restart supervisord
        sudo -u pi supervisord
        sudo -u pi supervisorctl update

        exit 1
fi
