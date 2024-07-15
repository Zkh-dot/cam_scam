#!/bin/bash
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTPATH
printf "$SCRIPTPATH\n"

if [ -d "./cam_scam_venv" ]; then
    printf "everything seems installed, running..."
else
    # printf "please install linux headers for your kernel. if they are installed, press any key\n"
    # read -p "waiting for any key to continue\n"
    printf "installing headers..."
    sudo pamac install $(pamac list --quiet --installed | grep "^linux[0-9]*[-rt]*$" | awk '{print $1"-headers"}' ORS=' ')

    v4l2-ctl --list-devices
    printf "creating venv..."
    python3 -m venv ./cam_scam_venv
    printf "installing requirements..."
    ./cam_scam_venv/bin/python3 -m pip install -r ./requirements.txt
fi

printf "running app..."
./cam_scam_venv/bin/python3 button_registration.py > ./logs/logs.log