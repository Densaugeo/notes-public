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
ssh-keygen -t rsa -f ~/.ssh/id_rsa_foo -C ''           # Create key
ssh-keygen -t rsa -f ~/.ssh/id_rsa_foo -C '' -N ''     # Create key (no passphrase)
ssh-keygen -t rsa -f ~/.ssh/id_rsa_foo -C $(hostname)  # Create key labeled with hostname
ssh-keygen -lvf ~/.ssh/id_rsa_foo.pub                  # View ASCII art
ssh-copy-id -i ~/.ssh/id_rsa_foo.pub username@hostname # Copy public key to host
ssh -i ~/.ssh/id_rsa_foo username@hostname             # Login with key
echo 'Host hostname                                    # Configure SSH login
    User username
    IdentityFile ~/.ssh/id_rsa_foo
    AddKeysToAgent yes
' >> ~/.ssh/config
ssh-add ~/.ssh/id_rsa_foo                              # Load key into ssh-agent (check with new settings)

waypipe ssh username@hostname SOME_APP                 # Run Wayland app on host and forward with Waypipe
ssh -X username@hostname-x SOME_APP                    # Run X app on host and forward with SSH

# Fix for Wayland/X forwarding between Fedora PCs (client side):
echo 'Host hostname
    # Fixes for Wayland forwarding and KDA themes on farwarded GUIs
    SetEnv XDG_CURRENT_DESKTOP=kde QT_QPA_PLATFORM=wayland

Host hostname-x
    HostName hostname
    # Fix for KDA themes on farwarded GUIs
    SetEnv XDG_CURRENT_DESKTOP=kde
' >> ~/.ssh/config

# Fix for Wayland/X forwarding between Fedora PCs (host side):
sudo bash -c 'echo "# Needed to allow Wayland forwarding
AcceptEnv QT_QPA_PLATFORM

# Needed to allow KDE themes in forwarded apps
AcceptEnv XDG_CURRENT_DESKTOP
" > /etc/ssh/sshd_config.d/waypipe-fix.conf'
sudo chmod 600 /etc/ssh/sshd_config.d/waypipe-fix.conf

~~~

## Grep

~~~
grep foo PATH                                    # Search for foo in file at PATH
grep foo PATH -n                                 # Show line numbers
grep foo PATH --color=always | sed 's/^[\t]*//'  # Remove leading whitespace*
grep foo PATH --color=always | sort | uniq       # Remove duplicates*
grep foo PATH wc -l                              # Count lines with matches
# *Incompatible with -n. Only compatible with -r if --no-filename is also used. Useful together

grep foo PATH -r                                 # Recursive
grep foo PATH -r --no-filename                   # Don't print filenames
grep foo PATH -rnI                               # Exclude binary files
grep foo PATH -rn --exclude=*.txt                # Exclude .txt files
grep foo PATH -rn --include=*.txt                # Include only .txt files
grep foo PATH -rl                                # List files with matches
grep foo PATH -rl | wc -l                        # Count files with matches
diff <(grep foo PATH -rl) <(grep bar PATH -rl)   # Check if foo and bar occur in the same files
# Print count of foo in each immediate subfolder
ls | xargs --replace={} sh -c "echo -n '{}: '; grep 'foo' -r '{}' | wc -l"

grep 'foo\.' PATH                                # Foo plus a literal period
grep '[Ff][Oo]\{2\}' PATH                        # Case insensitive foo
grep -E '[Ff][Oo]{2}' PATH                       # -E allows less escaping
grep '^foo' PATH                                 # Lines beginning with foo
grep 'foo$' PATH                                 # Lines ending with foo. Unreliable
grep '[^[:alnum:]]foo[^[:alnum:]]' PATH          # Foo with no alphanumeric chars before or after
~~~

## Vim

~~~
:se ww+=<> # :set whichwrap=<> Allows navigation with arrows to wrap over newlines
:se bs=2 # :set basckspace=indent,eol,start Allows normal backspacing in insert mode
:se mouse=a # Enable mouse
:se bo=all # :set belloff=all
~~~

## Block Devices

~~~
lsblk                              # List block devices
cat /etc/fstab                     # Mounting info for "permanent" drives
cat /etc/mtab                      # Mounting info for all currently mounted drives
sudo blkid --probe DEVICE          # Detailed block device info
sudo mount DEVICE MOUNT_POINT
sudo umount DEVICE|MOUNT_POINT

# For filesystems that don't store security info
sudo mount DEVICE MOUNT_POINT -o uid=1000,gid=1000,dmask=002,fmask=113
~~~

