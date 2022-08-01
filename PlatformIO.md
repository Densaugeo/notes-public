# PlatformIO Notes

## Installation

`python -m pip install --user platformio`

Docs recommended installing custom udev rules that PlatformIO supplies, but I did not need them. This may or may not be because the Arduino IDE was already installed.

Adding the current user to the dialout group would probably be required, but it had previously been done for Arduino.

Note that PlatformIO automatically installs toolchains when needed, so when installing you should build and download whichever project you are concerned about to install all the extras.

## Project Setup

~~~
mkdir project-folder
cd project-folder
python -m platformio project init --board SOME_BOARD
~~~

I used `nanoatmega328` and `nanoatmega328old` for the boards. It created a skeleton project, and set up the `plaformio,ini` file for using these boards. I have not tried to add boards to a project later on yet.

## Usage

~~~
python -m platformio run                               # Builds for all boards in plaformio.ini
python -m platformio run -e SOME_BOARD                 # Builds for the specified board

# Builds for the specified board and uploads. I did not have to specify a USB port
python -m platformio run -e SOME_BOARD --target upload 

# The pkg command installs libraries, and apparently other things too. The author name is the Github
# user of the package's repo, and the package name seems to come from the Arduino packaging file.
# For my base64 library it was 'densaugeo/base64'
python -m pkg install --library 'AUTHOR/PACKAGE'
~~~