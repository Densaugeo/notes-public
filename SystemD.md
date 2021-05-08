# SystemD Notes

DO NOT EVER, FOR ANY REASON, PLACE A SYMLINK IN `/usr/lib/systemd/system`. Some of Fedora's built-in service put symlinks here, but don't try it yourself - symlinked services can appear to work at first and then simply vanish from SystemD later (journalctl and systemctl status won't work on them, even if the symlinks are still present and intact).

~~~
systemctl status SERVICE
sudo systemctl start SERVICE
sudo systemctl stop SERVICE
sudo systemctl enable SERVICE # Cause SERVICE to run at startup
sudo systemctl disable SERVICE # Cause SERVICE to NOT run at startup
sudo systemctl status SERVICE@USER # Some services need to have a user specified (such as Syncthing)
sudo journalctl -u SERVICE # Read a service's logs
~~~

Service available for starting/enabling are stored in `/usr/lib/systemd/system` (at least on Fedora). Services that are enabled to run on startup are symlinked in `/etc/systemd/system`. The symlinks in `/usr/lib/systemd/system` do not appear to cause problems like the ones in `/usr/lib/systemd/system`.
