import ConfigParser
import os
from configparser import ConfigParser, ExtendedInterpolation
import datetime
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from twisted.internet import task
from twisted.internet import reactor
path = "settings.ini"
timeout = 5.0 #in seconds
#from ConfigParser import SafeConfigParser
 
def create_config(path):
    """
    Create a config file
    """
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.add_section("Settings")
    config.set("Settings", "font", "Courier")
    config.set("Settings", "font_size", "10")
    config.set("Settings", "font_style", "Normal")
    config.set("Settings", "font_info",
               "You are using %(font)s at %(font_size)s pt")
    with open(path, "wb") as config_file:
        config.write(config_file)

def initialise(path):
    config = get_config(path)
    if config.has_section('NextSeq_Clients') and config.has_section('Mandatory_Fields') and config.has_section('Async_Settings') :
        for name, value in config.items('NextSeq_Clients'):
            if config.has_section(value):
                if config.getboolean(value,'active'):
                    mandatory=get_setting(path, 'Mandatory_Fields', 'client')
                    if (check_mandatory_fields(mandatory,path,value)):
                        log_dir=get_setting(path, 'Async_Settings', 'LOCAL_BASE_LOG_DIR')
                        client_log=log_dir+"/"+str(value)
                        make_dir(log_dir)
                        make_dir(client_log)
                        make_dir(client_log+"/log")
                        make_dir(client_log+"/db")
                    else:
                        print "*****Missing mandatory fields for", value, "you must have the following fields in your",path,"file :", mandatory
                        exit(1)
                else:
                    print 'Skipping  %s = %s' % (name, value), "as it is inactive"
            else:
                print "No configuration found for ", '  %s = %s' % (name, value)
                
def get_config(path):
    """
    Returns the config object
    """
    if not os.path.exists(path):
        create_config(path)
        print "missing config file"
    config=ConfigParser(interpolation=ExtendedInterpolation())    
    #config = ConfigParser.ConfigParser()
    config.read(path)
    return config

 
def get_setting(path, section, setting):
    """
    Print out a setting
    """
    #print section,setting
    config = get_config(path)
    value = config.get(section, setting)
    """
    print "{section} {setting} is {value}".format(
        section=section, setting=setting, value=value)
        """
    return value
 
 
def update_setting(path, section, setting, value):
    """
    Update a setting
    """
    config = get_config(path)
    config.set(section, setting, value)
    with open(path, "wb") as config_file:
        config.write(config_file)
 
 
def delete_setting(path, section, setting):
    """
    Delete a setting
    """
    config = get_config(path)
    config.remove_option(section, setting)
    with open(path, "wb") as config_file:
        config.write(config_file)
 
def check_mandatory_fields(mandatory_list,path,section_name):
    mandatory_options=mandatory_list.strip().split(',')
    config = get_config(path)
    #my_settings=config.options(section_name)
    for candidate in mandatory_options:
        if config.has_option(section_name, candidate) is False:
            print "**Missing Field**:",candidate
            return False
    return True    

def run_process(cmd, logfile):
    """ execute a process"""
    #print cmd
    p = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
    stdout = []
    while True:
        line = p.stdout.readline()
        stdout.append(line)
       # print line,
        if line == '' and p.poll() != None:
            break
    loglist=''.join(stdout)
    outfile=open(logfile, "w")
    outfile.write(loglist)
    outfile.close()
    return p.returncode


    

def upload_to_remote_server(files_with_dir,filename):
    #print filename
    #print url
    ""
    logfile=filename+"_cat.debug.log"
    cmd= "cat " +files_with_dir+" > "+filename
    code=run_process(cmd, logfile)

def download_from_remote_server(files_with_dir,filename):
    #print filename
    #print url
    logfile=filename+"_cat.debug.log"
    cmd= "cat " +files_with_dir+" > "+filename
    code=run_process(cmd, logfile)


def main(path):
    config = get_config(path)
    if config.has_section('NextSeq_Clients') and config.has_section('Mandatory_Fields') :
        for name, value in config.items('NextSeq_Clients'):
            #print '  %s = %s' % (name, value)
            if config.has_section(value):
                if config.getboolean(value,'active'):
                    #check if all mandatory options are present for this client
                    mandatory=get_setting(path, 'Mandatory_Fields', 'client')
                    if (check_mandatory_fields(mandatory,path,value)):
                        print "process", '  %s = %s' % (name, value)
                        for param, val in config.items(value):
                            print '  %s = %s' % (param, val)
                            
                    else:
                        print "*****Missing mandatory fields for", value, "you must have the following fields in your",path,"file :", mandatory
                        exit(1)
                else:
                    print 'Skipping  %s = %s' % (name, value), "as it is inactive"
            else:
                print "No configuration found for ", '  %s = %s' % (name, value)
                
    """
    for section in config.sections():
        print section
    """
    #print url
 
def make_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
def check_file(filename):
    if os.path.isfile(filename) and os.access(filename, os.R_OK):
        return True
    else:
        return False
def execute_transfer():
    initialise(path)
    main(path)

#----------------------------------------------------------------------
if __name__ == "__main__":
    l = task.LoopingCall(execute_transfer)
    l.start(timeout) # call every sixty seconds
    reactor.run()
   