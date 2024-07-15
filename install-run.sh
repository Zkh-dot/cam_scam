#!/bin/bash
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTPATH
printf "$SCRIPTPATH\n"

printf "enter path to audio file\n"
read audio_file

printf "enter mic id\n"
read mic_id

if [ -d "./cam_scam_venv" ]; then
    printf "everything seems installed, running..."
else
    # printf "please install linux headers for your kernel. if they are installed, press any key\n"
    # read -p "waiting for any key to continue\n"
    printf "installing headers..."
    sudo pamac install $(pamac list --quiet --installed | grep "^linux[0-9]*[-rt]*$" | awk '{print $1"-headers"}' ORS=' ')
    pacman -S v4l2loopback-dkms v4l2loopback-utils  
    v4l2-ctl --list-devices
    printf "creating venv..."
    python3 -m venv ./cam_scam_venv
    sudo pacman -S gcc
    printf "installing requirements..."
    ./cam_scam_venv/bin/python3 -m pip install -r ./requirements.txt
    mkdir logs
fi

printf "running app..."
./cam_scam_venv/bin/python3 button_registration.py $mic_id $audio_file > ./logs/logs.log
