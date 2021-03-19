# Load Environment Variables
if [ -f "/home/pi/pimonitor_bot/.env" ]; then
    export $(cat "/home/pi/pimonitor_bot/.env" | grep -v '#' | awk '/=/ {print $1}')
fi

# Setting up directories
SUBDIR=incremental
DIR=/media/root/backup/pi/$SUBDIR/

# Check if backup directory exists
if [ ! -d "$DIR" ];
    then
        echo "Incremental backup directory $DIR does not exist, creating it now."
        mkdir $DIR
fi

# notify discord channel
discordnotification --webhook-url="$BACKUP_WEBHOOK" --text "**[incremental]** backup to \`$DIR\` started.\nRunning rsync in archive mode and preserving hard links."

echo "Starting backup, this may take some time."
rsync -aH --delete --exclude-from=/home/pi/pimonitor_bot/cron/rsync-exclude.txt / $DIR

# notify discord channel
discordnotification --webhook-url="$BACKUP_WEBHOOK" --text "**[incremental]** backup has completed successfully.\nNext backup will be performed tomorrow at 20:00."





