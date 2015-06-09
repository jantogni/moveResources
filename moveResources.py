import os
import sys
import subprocess

from time import sleep
from optparse import OptionParser

from suds.client import Client

# Default Component values

class tmcdbReader:
    def __init__(self, tmcUser = 'tmc', tmcPasswd = 'tmc\$dba', tmcConStr = 'ALMA_TMC.OSF.CL', sqlQuery = 'lo-lmc-2.sql'):
        """
        Constructor of tmcdbReader class. This class get antenna list deployed
        at lo-lmc-2 container, and get the Pad information from the TMCDBAccess web
        service.
        """
        self.antennasList = {}
        self.tmcUser = tmcUser
        self.tmcPasswd = tmcPasswd
        self.tmcConStr = tmcConStr
        self.sqlQuery = sqlQuery
        self.lmc2 = 'empty'
        self.defaultSteComponents = ['ACACORR1', 'ACACORR2', 'CVR4', 'LMC2']
        print 'Getting TMCDB configuration of CURRENT.AOS'

    def __del__(self):
        """
        Destructor
        """
        self.antennasList = None
        self.tmcUser = None
        self.tmcPasswd = None
        self.tmcConStr = None
        self.sqlQuery = None
        self.lmc2 = None
        self.defaultSteComponents = None

    def sqlplusQuery(self):
        """
        This method take the information from TMCDB database through SQL Query
        of all antennas deployed at lo-lmc-2 container and return the complete list.
        """
        connectionString = self.tmcUser + '/' + self.tmcPasswd +'@' + self.tmcConStr
        pipe = subprocess.Popen('sqlplus -silent ' + connectionString + ' @' + self.sqlQuery, stdout=subprocess.PIPE, shell=True)
        output, error = pipe.communicate()
        if error is not None:
            print "Error: %s" % error
            sys.exit(1)

        return output.strip()

    def getConfiguredAntennas(self):
        """
        Based on sqlplus query output, check if the antenna has deployed both SAS and LLC.
        After that, fill the antenna pad information from TMCDB Access webservice.
        """
        if self.lmc2 == 'empty':
            self.lmc2 = self.sqlplusQuery()
        
        antennas = {}
        antennaName = ['DV', 'DA', 'CM', 'PM']
        
        for i in self.lmc2.split('\n'):
            element = i.split('/')

            if any(a in element[1] for a in antennaName):
                if element[1] in antennas:
                    antennas[element[1]].append(element[2])
                else:
                    antennas[element[1]] = [element[2]]

        client = Client('http://support2.aos.alma.cl:8180/axis2/services/TMCDBAccessService?wsdl')

        for key in antennas:
            if len(antennas[key]) == 2:
                self.antennasList[key] = client.service.getCurrentAntennaPadInfo(key).padName

        return 'ok'

    def getAntennasList(self):
        """
        Return antennaList dict. Key: AntennaNane, Value:Pad
        """
        if self.antennasList == {}:
            self.getConfiguredAntennas()

        return self.antennasList

    def getComponentsList(self):
        """
        Return the default ste component to be moved
        """
        return self.defaultSteComponents

