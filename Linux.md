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
