# VM Notes

## Disk management

~~~
qemu-img convert -t qcow2 -t raw [input file] [output file] # Convert a qcow2 image to a raw image
sudo mount -o offset=[offset in bytes] [image] [mount point] # Mount a partition from a raw image
fdisk -l [image] # Print disk info. Offset used for mounting = [start]*[sector size]
~~~
