# Linux Notes

## Useful commands

~~~
lsmod
modprobe
modinfo
lspci
lsusb
lsblk
top
free [-h]
ps [-e]
df [-h] [device]
shutdown now [-h/-r]
poweroff
reboot
virsh
qemu-img
virsh: list start reboot shutdown autostart destroy (which actually just forces off)
~~~

## Vim

~~~
:se ww+=<> # :set whichwrap=<> Allows navigation with arrows to wrap over newlines
:se bs=2 # :set basckspace=indent,eol,start Allows normal backspacing in insert mode
:se mouse=a # Enable mouse
:se bo=all # :set belloff=all
~~~

## Copy files in sequence (for car radio)

~~~
cd SOURCE_DIR
find . -type f | sed 's/^/"/g' | sed 's/$/"/g' | xargs cp -t TARGET_DIR --parents
~~~

## Useful folders

~~~
/boot
/lib/modules
/proc
~~~
