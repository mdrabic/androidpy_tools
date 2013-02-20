#!/usr/bin/python

import time
import threading
from adb import ADB
from adb import ADBCommandResult

"""
Utilities to support the various android pytools.
"""

class Phone():
  """
  Holds device unique information.
  """

  def __init__(self, adbSerial):
    self.adbSerial = adbSerial


class DeviceManager(threading.Thread):
  """
  Responsible for detecting devices and acquiring device unique information.
  """

  # A list of Phones currently connected via ADB
  _devices = []
  _adb = None

  def remove_device(self,serial):
    """
    A device has been disconnected. Remove the device from the device list.
    """
    for device in self._devices:
      if device.adb_serial_num == serial:
        print "Device removed: "+serial
        self._devices.remove(device)
        return True

    return False


  def add_device(self,serial):
    """
    A new device has been connected. Add the device to the device list.
    """
    for device in self._devices:
        if device.adb_serial_num == serial:
            return False

    self._devices.append(Phone(serial))
    print "Device: "+serial+" added"
    return True


  def get_device_serial(self):
    p = self._devices[0]
    return p.adbSerial



  def run(self):
    """
    Loop infinitely to detect device connection/removals. If new device is
    connected, add it to the device list. If device is removed, remove it
    from the device list.

    Note: Only one device connection is supported at this time.
    """
    while True:
      list =  self.adb.adb_devices().strip().split("\n")

      # >= 2 since list[0] is 'List of connected Devices'; list[1] = serial number
      if len(list) >= 2:
        serial = list[1].split("\t")[0]
        if serial != self._devices[0]:
          self._devices.pop(0)
          self._devices.append(Phone(serial))

      time.sleep(.5)


  def __init__(self, adb=ADB()):
    self.adb = adb
