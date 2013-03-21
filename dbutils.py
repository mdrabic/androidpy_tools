#!/usr/bin/python

import os
import re
import sqlite3

"""
Utility methods for database opertations. 
"""

class sqlUtil():

  def __init__(self, database):
    """
    Create an instance of sqlUtil by providing the path to a sqlite database that 
    needs to be modified. 
    
    database -- Absolute path to the database.   
    """
    if os.path.isfile(database) and os.access(database, os.R_OK):
      self.conn = sqlite3.connect(database)
    else:
      raise IOError("Database not found or no permissions to access it")
      
    

  def simple_update(self, table, col, value):
    """
    Execute an update statement which will update the column named 'col' to 
    the value.
    """
    if not bool(re.search(r'[^A-Za-z0-9_]', table)):
      cursor = self.conn.cursor()
      cursor.execute('update '+table+' set value=? where name=?',(col, value))
      self.conn.commit()
      return True
    else:
      return False
      
      
  def simple_insert(self, table, cols, values):
    """
    Execute a insert statement which will insert the values 'values' into the 
    the columns 'cols'. 
    
    table -- name of table to insert data into
    cols -- column names in the format "col1,col2"
    values -- values to insert in the format "val1,val2,val3"
    """
    if not bool(re.search(r'[^A-Za-z0-9_]', table)) and \
       not bool(re.search(r'[^A-Za-z0-9_,]', cols))  and \
       not bool(re.search(r"[^A-Za-z0-9_,.\-\@:*'<>]", values)):
      cursor = self.conn.cursor()
      cursor.execute('INSERT INTO '+table+' ('+cols+') values ('+values+')')
      self.conn.commit()
      return True
    else:
      return False
    

  def close():
    """
    Close the current connection to the database
    """
    self.conn.close();
    
