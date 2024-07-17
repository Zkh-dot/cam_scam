#!/bin/bash
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTPATH

install_flag=false
button=f12

while getopts 'irb:a:m:' OPTION; do
  case "$OPTION" in
    i)
      echo "running in installation mode"
      install_flag=true
      ;;
    r)
      echo "running in run mode"
      ;;
    b)
      button="$OPTARG"
      ;;
    a)
      echo "set audio file"
      audio_file="$OPTARG"
      ;;
    m)
      echo "set mic id"
      mic_id="$OPTARG"
      ;;
    ?)
      printf "script usage: install-run.sh \n\t[-i] for installation \n\t[-r] for run\n\t[-b button] to set button\n\t[-a path] to set audo file\n\t[-m id] to set mic id\n\n" >&2
      exit 1
      ;;
  esac
done
shift "$(($OPTIND -1))"


if [ -d "./cam_scam_venv" ] || [ $install_flag = false ]; then
    printf "everything seems installed, running...\n"
    printf "running app...\n"
    if [ -z ${audio_file+x} ]; then
        printf "enter path to audio file\n"
        read audio_file
    fi
    if [ -z ${mic_id+x} ]; then
        printf "enter mic id\n"
        read mic_id
    fi
    printf "audio file is set to $audio_file\n"
    printf "mic id is set to $mic_id\n"
    printf "activation button is set to $button\n"
    ./cam_scam_venv/bin/python3 button_registration.py $mic_id $audio_file $button> ./logs/logs.log
else
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
