import os
import yaml
import subprocess

# load and parse config.yaml
with open('/filebup/config/config.yaml') as configf:
    configl = yaml.load(configf, Loader=yaml.SafeLoader)

# iterate over config.yaml
for crons in configl.keys():
    if configl[crons]['service'] == 'borg':
        schedule = configl[crons]['schedule']
        command = configl[crons]['command']

        # load cronfile
        with open('/var/spool/cron/crontabs/root') as cronf:
            cronc = cronf.read()

        # check if cron for regular pulling exists alreay in cronfile
        if command in cronc:
            print('Command {} already in cronfile'.format(command))
        else:
            subprocess.run(['echo ''"''{} {}''"'' >> /var/spool/cron/crontabs/root'.format(schedule, command)], shell=True) 
            print('Command {} written to cronfile'.format(command))