# TinyCoreLinux Notes

For the PiCore variant of TinyCoreLinux, version 8.0.

## General info

- Default username: tc
- Default password: ???
- Startup script location: `/opt/bootlocal.sh`
- Hostname setting: `host=[hostname]` argument of `cmdline.txt`/`cmdline3.txt` in root of PICORE partition
- List of automatically loaded TCEs: `/mnt/mmcblk0p2/tce/onboot.lst`

## Key commands

~~~
tce-load -wi [module] # Download and install a module
sudo wifi.sh # Interactively connect to a wifi network
sudo wifi.sh -a # Automatically connect to first stored wifi network
filetool.sh -b # Save user files
filetool.sh -d # List files that will be saved and their size
filetool.sh -r # Revert changes since last save (can also be done by rebooting)

# The exact files saved by filetool.sh are those listed in /opt/.filetool.lst, but not excluded by /opt/.xfiletool.sh
~~~

## Setup

~~~
# To enable ssh, set a password
sudo passwd tc
[password]
[confirm password]

# To set up wifi
tce-load -wi wifi
sudo wifi.sh
[select network]
[password]
echo 'sudo wifi.sh -a' >> /opt/bootlocal.sh
~~~
