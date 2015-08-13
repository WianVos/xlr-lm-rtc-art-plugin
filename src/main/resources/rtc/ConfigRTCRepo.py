import sys, time, ast

from java.lang import String
from java.util import Arrays
from org.apache.commons.collections.list import FixedSizeList;



from overtherepy import SshConnectionOptions, OverthereHost, OverthereHostSession
from rtc.ConfigRTCServer import ConfigRTCServer

class ConfigRTCRepo(object):
    def __init__(self, username, password, url, client_server,component, work_directory=None):
        self.server              = ConfigRTCServer.createServer(client_server, component, work_directory)
        self.rtc_username        = username
        self.rtc_password        = password
        self.rtc_repo            = url
        
    @staticmethod
    def createRepo(username,password,url, client_server, component, work_directory=None):
        return ConfigRTCRepo(username,password,url, client_server, component, work_directory)   

    def get_work_directory(self):
       return self.server.get_work_directory()

    def execute_lscm_command(self, command, properties, json=True, run_in_workdirectory=False, remote_credentials=True):
      if json: 
        return self.server.execute_lscm_command("%s %s %s --json" % (command, self.rtc_command_credentials(remote_credentials), properties), run_in_workdirectory)
      else:
        return self.server.execute_lscm_command("%s %s %s" % (command, self.rtc_command_credentials(remote_credentials), properties), run_in_workdirectory)

    def get_file_as_string(self, file_name):
      return self.server.get_file_contents(file_name)

    def write_string_as_file(self, file_name, content):
      return self.server.write_string_as_file(file_name, content)
            
    def rtc_command_credentials(self, remote=True):
        if remote:
          return " -u %s -P %s -r %s" % (self.rtc_username, self.rtc_password, self.rtc_repo)
        else:
          return " -u %s -P %s" % (self.rtc_username, self.rtc_password)

     
    def get_server(self):
        return self.server

   
