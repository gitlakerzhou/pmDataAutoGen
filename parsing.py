import re
import logging

metrics_entry = {}

def get_time(line):
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
            metrics_entry[word1] = time1

def get_avail(line):
        re1='(avail)'	# Word 1
        re2='.*?'	# Non-greedy match on filler
        re3='([+-]?\\d*\\.\\d+)(?![-+0-9\\.])'	# Float 1

        rg = re.compile(re1+re2+re3,re.IGNORECASE|re.DOTALL)
        m = rg.search(line)
        if m:
            word1=m.group(1)
            float1=m.group(2)
            #print "("+word1+")"+"("+float1+")"+"\n"
            metrics_entry[word1] = str(float1)+'%'

def regParseLineHeadKeyIntValue(txt):
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

def get_testNum(txt):
        re1='(testNum)'	# Word 1
        re2='.*?'	# Non-greedy match on filler
        re3='(\\d+)'	# Integer Number 1

        rg = re.compile(re1+re2+re3,re.IGNORECASE|re.DOTALL)
        m = rg.search(txt)
        if m:
            word1=m.group(1)
            int1=m.group(2)
            #print "("+word1+")"+"("+int1+")"+"\n"
            metrics_entry[word1] = int1

def get_pktStats(txt):
        (k,v) = regParseLineHeadKeyIntValue(txt)
        metrics_entry[k] = v


def get_rttStats(txt):
        (k,v) = regParseLineHeadKeyIntValue(txt)
        metrics_entry[k] = v


def get_jitStats(txt):
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
            metrics_entry[var1+'SD'] = int1
            metrics_entry[var1+'DS'] = int2

def getMetric(line):
        keyStr = ''
        words = str(line).split(' ')
        if words:
            keyStr = words[0]

        if (keyStr == "time"):
            get_time(line)
        if (keyStr == "avail"):
            get_avail(line)
        if (keyStr == 'testNum'):
            get_testNum(line)
        if (keyStr.startswith('pkt')):
            get_pktStats(line)
        if (keyStr.startswith('rtt')):
            get_pktStats(line)
        if (keyStr.startswith('posJit') or
            keyStr.startswith('negJit') or
            keyStr.startswith('interArrJit') or
            keyStr.startswith('peakToPeakJit') ):
            get_jitStats(line)

def handleShowStatsCfmSlaTest(lines):
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
        #global metrics_entry
        #metrics_entry = {}
        for line in lines:
            getMetric(line)
            #logging.info(metrics_entry)
        return metrics_entry

def getTestInstance(txt):
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
            logging.info ("("+cpeId+")"+"("+testId+")"+"("+testName +")"+"("+mepId+")"+"("+mepName+")"+"("+oper+")"+"("+destId+")")
            if (oper == 'acti'):
                return testId


def handleShowCfmSlaTestList(lines):
        """
        HN4000-1M# cpe 1001 show cfmSlaTest *

        CPE CFM SLA Test parameters:

        testId            mepId             oper  timeActive          destination
        ----------------  ----------------  ----  ------------------  -----------------
        1001/1 (SLA-1)    1 (MEP1001)       acti  7 days, 04:20:40    101

        :param lines:
        :return:
        """
        ids = [];
        for line in lines:
            id = getTestInstance(line)
            if id:
                ids.append(id)
        logging.info(ids)
        return ids

    #def get_test_detail_admin(txt):
def get_test_detail_mepId(txt):
        #txt='mepId             MEP ID                                    1 (MEP1001)'

        re1='(mepId)'	# Word 1
        re2='(\\s+)'	# White Space 1
        re3='(MEP)'	# Word 2
        re4='( )'	# Any Single Character 1
        re5='(ID)'	# US State 1
        re6='.*?'	# Non-greedy match on filler
        re7='(\\d+)'	# Integer Number 1
        re8='( )'	# Any Single Character 2
        re9='(\\()'	# Any Single Character 3
        re10='((?:[a-z][a-z0-9_]*))'	# Variable Name 1
        re11='(\\))'	# Any Single Character 4

        rg = re.compile(re1+re2+re3+re4+re5+re6+re7+re8+re9+re10+re11,re.IGNORECASE|re.DOTALL)
        m = rg.search(txt)
        if m:
            key=m.group(1)
            ws1=m.group(2)
            word2=m.group(3)
            c1=m.group(4)
            usstate1=m.group(5)
            int1=m.group(6)
            c2=m.group(7)
            c3=m.group(8)
            mepId=m.group(9)
            c4=m.group(10)
            metrics_entry[k] = mepId
            

    #def get_test_detail_oper(txt):
    #def get_test_detail_destMac(txt):
def get_test_detail_destMepName(txt):
        #txt='destMepName       Destination MEP name                      na'

        re1='(destMepName)'	# Word 1
        re2='(\\s+)'	# White Space 1
        re3='(Destination)'	# Word 2
        re4='( )'	# Any Single Character 1
        re5='(MEP)'	# Word 3
        re6='( )'	# Any Single Character 2
        re7='(name)'	# Word 4
        re8='(\\s+)'	# White Space 2
        re9='((?:[a-z][a-z0-9_]*))'	# Variable Name 1

        rg = re.compile(re1+re2+re3+re4+re5+re6+re7+re8+re9,re.IGNORECASE|re.DOTALL)
        m = rg.search(txt)
        if m:
            word1=m.group(1)
            ws1=m.group(2)
            word2=m.group(3)
            c1=m.group(4)
            word3=m.group(5)
            c2=m.group(6)
            word4=m.group(7)
            ws2=m.group(8)
            destMepName=m.group(9)
            metrics_entry[word1] = destMepName

