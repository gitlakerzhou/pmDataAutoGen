import os
import errno
import datetime
import json
import re

class TestIO(object):

    def __init__(self):
        self.rootDir = 'Not Defined'
        self.logEnable = False
        self.metrics_entry = {}
        self.test_list = []

    def dateStr(self):
        dt = datetime.datetime.now()
        return str(dt.year) + '_' + str(dt.month) + '_' + str(dt.day)

    def timeStamp(self):
        dt = datetime.datetime.now()
        return str(dt.day) + '_' + str(dt.hour) + '_' + str(dt.minute)

    def readConfig(self):
        try:
            data = json.loads(open("CONFIG.json").read())
        except:
            print('No CONIFG file is found, exiting')
            exit(1)
        self.rootDir = data["rootDir"]
        if data["log"] == "enable":
            self.logEnable = True

    def checkEnvironment(self):
        if not os.path.exists(self.rootDir):
            print('creating rootDir' + self.rootDir)
            os.makedirs(self.rootDir)
        #check host file
        if not os.path.exists(self.rootDir + "\\hosts"):
            print('Cannot find the hosts file, terminating')
            exit(1)

        #check account file
        if not os.path.exists(self.rootDir +"\\accounts"):
            print('Cannot find the accounts file, terminating')
            exit(1)

        print("checking Environment completed")

    def reportFiles(self, ip, cpe):
        files = {}
        if not os.path.exists(self.rootDir +'\\' + ip):
            print('creating rootDir' + self.rootDir)
            os.makedirs(self.rootDir +'\\' + ip)
        if not os.path.exists(self.rootDir +'\\' + ip + '\\' + cpe):
            os.makedirs(self.rootDir +'\\' + ip + '\\' + cpe)
        files["latest"] = open(self.rootDir +'\\' + ip + '\\' + cpe + '\\reprot', 'w+')
        files["daily"]  = open(self.rootDir +'\\' + ip + '\\' + cpe + '\\reprot_' + self.dateStr(), 'a+')
        return files

    def createReports(self, **testMetrics):
        #open the report files
        files = self.reportFiles(str(testMetrics['ip']), str(testMetrics['cpe']))
        #write the metircs to both latest report and daily report
        line = str(testMetrics['avail'])+','+str(testMetrics['pktNum'])+'%'+'\n'
        files['latest'].write(line)
        files['latest'].close()
        files['daily'].write(line)
        files['daily'].close()
        #close the file and error handling

    def get_time(self, line):
        re1='(time)'	# Word 1
        re2='.*?'	# Non-greedy match on filler
        re3='((?:[0]?[1-9]|[1][012])[-:\\/.](?:(?:[0-2]?\\d{1})|(?:[3][01]{1}))[-:\\/.](?:(?:[1]{1}\\d{1}\\d{1}\\d{1})|(?:[2]{1}\\d{3})))(?![\\d])'	# MMDDYYYY 1
        re4='.*?'	# Non-greedy match on filler
        re5='((?:(?:[0-1][0-9])|(?:[2][0-3])|(?:[0-9])):(?:[0-5][0-9])(?::[0-5][0-9])?(?:\\s?(?:am|AM|pm|PM))?)'	# HourMinuteSec 1

        rg = re.compile(re1+re2+re3+re4+re5,re.IGNORECASE|re.DOTALL)
        m = rg.search(line)
        if m:
            word1=m.group(1)
            mmddyyyy1=m.group(2)
            time1=m.group(3)
            #print "("+word1+")"+"("+mmddyyyy1+")"+"("+time1+")"+"\n"
            self.metrics_entry[word1] = time1

    def get_avail(self,line):
        re1='(avail)'	# Word 1
        re2='.*?'	# Non-greedy match on filler
        re3='([+-]?\\d*\\.\\d+)(?![-+0-9\\.])'	# Float 1

        rg = re.compile(re1+re2+re3,re.IGNORECASE|re.DOTALL)
        m = rg.search(line)
        if m:
            word1=m.group(1)
            float1=m.group(2)
            #print "("+word1+")"+"("+float1+")"+"\n"
            self.metrics_entry[word1] = float1

    def regParseLineHeadKeyIntValue(self, txt):
        re1='((?:[a-z][a-z0-9_]*))'	# Variable Name 1
        re2='.*?'	# Non-greedy match on filler
        re3='(\\d+)'	# Integer Number 1

        rg = re.compile(re1+re2+re3,re.IGNORECASE|re.DOTALL)
        m = rg.search(txt)
        if m:
            var1=m.group(1)
            int1=m.group(2)
            #print "("+var1+")"+"("+int1+")"+"\n"
            return (var1, int1)
        return ('unknown',0)

    def get_testNum(self, txt):
        re1='(testNum)'	# Word 1
        re2='.*?'	# Non-greedy match on filler
        re3='(\\d+)'	# Integer Number 1

        rg = re.compile(re1+re2+re3,re.IGNORECASE|re.DOTALL)
        m = rg.search(txt)
        if m:
            word1=m.group(1)
            int1=m.group(2)
            #print "("+word1+")"+"("+int1+")"+"\n"
            self.metrics_entry[word1] = int1

    def get_pktStats(self, txt):
        (k,v) = self.regParseLineHeadKeyIntValue(txt)
        self.metrics_entry[k] = v

    def get_rttStats(self, txt):
        (k,v) = self.regParseLineHeadKeyIntValue(txt)
        self.metrics_entry[k] = v

    def get_jitStats(self, txt):
        re1='((?:[a-z][a-z0-9_]*))'	# Variable Name 1
        re2='.*?'	# Non-greedy match on filler
        re3='(\\d+)'	# Integer Number 1
        re4='(\\/)'	# Any Single Character 1
        re5='.*?'	# Non-greedy match on filler
        re6='(\\d+)'	# Integer Number 2

        rg = re.compile(re1+re2+re3+re4+re5+re6,re.IGNORECASE|re.DOTALL)
        m = rg.search(txt)
        if m:
            var1=m.group(1)
            int1=m.group(2)
            c1=m.group(3)
            int2=m.group(4)
            #print "("+var1+")"+"("+int1+")"+"("+c1+")"+"("+int2+")"+"\n"
            self.metrics_entry[var1+'SD'] = int1
            self.metrics_entry[var1+'DS'] = int2

    def getMetric(self, line):
        keyStr = str(line).split(' ')[0]
        if (keyStr == "time"):
            self.get_time(line)
        if (keyStr == "avail"):
            self.get_avail(line)
        if (keyStr == 'testNum'):
            self.get_testNum(line)
        if (keyStr.startswith('pkt')):
            self.get_pktStats(line)
        if (keyStr.startswith('rtt')):
            self.get_pktStats(line)
        if (keyStr.startswith('posJit') or
            keyStr.startswith('negJit') or
            keyStr.startswith('interArrJit') or
            keyStr.startswith('peakToPeakJit') ):
            self.get_jitStats(line)

    def handleShowStatsCfmSlaTest(self, lines):
        """
        :return: list of lines in the CLI response

        HN4000-1M# cpe 1001 show statistics cfmSlaTest 1

        CPE 1001 (OVN404-CP) CFM SLA Test 1 (SLA-1) statistics:

        Keyword           Description                               Value
        ----------------  ----------------------------------------  --------------------
        time              Start time of last test iteration         04/22/2015 13:05:49
        avail             Service availability (%)                  0.000

        Test values:
        testNum           Number of tests                                    1

        Packet values:
        pktNum            Number of packets                                 10
        pktFail           Number of failed packets                          10
        pktLoss           Packet loss                                        0
        pktOOS            Packets out of sequence                            0
        pktLate           Number of late packets                             0

        Round trip time values (ms):
        rttNum            RTT number                                         0
        rttSum            RTT sum                                            0
        rttSum2           RTT sum2                                           0
        rttMin            RTT minimum                                        0
        rttMax            RTT maximum                                        0
        rttAvg            RTT Average                                        0

        Jitter values (us) (SD = source to destination, DS = destination to source):
        interArrJit       Interarrival jitter      (in/out)                  0/        0
        peakToPeakJit     Peak-to-peak jitter      (SD/DS)                   0/        0
        posJitNum         Positive jitter number   (SD/DS)                   0/        0
        posJitSum         Positive jitter sum      (SD/DS)                   0/        0
        posJitSum2        Positive jitter sum2     (SD/DS)                   0/        0
        posJitMin         Positive jitter minimum  (SD/DS)                   0/        0
        posJitMax         Positive jitter maximum  (SD/DS)                   0/        0
        negJitNum         Negative jitter number   (SD/DS)                   0/        0
        negJitSum         Negative jitter sum      (SD/DS)                   0/        0
        negJitSum2        Negative jitter sum2     (SD/DS)                   0/        0
        negJitMin         Negative jitter minimum  (SD/DS)                   0/        0
        negJitMax         Negative jitter maximum  (SD/DS)                   0/        0
        """
        self.metrics_entry = {}
        for line in lines:
            self.getMetric(line)

    def getTestInstance(self, txt):
        txt='1001/1 (SLA-1)    1 (MEP1001)       acti  7 days, 04:20:40    101'

        re1='(\\d+)'	# Integer Number 1
        re2='(\\/)'	# Any Single Character 1
        re3='(\\d+)'	# Integer Number 2
        re4='.*?'	# Non-greedy match on filler
        re5='(\\()'	# Any Single Character 2 (
        re6='(.*?)'	# Non-greedy match on filler
        re7='(\\))'	# Any Single Character 3 )
        re8='.*?'	# Non-greedy match on filler
        re9='(\\d+)'	# Integer Number 3
        re10='.*?'	# Non-greedy match on filler
        re11='(\\()'	# Any Single Character 4
        re12='(.*?)'	# Non-greedy match on filler
        re13='(\\))'	# Any Single Character 5
        re14='.*?'	# Non-greedy match on filler
        re15='((?:[a-z][a-z]+))'	# Word 1
        re16='.*?'	# Non-greedy match on filler
        re17='\\d+'	# Uninteresting: int
        re18='.*?'	# Non-greedy match on filler
        re19='\\d+'	# Uninteresting: int
        re20='.*?'	# Non-greedy match on filler
        re21='\\d+'	# Uninteresting: int
        re22='.*?'	# Non-greedy match on filler
        re23='\\d+'	# Uninteresting: int
        re24='.*?'	# Non-greedy match on filler
        re25='(\\d+)'	# Integer Number 4

        rg = re.compile(re1+re2+re3+re4+re5+re6+re7+re8+re9+re10+re11+re12+re13+re14+re15+re16+re17+re18+re19+re20+re21+re22+re23+re24+re25,re.IGNORECASE|re.DOTALL)
        m = rg.search(txt)
        if m:
            cpeId=m.group(1)
            c1=m.group(2)
            testId=m.group(3)
            c2=m.group(4)
            testName=m.group(5)
            c3=m.group(6)
            mepId=m.group(7)
            c4=m.group(8)
            mepName=m.group(9)
            c5=m.group(10)
            oper=m.group(11)
            destId=m.group(12)
            print "("+cpeId+")"+"("+testId+")"+"("+testName +")"+"("+mepId+")"+"("+mepName+")"+"("+oper+")"+"("+destId+")"+"\n"


    def handleShowCfmSlaTestList(self, lines):
        """
        HN4000-1M# cpe 1001 show cfmSlaTest *

        CPE CFM SLA Test parameters:

        testId            mepId             oper  timeActive          destination
        ----------------  ----------------  ----  ------------------  -----------------
        1001/1 (SLA-1)    1 (MEP1001)       acti  7 days, 04:20:40    101

        :param lines:
        :return:
        """
        self.test_list = []
        for line in lines:
            self.getTestInstance(line)

    #def get_test_detail_admin(self, txt):
    #def get_test_detail_mepId(self, txt):
    #def get_test_detail_oper(self, txt):
    #def get_test_detail_destMac(self, txt):
    #def get_test_detail_destMepName(self, txt):
    def get_test_detail_destMepTag(self, txt):
        (k,v) = self.regParseLineHeadKeyIntValue(txt)
        self.test_instance[k] = v
    def get_test_detail_testFreq(self, txt):
        (k,v) = self.regParseLineHeadKeyIntValue(txt)
        self.test_instance[k] = v
    def get_test_detail_iter(self, txt):
        (k,v) = self.regParseLineHeadKeyIntValue(txt)
        self.test_instance[k] = v
    def get_test_detail_size(self, txt):
        (k,v) = self.regParseLineHeadKeyIntValue(txt)
        self.test_instance[k] = v
    def get_test_detail_freq(self, txt):
        (k,v) = self.regParseLineHeadKeyIntValue(txt)
        self.test_instance[k] = v
    def get_test_detail_timeout(self, txt):
        (k,v) = self.regParseLineHeadKeyIntValue(txt)
        self.test_instance[k] = v
    def get_test_detail_priority(self, txt):
        (k,v) = self.regParseLineHeadKeyIntValue(txt)
        self.test_instance[k] = v

    def get_test_instance_detail(self,lines):
        """
        Keyword           Description                               Value
        ----------------  ----------------------------------------  --------------------
        admin             Administrative state                      enable
        mepId             MEP ID                                    1 (MEP1001)
        oper              Operational state                         active
        timeActive        Test runtime                              7 days, 05:17:22
        destMac           Destination MAC address                   na
        destMepName       Destination MEP name                      na
        destMepTag        Destination MEP tag                       101
        testFreq          Test frequency in seconds                 300
        iter              Packet iterations                         10
        size              Packet size                               0
        freq              Packet frequency in msec                  1000
        timeout           Packet timeout in msec                    5000
        priority          VLAN priority                             1
        """
        self.test_instance = {}
        for line in lines:
            keyStr = str(line).split(' ')[0]
            """if (keyStr == "admin"):
                self.get_test_detail_admin(line)
            if (keyStr == "mepId"):
                self.get_test_detail_mepId(line)
            if (keyStr == 'oper'):
                self.get_test_detail_oper(line)
            if (keyStr == 'destMac'):
                self.get_test_detail_destMac(line)
            if (keyStr == 'destMepName'):
                self.get_test_detail_destMepName(line)"""
            if (keyStr == 'destMepTag'):
                self.get_test_detail_destMepTag(line)
            if (keyStr == "testFreq"):
                self.get_test_detail_testFreq(line)
            if (keyStr == "iter"):
                self.get_test_detail_iter(line)
            if (keyStr == 'size'):
                self.get_test_detail_size(line)
            if (keyStr == 'freq'):
                self.get_test_detail_freq(line)
            if (keyStr == 'timeout'):
                self.get_test_detail_timeout(line)
            if (keyStr == 'priority'):
                self.get_test_detail_priority(line)


t = TestIO()
t.readConfig()
t.checkEnvironment()

lines = open("response").readlines()
t.handleShowStatsCfmSlaTest(lines)
#print(t.metrics_entry)
myhost = {'ip':"1.1.2.1", 'type':4000, 'cpe': 1001}
metricsHost = t.metrics_entry.copy()
metricsHost.update(myhost)
t.createReports(**metricsHost)
t.getTestInstance('')
