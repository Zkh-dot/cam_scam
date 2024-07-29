# cam_scam

Currently supports arch-, ubuntu- and debian- based distributives. Works with any amount of cameras and only one mic. For stable instalation we recomend kernel version higher than 6.5, but you can be lucky with older one.

## installation

To install the program, run install-run.sh like 
```bash 
sudo ./install-run.sh -i
```

and enter all required values. Then run the command


``` bash
v4l2-ctl --list-devices
```

If it successfully lists available physical cameras, the installation was successful.

## usage

To run the program, FIRST connect all physical cameras and microphones, then re-run install-run.sh and enter all the required values. The launch is complete, you can use the program.

You can see all options with 

```bash
./install-run.sh -q
```