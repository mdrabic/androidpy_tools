#!/usr/bin/python

"""
Wrapper for basic Android Debug Bridge commands. 
"""


import os
import subprocess
from exception import ADBException
from exception import ADBProcessError
from subprocess import check_output
from subprocess import CalledProcessError

class ADB():

  __adb_path = None
  
  
  def set_adb_path(self, path):
    """
    Set path to the adb executable.
    """  
    self.__adb_path = path


  def _adb_self_test(self, adbPath):
    """
    A simple test to check if the adb executable exists and run the
    'adb version' command for verification.
    adbPath -- Absolute path to ADB

    Throws ADBException:
      If adb file does not exist or does not have execute permissions
    Throws ADBProcessError:
      If the 'adb version' command failed
    """
    if os.path.isfile(adbPath) and os.access(adbPath, os.X_OK):
      self._run_command((adbPath+" version").split())
      return True
    else:
      raise ADBException("ADB could not be located or is not executable")

  
  def adb_shell(self, serial, cmd):
    """
    Execute the specified cmd in the android shell for the device specified 
    by the serial.
    Note: The only way to tell if the cmd sent to the android shell passed or
    executed as expected is for the caller to parse the output to ensure the
    results are what is expected.
    """
    cmd = (self.__adb_path + " -s " + serial + " shell " + cmd).split()
    return self._run_command(cmd.split())

    
    
  def adb_push(self, serial, local, remote):
    """
    Push the specified local file/dir to the remote location on the Android file 
    system for the specified device. 
    """
    cmd = self.__adb_path + " -s " + serial + " push " + local +" "+ remote
    return self._run_command(cmd.split())

    
  def adb_pull(self, serial, remote, local):
    """
    Pull the specified remote file/dir to the local location. 
    """
    cmd = self.__adb_path + " -s " + serial + " pull " + local +" "+ remote
    return self._run_command(cmd.split())
    

  def adb_install(self, serial, apk):
    """
    Install an APK on the device specified by serial. 
    """ 
    cmd = self.__adb_path + " -s " + serial + " install " + apk
    return self._run_command(cmd.split())


  def adb_devices(self):
    """
    Get a list of connected devices
    """
    cmd = self.__adb_path + " devices"
    return self._run_command(cmd.split())


  def _run_command(self, cmd):
    """
    Execute an adb command via the subprocess module. If the process exits with
    a exit status of zero, the output is encapsulated into a ADBCommandResult and
    returned. Otherwise, an ADBExecutionError is thrown.
    """
    try:
        output = check_output(cmd, stderr=subprocess.STDOUT)
        return ADBCommandResult(0,output)
    except CalledProcessError as e:
        raise ADBProcessError(e.cmd, e.returncode, e.output)

  
  def __init__(self,adbPath="adb"):
    """
    Init the class by optionally giving it a path to an adb executable. Otherwise,
    the class assumes adb is the environment PATH variable and retrieves the full
    path to the executable. The adb_self_test function is called to verify ADB.

    adbPath -- Path to adb executable

    Throws ADBException:
      If ADB is not found in PATH or on the file system
      If ADB does not have execute permission

    Throws ADBProcessError
      If the _adb_self_test() does not pass
    """
    tmpPath = adbPath
    if tmpPath == "adb":
      for path in os.environ["PATH"].split(os.pathsep):
        fullADBPath = os.path.join(path,adbPath)
        if os.path.isfile(fullADBPath):
          tmpPath = fullADBPath
          break
      else:
        raise ADBException("ADB not found in PATH")

    if self._adb_self_test(tmpPath):
      self.__adb_path = tmpPath





class ADBCommandResult():
  """
  Holds the result of running an ADB command.
  """

  def __init__(self, rtnCode, output):
    """
    rtnCode -- The exit code
    output -- Any output from the process
    """
    self.rtnCode = rtnCode
    self.output = output
