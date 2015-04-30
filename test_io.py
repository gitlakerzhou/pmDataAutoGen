import os
import errno
import datetime
import json
import re
import logging



class TestIO(object):

    def __init__(self):
        self.rootDir = 'Not Defined'
        self.logEnable = False
        #self.metrics_entry = {}
        self.output_list = []

    def dateStr(self):
        dt = datetime.datetime.now()
        return str(dt.year) + '_' + str(dt.month) + '_' + str(dt.day)

    def timeStamp(self):
        dt = datetime.datetime.now()
        return str(dt.day) + '_' + str(dt.hour) + '_' + str(dt.minute)

    def readConfig(self):
        path = os.path.dirname(os.path.realpath(__file__))
        try:
            data = json.loads(open(path + "/" +"CONFIG.json").read())
        except:
            logging.info('No CONIFG file is found, exiting')
            exit(1)
        self.rootDir = data["rootDir"]
        if data["log"] == "enable":
            self.logEnable = True
        for e in data["output"]:
            self.output_list.append(e)
        logging.info("output format: " + ','.join(self.output_list))
		

    def checkEnvironment(self):
        if not os.path.exists(self.rootDir):
            logging.info('creating rootDir' + self.rootDir)
            os.makedirs(self.rootDir)
        #check host file
        if not os.path.exists(self.rootDir + "/hosts"):
            logging.info('Cannot find the hosts file, terminating')
            exit(1)

        #check account file
        if not os.path.exists(self.rootDir +"/accounts"):
            logging.info('Cannot find the accounts file, terminating')
            exit(1)

        print("checking Environment completed")

    def reportFiles(self, ip, cpe):
        files = {}
        if not os.path.exists(self.rootDir +'/' + ip):
            print('creating rootDir' + self.rootDir)
            os.makedirs(self.rootDir +'/' + ip)
        if not os.path.exists(self.rootDir +'/' + ip + '/' + cpe):
            os.makedirs(self.rootDir +'/' + ip + '/' + cpe)
        files["latest"] = open(self.rootDir +'/' + ip + '/' + cpe + '/reprot', 'w+')
        files["daily"]  = open(self.rootDir +'/' + ip + '/' + cpe + '/reprot_' + self.dateStr(), 'a+')
        return files

    def createReports(self, **testMetrics):
        #open the report files
        files = self.reportFiles(testMetrics['ip'], testMetrics['cpe'])

        #build the line:
        line = ''
        for entry in self.output_list:
            if entry in testMetrics:
                line = line + str(testMetrics[entry]) + ','
            else:
                logging.info('measurement ' + entry + 'does not exist!')
        line = line[:-1] + '\n'

        #write the metircs to both latest report and daily report
        files['latest'].write(line)
        files['latest'].close()
        files['daily'].write(line)
        files['daily'].close()
        #close the file and error handling






