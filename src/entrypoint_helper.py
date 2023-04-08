import os
import yaml
import subprocess

# load and parse config.yaml
with open('/filebup/config/config.yaml') as configf:
    configl = yaml.load(configf, Loader=yaml.SafeLoader)

# iterate over all repos in config.yaml
for volume in configl.keys():
    if configl[volume]['service'] == 'borg':
        localpath = configl[volume]['localpath']
        borguser = configl[volume]['borguser']
        borghost = configl[volume]['borghost']
        borgport = configl[volume]['borgport']
        borgdir = configl[volume]['borgdir']
        borgsshkey = configl[volume]['borgsshkey']
        borgpass = configl[volume]['borgpass']

        borgschedule = configl[volume]['borgschedule']
        hcheckurlbup = configl[volume]['hcheckurlbup']

        pruneschedule = configl[volume]['pruneschedule']
        hcheckurlprune = configl[volume]['hcheckurlprune']
        hcheckurlcompact = configl[volume]['hcheckurlcompact']

        checkschedule = configl[volume]['checkschedule']
        hcheckurlcheck = configl[volume]['hcheckurlcheck']

        # load cronfile
        with open('/var/spool/cron/crontabs/root') as cronf:
            cronc = cronf.read()
        
        # check if cron for regular pulling exists alreay in cronfile
        if volume in cronc:
            print('Volume {} backup with borg already in cronfile'.format(volume))
        else:
            helpercreatesh = "#!/bin/bash\n"
            helpercreatesh += "chmod 400 /filebup/config/secrets/{}\n".format(borgsshkey)
            helpercreatesh += "healthcheckurl={}\n".format(hcheckurlbup)
            helpercreatesh += "export BORG_RSH='ssh -o StrictHostKeyChecking=no -i /filebup/config/secrets/{}'\n".format(borgsshkey)
            helpercreatesh += "export BORG_PASSPHRASE='{}'\n".format(borgpass)
            helpercreatesh += "REPOSITORY='ssh://{}@{}:{}/./{}'\n".format(borguser, borghost, borgport, borgdir)
            helpercreatesh += "curl -fsS -m 10 --retry 5 -o /dev/null $healthcheckurl/start\n"
            helpercreatesh += "m=$(borg create -s --show-version --show-rc -c 300 -C auto,lzma,6 $REPOSITORY::$(date +'%Y%m%d-%H%M') /filebup/volumes/{} 2>&1)\n".format(localpath)
            helpercreatesh += "curl -fsS -m 10 --retry 5 --data-raw \"$(echo \"$m\" | tail -c 100000)\" $healthcheckurl/$?\n"
            helpercreatesh += "unset healthcheckurl BORG_RSH BORG_PASSPHRASE REPOSITORY m"

            with open('/filebup/cronhelpers/{}-create.sh'.format(volume), 'w') as writer:
                writer.write(helpercreatesh)

            subprocess.run(['echo ''"''{} sh /filebup/cronhelpers/{}-create.sh''"'' >> /var/spool/cron/crontabs/root'.format(borgschedule, volume)], shell=True) 

            print('Volume {} backup create with borg written to cronfile'.format(volume))


            helperpruneesh = "#!/bin/bash\n"
            helperpruneesh += "chmod 400 /filebup/config/secrets/{}\n".format(borgsshkey)
            helperpruneesh += "healthcheckurl={}\n".format(hcheckurlprune)
            helperpruneesh += "healthcheckurlcompact={}\n".format(hcheckurlcompact)
            helperpruneesh += "export BORG_RSH='ssh -o StrictHostKeyChecking=no -i /filebup/config/secrets/{}'\n".format(borgsshkey)
            helperpruneesh += "export BORG_PASSPHRASE='{}'\n".format(borgpass)
            helperpruneesh += "REPOSITORY='ssh://{}@{}:{}/./{}'\n".format(borguser, borghost, borgport, borgdir)
            helperpruneesh += "curl -fsS -m 10 --retry 5 -o /dev/null $healthcheckurl/start\n"
            helperpruneesh += "m=$(borg prune -v --list --keep-within=1w -d=28 -w=12 -m=12 -y=5 $REPOSITORY 2>&1)\n"
            helperpruneesh += "curl -fsS -m 10 --retry 5 --data-raw \"$(echo \"$m\" | tail -c 100000)\" $healthcheckurl/$?\n"
            helperpruneesh += "unset m\n"
            helperpruneesh += "curl -fsS -m 10 --retry 5 -o /dev/null $healthcheckurlcompact/start\n"
            helperpruneesh += "m=$(borg compact $REPOSITORY 2>&1)\n"
            helperpruneesh += "curl -fsS -m 10 --retry 5 --data-raw \"$(echo \"$m\" | tail -c 100000)\" $healthcheckurlcompact/$?\n"
            helperpruneesh += "unset healthcheckurl healthcheckurlcompact BORG_RSH BORG_PASSPHRASE REPOSITORY m"

            with open('/filebup/cronhelpers/{}-prune.sh'.format(volume), 'w') as writer:
                writer.write(helperpruneesh)

            subprocess.run(['echo ''"''{} sh /filebup/cronhelpers/{}-prune.sh''"'' >> /var/spool/cron/crontabs/root'.format(pruneschedule, volume)], shell=True) 

            print('Volume {} backup prune and compact with borg written to cronfile'.format(volume))


            helperchecksh = "#!/bin/bash\n"
            helperchecksh += "chmod 400 /filebup/config/secrets/{}\n".format(borgsshkey)
            helperchecksh += "healthcheckurl={}\n".format(hcheckurlcheck)
            helperchecksh += "export BORG_RSH='ssh -o StrictHostKeyChecking=no -i /filebup/config/secrets/{}'\n".format(borgsshkey)
            helperchecksh += "export BORG_PASSPHRASE='{}'\n".format(borgpass)
            helperchecksh += "REPOSITORY='ssh://{}@{}:{}/./{}'\n".format(borguser, borghost, borgport, borgdir)
            helperchecksh += "curl -fsS -m 10 --retry 5 -o /dev/null $healthcheckurl/start\n"
            helperchecksh += "m=$(borg check --verbose --progress $REPOSITORY 2>&1)\n"
            helperchecksh += "curl -fsS -m 10 --retry 5 --data-raw \"$(echo \"$m\" | tail -c 100000)\" $healthcheckurl/$?\n"
            helperchecksh += "unset healthcheckurl BORG_RSH BORG_PASSPHRASE REPOSITORY m"

            with open('/filebup/cronhelpers/{}-check.sh'.format(volume), 'w') as writer:
                writer.write(helperchecksh)

            subprocess.run(['echo ''"''{} sh /filebup/cronhelpers/{}-check.sh''"'' >> /var/spool/cron/crontabs/root'.format(checkschedule, volume)], shell=True) 

            print('Volume {} backup check with borg written to cronfile'.format(volume))
    else:
        print('{} not yet supported'.format(configl[volume]['service']))
