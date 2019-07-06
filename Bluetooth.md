# Bluetooth notes

## hcitool
Search for BLE devices, test connections

~~~
hcitool dev                      # List Blueooth interfaces
hcitool lescan                   # Scan for BLE advertisers
hcitool lename [MAC]             # Find BLE device's name (cannot be used while connection is active)
hcitool leinfo [MAC]             # Find BLE device's info (cannot be used while connection is active)
hcitool lecc [MAC]               # Connect to BLE device
hcitool ledc [Connection ID]     # Disconnect from BLE device
hcitool con                      # List active connections
~~~

## gatttool
Read and write GATT characteristics

~~~
# Open ineractive session
gatttool -I

# In interactive session:
connect [MAC]            # Connect to a BLE device
characteristics          # List all GATT characteristics
char-read-hnd [handle]   # Read GATT characteristic by handle

# Read characteristic
gatttool --device=[MAC] --char-read --handle=0x[handle]
~~~
