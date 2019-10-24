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

## SSH

~~~
ssh username@hostname                                  # Basic login
scp /some/path username@hostname:/some/path            # Copy file
ssh-keygen -t rsa -f ~/.ssh/id_rsa_foo                 # Create key
ssh-keygen -t rsa -f ~/.ssh/id_rsa_foo -N ''           # Create key (no passphrase)
ssh-keygen -lvf ~/.ssh/id_rsa_foo.pub                  # View ASCII art
ssh-copy-id -i ~/.ssh/id_rsa_foo.pub username@hostname # Copy public key to host
ssh -i ~/.ssh/id_rsa_foo username@hostname             # Login with key
echo 'Host hostname                                    # Configure SSH login
    IdentityFile ~/.ssh/id_rsa_foo
    User username
' >> .ssh/config
ssh-add ~/.ssh/id_rsa_foo                              # Load key into ssh-agent (check with new settings)
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
