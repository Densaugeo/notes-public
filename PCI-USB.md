# PCI and USB Topology Notes

## PCI

`lspci`
- USB2 and USB3 controllers come in pairs. Each USB2+USB3 controller pair appears as a single controller in `lspci`.
- USB4 controllers appear as separate devices in `lspci`
- USB2/3 controllers may not be labeled with their version number, but USB4 usually are.

`lstopo`
- Most PCI devices don't show up in lstopo. I couldn't find any solid information abouy why. Maybe they are built into the CPU.
- Some people say the numbers are bandwidth, but I was unable to confirm.
- Nvidia GPUs can slow down their PCI speed, so numbers they report may be low.
- At least one person on Reddit thought the little squares are bridges and ports, but this doesn't make much sense. There are too many of them.

`sudo dmesg | grep iommu`

## USB

`lsusb`
- USB4 controllers do not appear in `lsusb`.
- USB4 controllers do not necessarily correspond to USB2/3 controllers. Physical ports that share a USB2/3 controller may not share a USB4 controller and vice versa.
- The most knowledgeable poster I found on Reddit said that the difference between USB 3.0/3.1/3.2 is a "pdf version" not a speed difference, and should be ignored.
- USB3 ports that share a controller may have different capabilities, especially related to video output. I had trouble following the explanation but it seems related to hardware timers for the high-speed connection.

## Reddit Threads

- https://www.reddit.com/r/VFIO/comments/1iafrbw/what_do_the_connection_numbers_in_lstopo_mean/
- https://www.reddit.com/r/framework/comments/1iapm7n/mapping_pciusb_topology/