def get_test_detail_destMepTag(txt):
        (k,v) = regParseLineHeadKeyIntValue(txt)
        metrics_entry[k] = v
def get_test_detail_testFreq(txt):
        (k,v) = regParseLineHeadKeyIntValue(txt)
        metrics_entry[k] = v
def get_test_detail_iter(txt):
        (k,v) = regParseLineHeadKeyIntValue(txt)
        metrics_entry[k] = v
def get_test_detail_size(txt):
        (k,v) = regParseLineHeadKeyIntValue(txt)
        metrics_entry[k] = v
def get_test_detail_freq(txt):
        (k,v) = regParseLineHeadKeyIntValue(txt)
        metrics_entry[k] = v
def get_test_detail_timeout(txt):
        (k,v) = regParseLineHeadKeyIntValue(txt)
        metrics_entry[k] = v
def get_test_detail_priority(txt):
        (k,v) = regParseLineHeadKeyIntValue(txt)
        metrics_entry[k] = v

def get_test_instance_detail(lines):
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
        global metrics_entry
        metrics_entry = {}
        keyStr = ''
        for line in lines:
            words = str(line).split(' ')
            """if (keyStr[0] == "admin"):
                get_test_detail_admin(line)
            
            if (keyStr[0] == 'oper'):
                get_test_detail_oper(line)
            if (keyStr[0] == 'destMac'):
                get_test_detail_destMac(line)
            """
            if (words):
                keyStr = words[0]
            else:
                continue
            if (keyStr == "mepId"):
                get_test_detail_mepId(line)
            if (keyStr == 'destMepName'):
                get_test_detail_destMepName(line)
            if (keyStr == 'destMepTag'):
                get_test_detail_destMepTag(line)
            if (keyStr == "testFreq"):
                get_test_detail_testFreq(line)
            if (keyStr == "iter"):
                get_test_detail_iter(line)
            if (keyStr == 'size'):
                get_test_detail_size(line)
            if (keyStr == 'freq'):
                get_test_detail_freq(line)
            if (keyStr == 'timeout'):
                get_test_detail_timeout(line)
            if (keyStr == 'priority'):
                get_test_detail_priority(line)
        return metrics_entry


def handleShowBondingList(lines):
        """
        2BASE-TL port bonding parameters (* = discovered, not preprovisioned):
        
        2basetlId        oper  pme  dot  aggrRat  rmtMacAddress       pmePortList
        ---------------  ----  ---  ---  -------  ------------------  ------------------
        1001             acti  hnb  tru  22.816   *00:05:7a:02:3d:57  1/17-20
        1002             acti  hnb  tru  22.816   *00:05:7a:71:85:6b  1/21-24
        
        """
        bondings = []
        re1='(\\d+)'	# Integer Number 1
        re2='.*?'	# Non-greedy match on filler
        re3='(acti)'	# Word 1

        rg = re.compile(re1+re2+re3,re.IGNORECASE|re.DOTALL)

        for line in lines:
            m = rg.search(line)
            if m:
                bondings.append(m.group(1))
        return bondings

def handleShowStatsPolicerAll(lines):
        """
        CPE Policer statistics:
        
        Instance  age                     cirPass     pirPass     pirDrop
        --------  -------------------  ----------  ----------  ----------
        1001/1    1 days, 02:45:12              0           0           0
        """
        policer_stats = {}
        
        re1='(\\d+)'	# Integer Number 1
        re2='(\\/)'	# Any Single Character 1
        re3='(\\d+)'	# Uninteresting: int
        re4='.*?'	# Non-greedy match on filler
        re5='(\\d+)'	# Integer Number 2
        re6='.*?'	# Non-greedy match on filler
        re7='(days)'	# Variable Name 1
        re8='.*?'	# Non-greedy match on filler
        re9='(\\d+)'	# Integer Number 4
        re10='(:)'	# Any Single Character 2
        re11='(\\d+)'	# Integer Number 5
        re12='(:)'	# Any Single Character 3
        re13='(\\d+)'	# Integer Number 6
        re14='.*?'	# Non-greedy match on filler
        re15='(\\d+)'	# Integer Number 7
        re16='.*?'	# Non-greedy match on filler
        re17='(\\d+)'	# Integer Number 8
        re18='.*?'	# Non-greedy match on filler
        re19='(\\d+)'	# Integer Number 9       
        rg = re.compile(re1+re2+re3+re4+re5+re6+re7+re8+re9+re10+re11+re12+re13+re14+re15+re16+re17+re18+re19,re.IGNORECASE|re.DOTALL)

        for line in lines:
            if line:
                m = rg.search(line)
                if m:
                    policer_stats['cpe']=m.group(1)
                    policer_stats['policerId']=m.group(3)

                    policer_stats['cirPass']=m.group(11)
                    policer_stats['pirPass']=m.group(12)
                    policer_stats['pirDrop']=m.group(13)
        return policer_stats
       
        