class moveResources:
    def __init__(self, targetSTE):
        """
        Constructor
        """

        tmcdb = tmcdbReader()

        self.antennasList = tmcdb.getAntennasList()
        self.componentsList = tmcdb.getComponentsList()
        self.targetSTE = targetSTE

    def __del__(self):
        """
        Destructor
        """

        self.targetSTE = None
        self.antennasList = None
        self.componentsList = None

    def moveAntenna(self, antennaName, pad, targetSte):
        """
        Move Antenna
        """
        
        #pipe = subprocess.Popen('moveAntennas -a ' + antennaName +' -p ' + pad + ' -s ' + 'TB' + targetSte + ' -v', stdout=subprocess.PIPE, shell=True)
        #output, error = pipe.communicate()
        #if error is not None:
        #    print "Error: %s" % error
        #    sys.exit(1)

        print 'moveAntennas -a ' + antennaName +' -p ' + pad + ' -s ' + 'TB' + targetSte + ' -v'

    def moveComponent(self, componentName, targetSte):
        """
        Move component
        """

        #pipe = subprocess.Popen('moveSteComponents -s ' + targetSte + ' -c ' + componentName + ' -v', stdout=subprocess.PIPE, shell=True)
        #output, error = pipe.communicate()
        #if error is not None:
        #    print "Error: %s" % error
        #    sys.exit(1)

        print 'moveSteComponents -s ' + targetSte + ' -c ' + componentName + ' -v'

    def execute(self):
        """
        Move all antennas, component and reboot the machines
        """
    
        print ""
        print 'Moving antennas to', self.targetSTE
        for antennaName in self.antennasList:
            self.moveAntenna(antennaName, self.antennasList[antennaName], self.targetSTE)
            sleep(0.5)

        print ""
        print 'Moving components to', self.targetSTE
        for componentName in self.componentsList:
            self.moveComponent(componentName, self.targetSTE)
            sleep(0.5)

        print ""
        print "Reboot ACA Machines"
        if self.targetSTE == 'AOS':
            print 'acacor_comps cycle; acacor_power COJ-DMC-1-1 cycle; acacor_power COJ-DMC-1-2 cycle'
            sleep(0.5)
            #pipe = subprocess.Popen('acacor_comps cycle; acacor_power COJ-DMC-1-1 cycle; acacor_power COJ-DMC-1-2 cycle', stdout=subprocess.PIPE, shell=True)
            #output, error = pipe.communicate()
            #if error is not None:
            #    print "Error: %s" % error
            #    sys.exit(1)

            print 'ssh root@coj-os-1 reboot'
            #pipe = subprocess.Popen('ssh root@coj-os-1 reboot', stdout=subprocess.PIPE, shell=True)
            #output, error = pipe.communicate()
            #if error is not None:
            #    print "Error: %s" % error
            #    sys.exit(1)


        if self.targetSTE == 'AOS2':
            print 'ssh almamgr@aos2-gns.osf.alma.cl "acacor_comps cycle; acacor_power COJ-DMC-1-1 cycle; acacor_power COJ-DMC-1-2 cycle"'
            #pipe = subprocess.Popen('ssh almamgr@aos2-gns.osf.alma.cl "acacor_comps cycle; acacor_power COJ-DMC-1-1 cycle; acacor_power COJ-DMC-1-2 cycle"', stdout=subprocess.PIPE, shell=True)
            #output, error = pipe.communicate()
            #if error is not None:
            #    print "Error: %s" % error
            #    sys.exit(1)

            print 'ssh almamgr@aos2-gns.osf.alma.cl "ssh root@coj-os-1 reboot"'
            sleep(0.5)
            #pipe = subprocess.Popen('ssh almamgr@aos2-gns.osf.alma.cl "ssh root@coj-os-1 reboot"', stdout=subprocess.PIPE, shell=True)
            #output, error = pipe.communicate()
            #if error is not None:
            #    print "Error: %s" % error
            #    sys.exit(1)

def optionsParse():
    if "jantogni" not in os.environ['USER']:
        sys.exit("Please run this command as almamgr")

    usage = '''
    moveResources [-s] [-a] [-c] [-d]

    Type -h, --help for help.
    '''

    parser = OptionParser(usage)

    parser.add_option("-s", "--ste", default=False, help = "Mandatory: Target STE to Move Resources (e.g TBAOS, TBAOS2)")
    #parser.add_option("-a", "--antennas", default=False, help = "Optional: If present, only move the antennas in the list")
    #parser.add_option("-c", "--components", default=False, help = "Optional: If present, only move the ste components in the list")
    #parser.add_option("-d", "--default", default='True', help = "Optional: If not present, it use the default configuration of antennas and STE components. If it is False, it will take a hardcode list.")
    #parser.add_option("-t", "--tmcdb", default='CURRENT.AOS', help = "Optional: If present, it will take a specific TMCDB configuration. In other case it will take CURRENT.AOS")

    (options , args) = parser.parse_args()

    if options.ste == False:
        print "Usage:"
        print usage

        sys.exit(0)

    return options

def main():
    options = optionsParse() 

    try:
        #m = moveResources(options.ste, options.default, options.tmcdb, options.antennas, options.components)
        if options.ste in ['AOS', 'AOS2']:
            m = moveResources(options.ste)
            m.execute()
        else:
            print 'STE options are AOS and AOS2, please try again'

    except :
        raise
        print 'Cannot moveResources'
    
if __name__ == '__main__':
    sys.exit( main() )
