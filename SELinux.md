# SELinux Notes

~~~
ls -Z # Print SELinux settings for files
chcon -[u/r/t] [value] [file] # Change SELinux settings for files
getenforce # Get enforcing state
setenforce [0/1/permissive] # Set enforcing state
cat /var/log/audit/audit.log | grep -a [whatever] # SELinux access logs are here. -a needed to read as text
cat /var/log/audit/audit.log | grep -a [whatever] | audit2why # Explain why whatever was denied
cat /var/log/audit/audit.log | grep -a [whatever] | audit2allow # List rules that would allow whatever
cat /var/log/audit/audit.log | grep -a [whatever] | audit2allow -m [whatever] # Print a module to allow whatever
cat /var/log/audit/audit.log | grep -a [whatever] | audit2allow -M [whatever] # Create package to allow whatever
semodule -i [whatever] # Install package for whatever
checkmodule ??? # Compile a module from plain text
semodule_package ??? # Create a package from a compiled module
semanage booleans -l # List all adjustable booleans
setsebool -P [boolean_name] [0/1] # Set boolean and persist across reboots
~~~

SELinux Commands that worked to enable syncthing:

~~~
sudo cat /var/log/audit/audit.log | grep -a syncthing | audit2allow -a -M selinux
sudo semodule -i selinux.pp
rm selinux.pp
~~~
