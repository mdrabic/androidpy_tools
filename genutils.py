#!/usr/bin/python

"""
Utility class that provides functions to aid in the provisioning of a device. 
"""

from adb import *
from exception import * 
import argparse
import hashlib
import os


class Genutils():

  def __init__(self, adb, serial):
    """
    Init the class with the serial number of the device that is being 
    provisioned and an instance of ADB. The serial number is needed due to the 
    parameter dependency by the adb.py module.
    """
    self.adb = adb
    self.serial = serial
  
  
  def wait_boot_complete(self, encryption='off'):
    """
    When data at rest encryption is turned on, there needs to be a waiting period 
    during boot up for the user to enter the DAR password. This function will wait
    till the password has been entered and the phone has finished booting up.
    
    OR
    
    Wait for the BOOT_COMPLETED intent to be broadcast by check the system 
    property 'sys.boot_completed'. A ADBProcessError is thrown if there is an 
    error communicating with the device. 
    
    This method assumes the phone will eventually reach the boot completed state.
    
    A check is needed to see if the output length is zero because the property
    is not initialized with a 0 value. It is created once the intent is broadcast.

    """
    if encryption is 'on':
      decrypted = None
      target = 'trigger_restart_framework'
      print 'waiting for framework restart'
      while decrypted is None:
        status = self.adb.adb_shell(self.serial, "getprop vold.decrypt")
        if status.output.strip() == 'trigger_restart_framework':
          decrypted = 'true'
          
      #Wait for boot to complete. The boot completed intent is broadcast before
      #boot is actually completed when encryption is enabled. So 'key' off the 
      #animation.
      status = self.adb.adb_shell(self.serial, "getprop init.svc.bootanim").output.strip()
      print 'wait for animation to start'
      while status == 'stopped':
        status = self.adb.adb_shell(self.serial, "getprop init.svc.bootanim").output.strip()
      
      status = self.adb.adb_shell(self.serial, "getprop init.svc.bootanim").output.strip()
      print 'waiting for animation to finish'
      while status == 'running':
        status = self.adb.adb_shell(self.serial, "getprop init.svc.bootanim").output.strip()        
        
    else:
      boot = False
      while(not boot):      
        self.adb.adb_wait_for_device(self.serial)
        res = self.adb.adb_shell(self.serial, "getprop sys.boot_completed")
        if len(res.output.strip()) != 0 and int(res.output.strip()) is 1:
          boot = True
       

  def push_and_set_file(self, local, remote, chown=None, fileMode=None):
    """
    A convience method to push a local file to a remote location on the phone,
    set the owner/group and set the file mode. 
    
    local  -- Path to file to push.
    remote -- Where the file should be placed on the device. 
              Note: remote should *NOT* include the file's name. Only location. 
    chown  -- Owner & Group in the format "owner.group". ex. "app_1.app_1"
    fileMode -- The file mode bits in octal form. ex "777" or "751"
    """   
    self.adb.adb_push(self.serial, local, remote)
    #create a file obj; use get name    
    if chown is not None:
      self.adb.adb_shell(self.serial, 
                    "chown "+chown+" "+remote+os.sep+os.path.basename(local))
    if fileMode is not None: 
      self.adb.adb_shell(self.serial,
                    "chmod "+str(fileMode)+" "+remote+os.sep+os.path.basename(local))

     
  def install_busybox(self, busybox):
    """
    Install the busybox utility on the device into the /system/newbin directory.
    busybox -- The path to busybox on the local filesystem. 
    """    
    self.adb.adb_shell(self.serial, "mkdir /system/newbin")
    self.push_and_set_file(busybox,
                      "/system/newbin",fileMode=755)
    self.adb.adb_shell(self.serial, 
                  "/system/newbin/busybox --install /system/newbin")
    self.adb.adb_shell(self.serial, "mv /system/newbin/grep /system/bin")
    self.adb.adb_shell(self.serial, "mv /system/newbin/sed /system/bin")
    self.adb.adb_shell(self.serial, "mv /system/newbin/cp /system/bin")
    self.adb.adb_shell(self.serial, "mv /system/newbin/pkill /system/bin")
    self.adb.adb_shell(self.serial, "rm -r /system/newbin/")


  def sha1sum(self, f, block=2**20):
    """
    Produce a SHA 1 digest of the file. 
    f -- the path to the file to hash. 
    """
    if(os.path.isfile(f) and os.access(f, os.R_OK)):
      mFile = open(f,'rb');
      sha1 = hashlib.sha1()
      
      while True:
        data = mFile.read(block)
        if not data:
          break
        sha1.update(data)
      
      return sha1.hexdigest()
      
    else:
      raise IOError('File "'+f+'" does not exist or is unreadable.')
      
   
  def get_app_id(self, package):
    """
    Get the packages owner ID. 
    package -- The application's installation package name. Ex. "com.example.app"
    """
    res = self.adb.adb_shell(self.serial,
          "ls -l /data/data | grep %s | sed -e 's|.* a|a|g' | sed -e 's| .*||g'"%(package))
    return res.output.strip()
  
  
