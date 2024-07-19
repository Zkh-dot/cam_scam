#!/bin/bash

# go to code dir
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTPATH

# default values
install_flag=false
button="f12"
only="all"

# detect system packet manager
declare -A osInfo;
osInfo[/etc/arch-release]="pacman -S"
osInfo[/etc/debian_version]="apt-get install"

for f in ${!osInfo[@]}
do
    if [[ -f $f ]];then
        pack_manager=${osInfo[$f]}
    fi
done
if [ -z ${pack_manager+x} ]; then 
  echo "we have no idea, what this system is, sorry"
  exit 255
fi

# get command line arguments
while getopts 'irb:a:m:o:' OPTION; do
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
    o)
      echo "only $OPTARG"
      only="$OPTARG"
      ;;
    ?)
      printf "script usage: install-run.sh \n\t[-i] for installation \n\t[-r] for run\n\t[-b button] to set button\n\t[-a path] to set audo file\n\t[-m id] to set mic id\n\t[-o mic/video] to work only with mic or video\n" >&2
      exit 1
      ;;
  esac
done
shift "$(($OPTIND -1))"


if [ -d "./cam_scam_venv" ] && [ $install_flag = false ]; then
    printf "everything seems installed, running...\n"
    printf "running app...\n"
    if [ -z ${audio_file+x} ] && [ $only != "cam" ]; then
        printf "enter path to audio file\n"
        read audio_file
    fi
    if [ -z ${mic_id+x} ] && [ $only != "cam" ]; then
        printf "enter mic id\n"
        read mic_id
    fi
    printf "audio file is set to $audio_file\n"
    printf "mic id is set to $mic_id\n"
    printf "activation button is set to $button\n"
    ./cam_scam_venv/bin/python3 button_registration.py $button $only $mic_id $audio_file # > ./logs/logs.log
else
    printf "installing headers..."
    if [ "$pack_manager" == "pacman -S" ]; then
      sudo pamac install $(pamac list --quiet --installed | grep "^linux[0-9]*[-rt]*$" | awk '{print $1"-headers"}' ORS=' ')
    else
      sudo apt-get install linux-headers-$(uname -r);
    fi
    $pack_manager v4l2loopback-dkms v4l2loopback-utils  
    v4l2-ctl --list-devices
    printf "creating venv..."
    if [ "$pack_manager" == "apt-get install" ]; then
      sudo $pack_manager python3.$(python3 -c 'import sys;print(sys.version_info[:][1])')-venv
      # sudo $pack_manager python3-pip -y
    fi
    python3 -m venv ./cam_scam_venv
    sudo $pack_manager gcc
    printf "installing requirements..."
    ./cam_scam_venv/bin/pip3 install -r ./requirements.txt
    mkdir logs
fi