/etc/fstab
~~~
# FS_SPEC MOUNT_POINT FS_TYPE OPTIONS DUMP FSCK
# DUMP = 0 or 1 to disable/enable integration with the 'dump' tool I don't use
# FSCK = 0 to not use, 1 for boot partition, 2 for others to be checked at boot

# Basic ext4 drive
UUID=UUID MOUNT_POINT ext4 defaults 0 2

# To save options for vfat flash drive
UUID=UUID MOUNT_POINT vfat defaults,noauto,uid=1000,gid=1000,dmask=002,fmask=113 0 0
~~~

## Rsync

~~~
# Do not use trailing slashes in SOURCE; this causes unpredictable behavior
# By default, rsync uses file sizes and modification times to check for update. -c causes it to sue md5 instead
rsync -nv SOURCE DESTINATION               # Verbose dry run - see what rsync will do
rsync -r SOURCE DESTINATION                # Recursive - on first run, copies folder (excluding metadata)
rsync -rc --delete SOURCE DESTINATION      # -c for checksum and --delete ensure complete update

# These seem to only work sometimes? Better method: diff <(tree -sDC) ...
rsync -nvr --delete SOURCE DESTINATION     # Check for changes by file sizes and modification times
rsync -nvrc --delete SOURCE DESTINATION    # Check for changes by checksum
~~~

## Nmap

TCP connection creation:

~~~
Client > SYN > Host        # TCP and SYN scans start here
Client < SYN/ACK < Host    # If port is closed, RST is sent instead
Client > ACK > Host        # SYN scans end here by sending RST instead
                           # ACK scans start here
Client < Data? < Host      # If port is closed, RST is sent instead
Client > RST > Host        # TCP and ACK scans end here
~~~

Common commands:

~~~
# Protocol scan for ICMP, IGMP, IPv4, TCP, UDP, IPv6, IPv6-route, and IPv6-frag
sudo nmap HOST -sO -p 1,2,4,6,17,41,43,44

nmap HOST -sT -p 80                     # TCP scan port 80
sudo nmap HOST -sS -p 80,433,8000-8080  # SYN scan ports 80, 443, and 8000-8080
~~~

| Scan Type | Arg | No Response    | ICMP Unreachable <br /> (Code = 1-3, 9-10, or 13) | RST | Other
|-----------|-----|----------------|---|---|---
| Protocol  | -sO | open\|filtered | Code ≠ 2: filtered <br /> Code = 2: closed || Anything else: open
| UDP       | -sU | open\|filtered | Code ≠ 3: filtered <br /> Code = 3: closed || Anything else: open
| TCP       | -sT | filtered       | filtered | closed | Full connection: open
| SYN       | -sS | filtered       | filtered | closed | SYN/ACK: open
| ACK       | -sA | filtered       | filtered | unfiltered
| Window*   | -sW | filtered       | filtered | Window size = 0: closed <br /> Window size > 0: open
| Null*     | -sN | open\|filtered | filtered | closed
| FIN*      | -sF | open\|filtered | filtered | closed
| Xmas*     | -sX | open\|filtered | filtered | closed
| Maimon*   | -sM | open\|filtered | filtered | closed

*Scan results unreliable due to poor standards compliance

| Scan Type | Notes
|-----------|---
| TCP       | TCP connect scan. Only scan that does not require root
| Window    | Like ACK scan, but checks the response's window size field
| Null      | TCP scan with no flags
| Xmas      | TCP scan with FIN, PSH, and URG flags
| Maimon    | TCP scan with FIN and ACK flags

## File Tricks

~~~
# Set permissions on all files in file tree beginning at PATH
find PATH -type f -exec chmod 664 {} +

# Copy files in sequence (for car radio)
cd SOURCE_DIR
find . -type f | sed 's/^/"/g' | sed 's/$/"/g' | xargs cp -t TARGET_DIR --parents

# Compare two folders by layout (-s = sizes, -D = modification times, -C = always colorize)
diff <(tree -sDC 'FOLDER_1') <(tree -sDC 'FOLDER_2')

# Compare two folders by file contents
git diff --no-index 'FOLDER_1' 'FOLDER_2'
~~~

## Script Writing

~~~
#!/bin/bash
# -e: Exit if a command fails
# -u: Treat unset variables as an error in parameter expansion
# -f: Disable pathname expansion
# -o pipefail: If any command in a pipe fails, the pipe fails
set -euf -o pipefail

# Check scripts with shellcheck
~~~

## Useful folders

~~~
/boot
/lib/modules
/proc
~~~
