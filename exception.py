#!/usr/bin/python

"""
Contains android-pytool specific exceptions.
"""


class ADBException(Exception):
  """
  Generic exception indicating anything relating to the execution
  of ADB. A string containing an error message should be supplied
  when raising this exception.
  """
  def __init__(self,msg):
    """
    msg -- string indicating the error that occurred
    """
    self.msg = msg


class ADBProcessError(ADBException):
  """
  Exception to describe an ADB execution error.  For example, the adb
  command could return 0 but the shell on the android device does not
  understand the command it received. Thus, this exception should not be
  thrown.

  An example of an appropriate situation is when a adb push command is ran
  and the remote location is read-only. The push will fail and this should
  be thrown.
  """

  def __init__(self, cmd, rtnCode, output):
    """
    cmd -- The string or byte array of the adb command ran
    rtnCode -- The process return code
    output -- Any output from the failed process
    """
    self.cmd = cmd
    self.rtnCode = rtnCode
    self.output = output
    self.msg = "ADB returned a non-zero exit code"
