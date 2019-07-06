# Package Manager Notes

## DNF

~~~
sudo dnf update
dnf info [package]
sudo dnf install [package]
~~~

## Apt-get / Aptitude

~~~
sudo apt-get update # Only updates cache
sudo apt-get upgrade
apt-cache show [package]
sudo apt-get install [package]
apt download [package]
dpkg -I [package] # List info for .deb file, including dependencies
dpkg -x [package] [location] # Extract file tree from .deb file
~~~
