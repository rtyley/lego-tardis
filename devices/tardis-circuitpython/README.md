

```bash
cd ~/development/lego-tardis/tardis-circuitpython
circup --path device-fs/ install -r requirements.txt
circup --path device-fs/ update
```


https://learn.adafruit.com/welcome-to-circuitpython/pycharm-and-circuitpython

I'm trialing omitting the
[_'add CIRCUITPY as a content root'_](https://learn.adafruit.com/welcome-to-circuitpython/pycharm-and-circuitpython#creating-a-project-on-a-computers-file-system-3105042-4)
part, instead mounting the CIRCUITPY drive as a sub-folder of my git project, so I can directly git-commit files
from the CIRCUITPY usb device.

https://apple.stackexchange.com/a/147722/432617

```commandline
diskutil list external CIRCUITPY
/dev/disk4 (external, physical):
   #:                       TYPE NAME                    SIZE       IDENTIFIER
   0:     FDisk_partition_scheme                        *1.0 MB     disk4
   1:                 DOS_FAT_12 CIRCUITPY               1.0 MB     disk4s1

sudo mount -t msdos /dev/disk4s1 lego-tardis/circuitpython
```

```commandline
diskutil unmount lego-tardis/circuitpython
```

```commandline
diskutil rename CIRCUITPY LEGO-TARDIS
Volume on disk4s1 renamed to LEGO-TARDIS
```

```commandline
cat /etc/fstab
#
# Warning - this file should only be modified with vifs(8)
#
# Failure to do so is unsupported and may be destructive.
#

LABEL=LEGO-TARDIS /Users/roberto/development/lego-tardis/devices/tardis-circuitpython/device-fs msdos -u=501
```

* adafruit-circuitpython-ds3231
* adafruit-circuitpython-aw9523
* https://github.com/pimoroni/pmk-circuitpython ??
* [adafruit-circuitpython-is31fl3731](https://pypi.org/project/adafruit-circuitpython-is31fl3731/)

