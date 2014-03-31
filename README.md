# AVX - Audio-Visual Control Extensions 


## INTRODUCTION

AVX is a library designed to allow control of A/V devices such as video
switchers and PTZ cameras.

It's designed to allow control of devices locally or over a network via Pyro4
RPC. A "Controller" process acts as an interface to the devices, and
controlling them is as straightforward as calling a method on the Controller
object.

Rich client applications can be built with Qt or your windowing toolkit of
choice, using Python and Pyro4 for communications.


## INSTALLATION & CONFIGURATION

You will need a Python (2.7 is what I've used) with python-serial, PySide, and
Pyro4.

The easiest method of installing is to either grab a pre-built egg or build one
from source yourself (`python setup.py bdist_egg`) and install using pip. AVX requires:

* Python 2.7
* python-serial
* PySide
* Pyro4
* setuptools

In theory, `pip install` should take care of the dependencies for you. 

Mapping of physical hardware devices through serial ports to virtual devices is
done in the `config.json` file. A typical definition of a single-device system
may look like:

```
{
  "devices" : [
    {
      "deviceID" : "Main",
      "class" : "org.muscat.avx.devices.KramerVP88.KramerVP88",
      "options" : {
        "serialDevice" : "/dev/usb-ports/1-1.3.3:1.0",
        "machineNumber" : 1
      }
    }
  ]
}
``` 

Elements under "options" are passed directly as named parameters to the
constructor (`__init`) of the class. Most, but not all, current devices require
a `serialDevice` option.


Be sure to map devices based on their USB
device path - `/dev/ttyUSBx`'es might get swapped round after a reboot, which
would be sad. Everything GUI-side refers to the `deviceID` string you assign
to each device, so balance these between descriptive and concise.


## RUNNING

You will need a Pyro4 nameserver running somewhere on your network. The 
`runNameserver.sh` script will take care of this for you, or use the
`contrib/pyro-nsd` init script for Debian (maybe others?)

The `runController.py` script will start a Controller instance and register it
with the Pyro4 nameserver, making it available to all machines on your network.
By default it will load a `config.json` configuration file, or whatever you
specify with -c on the commandline.

The controller machine can also use the `contrib/AldatesXController` init script
to run the controller as a daemon.


## Supported Devices

Currently the devices best supported include:

* Kramer video switchers supporting Protocol 2000 over serial
** e.g. VP-88
* Kramer 602 (non-Protocol 2000)
* Inline 3080 video switcher
* Kramer VP70x scan converters
* Coriogen Eclipse scan converter
* Sony VISCA PTZ cameras
* ETC Unison lighting controller
* Several models of USB relay cards

In many cases support is partial but straightforward to improve - patches
welcome!
