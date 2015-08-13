import sys, time, ast 

from java.lang import String
from java.util import Arrays
from org.apache.commons.collections.list import FixedSizeList;
import simplejson as json
from overtherepy import SshConnectionOptions, OverthereHost, OverthereHostSession
from rtc.ConfigRTCServer import ConfigRTCServer
from rtc.ConfigRTCRepo import ConfigRTCRepo
import org.slf4j.Logger 

class RTCWorkspace(object):
    def __init__(self, config, client_server, uuid=None, work_directory=None, change_set_nr=None):
        self.repo      = ConfigRTCRepo.createRepo(config['username'],config['password'], config['RTC_REPO'], client_server, config['COMPONENT'], work_directory)
	self.name      = config['WORKSPACE']
        self.uuid      = uuid
        self.stream    = config['STREAM']
        self.component = config['COMPONENT']
        self.change_set_nr   = change_set_nr
        self.work_item       = config['WORKITEM']
  
    def __del__(self):
        #logger.info("Class cleanup trying to destroy workspace")
        self.destroy()

    @staticmethod
    def createRTCWorkspace(config, client_server, uuid=None, work_directory=None, change_set_nr=None):
        ws = RTCWorkspace(config, client_server, uuid, work_directory, change_set_nr)
        
        if uuid is None:
          ws.initialize()
        
        return ws

    def initialize(self):
        #logger.info("initialize")
        self.create()	
    	self.add_component()
    	self.set_target()
    	self.load()

    def commit_and_push(self):
        self.checkin()
        if self.change_set_nr:
          self.add_comment()
          self.create_baseline()
          self.assoc_work_item()
          self.deliver_to_stream()
          self.destroy()
          return True
        else:
          #logger.info("no changes where detected, nothing to do here")
          self.destroy()
          return False

    def get_work_directory(self):
        return self.repo.get_work_directory()

    def read_file(self, file_name):
	try:
	  response = self.repo.get_file_as_string(file_name)
        except Exception:
          raise Exception('Unable to read file')
        return response

    def write_file(self, file_name, content):
          response = self.repo.write_string_as_file(file_name, content)
          return response

    def get_uuid(self):
    	if self.uuid is None:
    	  response = self.create()
    	  self.uuid = response['uuid']
        return self.uuid

    def get_change_set_nr(self):
        return self.change_set_nr

    def create(self):
    	response = self.execute("create workspace","%s -e" % self.name)
        self.uuid = response['uuid']

    def destroy(self):
    	if self.uuid is not None:
          #logger.info("destroying workspace: " + self.uuid )
    	  response = self.execute("delete workspace", self.uuid, False)
          self.uuid = None
          #logger.info("workspace destroyed")
          

    def add_component(self):
        self.execute("workspace add-component", "-s %s %s %s " % (self.stream, self.get_uuid(), self.component), False)
	
    def set_target(self):
        self.execute("change-target workspace", "%s %s" % (self.get_uuid(), self.stream), False)

    def load(self):
    	self.execute("load", "%s -d <work_dir> --all -q" % (self.get_uuid()), False)

    def checkin(self):
        response = self.execute("checkin", "%s" % self.get_work_directory(), True, True, False) 
        if response:
          #logger.info("found a valid response to the checking command, getting change_nr")
          self.change_set_nr = response[0]["components"][0]["outgoing-changes"][0]["uuid"]
          #logger.info("change_nr is going to be %s" % (self.change_set_nr))
        else:
          #logger.info("checkin did not give a valid response: this means that there was nothing to check in")
          print("checkin did not give a valid response: this means that there was nothing to check in")
        
    def add_comment(self, msg="config_commit_comment"):
        self.execute("changeset comment", "%s %s" % (self.change_set_nr, msg), False) 

    def create_baseline(self):
        self.execute("create baseline" , "--overwrite-uncommitted --all %s %s" % (self.uuid, "ltb"), False) 

    def assoc_work_item(self):
        self.execute("add workitem" , "%s %s" % (self.change_set_nr, self.work_item), False) 

    def deliver_to_stream(self): 
        self.execute("deliver","-s %s" % (self.uuid))

    def execute(self, command, properties, use_json=True, run_in_workdirectory=False, remote_credentials=True):
	  if use_json is True:
            #logger.info("using json for %s" % (command))
	    response = self.repo.execute_lscm_command(command, properties, use_json, run_in_workdirectory, remote_credentials)
            x = 1
            string_response = None
	    for line in response.stdout:
              if x == 1:
                string_response = ""
              x += 1
              string_response = "%s %s" % (string_response, line)
            if string_response: 
              json_response = json.loads(string_response)
	      return json_response
            else:
              return None
	  else:
            #logger.info("not using json for %s" % (command))
	    response = self.repo.execute_lscm_command(command, properties, use_json, run_in_workdirectory, remote_credentials)
            #logger.info(str(response.stdout))
	    return response
