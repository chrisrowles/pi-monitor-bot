#!/usr/bin/env bash

[[ "$(whoami)" != 'root' ]] &&
{
    echo "This script requires sudo privileges"
    exit 1;
}

ROOTDIR=/home/pi/pimonitor_bot
INSTALLDIR=${ROOTDIR}/provision

# check if discord.sh is installed for webhooks, if not, install it first
if [ -f /usr/bin/discordnotification ];
    then
        echo "discord.sh is installed"
    else
        echo "Installing discord.sh from https://github.com/ChaoticWeg"
        wget https://raw.githubusercontent.com/ChaoticWeg/discord.sh/master/discord.sh -O /usr/bin/discordnotification
        chmod u+x /usr/bin/discordnotification
fi

# check if fail2ban is installed, if not, install it first
FAIL2BANSTATUS=`dpkg -s fail2ban | grep Status`;
if [[ $FAIL2BANSTATUS == S* ]]
    then
        echo "fail2ban is installed."
    else
        echo "fail2ban is not installed."
        echo "Installing fail2ban. Please wait..."
        apt-get -y install fail2ban

        echo "setting up discord webhook"
        cp ${INSTALLDIR}/webhook/fail2ban_discord.conf /etc/fail2ban/action.d/discord_notifications.conf

        echo "copying jail configuration"
        cp ${INSTALLDIR}/jail.local /etc/fail2ban/jail.local
fi

# make sure fail2ban is started and enabled at boot
echo "starting fail2ban and enabling at system boot"
systemctl start fail2ban
systemctl enable fail2ban

# setup backup cron jobs
echo "setting up backup cron jobs"
(crontab -l ; echo "00 09 01 * * bash "$ROOTDIR"/cron/backup-dd.sh") | sort - | uniq - | crontab -
(crontab -l ; echo "00 09 * * * bash "$ROOTDIR"/cron/backup-rsync.sh") | sort - | uniq - | crontab -

# check if supervisor is installed, if not then install it
SUPERVISORSTATUS=`dpkg -s supervisor | grep Status`;
if [[ $SUPERVISORSTATUS == S* ]]
    then
        echo "supervisor is installed."
    else
        echo "supervisor is not installed."
        echo "Installing supervisor. Please wait..."
        apt-get -y install supervisor

        # Configure to run as user pi
        chown -R pi:pi /var/log/supervisor
        cp ${INSTALLDIR}/supervisord.conf /etc/supervisord.conf
fi

# Add supervisor configuration
cp ${ROOTDIR}/supervisor/bot.supervisor /etc/supervisord/conf.d/

# run supervisor and ensure latest config is loaded
supervisord
supervisorctl update

supervisorctl status
echo "If supervisor is running, then your bot should now be online in Discord."

exit 0
