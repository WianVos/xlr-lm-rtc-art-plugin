import sys, time, ast,datetime, random, string
from java.lang import String
from java.util import Arrays
from org.apache.commons.collections.list import FixedSizeList;
 


from overtherepy import SshConnectionOptions, OverthereHost, OverthereHostSession, BashScriptBuilder

class ConfigRTCServer(object):
    def __init__(self, server, dirname="tmp", work_directory=None):

        # if 'key_file' in server:
        #   self.sshOpts = SshConnectionOptions(server['host'], username=server['username'],privateKeyFile=server['key_file'])
        # else:
        #   self.sshOpts = SshConnectionOptions(server['host'], username=server['username'],password=server['password'])

        self.sshOpts = SshConnectionOptions(server['host'], username=server['username'],privateKeyFile=server['key_file'],password=server['password'] )

        self.host = OverthereHost(self.sshOpts)
        self.session = OverthereHostSession(self.host)
        self.WorkDirBase = server['filesystemLocation']
        self.session.execute("/bin/mkdir -p %s" % (self.WorkDirBase))
        workDir = self.session.remote_file(self.WorkDirBase)
        self.session.get_conn().setWorkingDirectory(workDir)

        if work_directory is None:
          self.WorkDirTimeStamp = int(time.time())
          self.WorkDirName = dirname
          self.workDirectory = None
        else:
          self.workDirectory = work_directory

        self.RtcClient = server['pathToClientSoftware']




    @staticmethod
    def createServer(server, dirname, work_directory=None): 
        return ConfigRTCServer(server, dirname, work_directory)


    def get_work_directory(self):
        return self.workDirectory
       
    def get_file_contents(self, file_name):
        response = self.session.read_file("%s/%s" % (self.getWorkDirectory(), file_name))
        return response
   
    def write_string_as_file(self, file_name, content):
        remote_file = self.session.remote_file("%s/%s" % (self.getWorkDirectory(), file_name))
        response = self.session.copy_text_to_file(str(content), remote_file)
	 
    def execute_lscm_command(self, command, run_in_workdirectory=False):
        #logger.info(command)
        command = self.sub_placeholders(command)
        lscm_command="%s %s" % (self.RtcClient, command)

        if run_in_workdirectory is False:
          response = self.execute_command(lscm_command)
        else:
          response = self.execute_command_in_workDirectory(lscm_command)
        return response

    def execute_command_in_workDirectory(self, command):
    #    #logger.info("switching overthere to workdirectory")
    #    workDir = self.session.remote_file(self.get_work_directory())
    #    self.session.get_conn().setWorkingDirectory(workDir)
    #    #logger.info("switched to workDirectory")
        command = "cd %s;%s" % (self.get_work_directory(), command) 
        return self.execute_command(command)
 
    #def execute_command(self, command):
    #    #logger.info("executing command: %s " % (command))
    #    response = self.session.execute(command, check_success=False, suppress_streaming_output=False)
    #    if response.rc != 0:
    #      #logger.info(response.stderr)
    #      #logger.info("unable to execute command %s" % (command))
    #      raise Exception('unable to execute command ')
    #    else:
    #      #logger.info("Response", str(response.stdout))
    #      return response

    def execute_command(self, command, retain_scripts=True):
        command_object = BashScriptBuilder()
        for command_line in command.split(';'):
	  command_object.add_line(command_line)
       
        executable_command = command_object.build() 

        tmp_script_file_name = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(9))
        #logger.info("uploading script %s" % tmp_script_file_name) 

        script = self.session.upload_text_content_to_work_dir(executable_command, tmp_script_file_name, executable=True)
        
        response = self.session.execute(script.getPath(), check_success=False, suppress_streaming_output=False)

        #logger.info("stdErr for command yielded: " + str(response.stderr))
        #logger.info("stdOut for command yielded: " + str(response.stdout))
        #logger.info("the returncode for the command was:" + str(response.rc)) 
        if response.rc != 0:
          #logger.info("unable to execute command %s" % (command))
          raise Exception('unable to execute command ')
        else:
          #logger.info("Response", str(response.stdout))
          return response

                 
        
    def getWorkDirectory(self):
        if self.workDirectory is None:
          self.session.execute("/bin/mkdir -p %s/%s/%s" % (self.WorkDirBase,self.WorkDirTimeStamp,self.WorkDirName))
          self.workDirectory =  "%s/%s/%s" % (self.WorkDirBase,self.WorkDirTimeStamp,self.WorkDirName)
        return self.workDirectory

    def destroy_work_directory(self):
        if self.workDirectory is not None:
          self.execute_command("/bin/rm -rf %s/%s" % (self.WorkDirBase, self.WorkDirName))
    
    def sub_placeholders(self, input):
        #logger.info(self.workDirectory)
        #logger.info(self.getWorkDirectory())
	output = input.replace('<work_dir>',  self.getWorkDirectory())
        return output

         
