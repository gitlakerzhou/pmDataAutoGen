#!/usr/bin/env python
from Exscript.util.match    import any_match
from Exscript.util.template import eval_file
from Exscript.util.start    import quickstart
from Exscript.util.interact import read_login
from Exscript.protocols import SSH2
from Exscript            import Host
from Exscript.util.file  import get_hosts_from_file, get_accounts_from_file
from Exscript.util.start import start
import test_io
import logging
import parsing
import time

class Sessions(object):
	def __init__(self, io):
		self.hosts = []
		self.accounts = []
		self.io = io
		self.hosts = get_hosts_from_file(self.io.rootDir + "/" + "hosts")
		logging.info("read in hosts" + self.io.rootDir + "/" + "hosts")
		if not self.hosts:
			logging.info("EMPTY HOST FILE, exit ...")
			exit(1)
		for h in self.hosts:
			logging.info("host:" + h.get_address())

		self.accounts = get_accounts_from_file(io.rootDir + "/" + "accounts")
		logging.info("read in accounts" + self.io.rootDir + "/" + "accounts")
		if not self.accounts:
			logging.info("EMPTY ACCOUNT FILE, exit ...")
			exit(1)
		for a in self.accounts:
			logging.info("account:" + a.get_name())

	def command_loop(self, job, host, conn):
		conn.autoinit()
		#conn.execute('show config run')
		host = conn.get_host()
		logging.info(host)
		if not conn.is_app_authenticated() or not conn.is_app_authorized():
			logging.info("authentication failed on " + host)

		#get list of CPEs
		logging.info('show bonding *')
		conn.execute('show bonding *')
		time.sleep(2)
		resp = conn.response.split('\n')
		
		bondings = parsing.handleShowBondingList(resp)
		logging.info(','.join(bondings))
		

		#for each bonding get test instance list
		for b in bondings:
			measurements = {}
			bwm = {}
			pm = {}
			logging.info('show cfmSlaTest *')
			conn.execute('cpe ' + str(b) + ' show cfmSlaTest *')
			resp = conn.response.split('\n')
			instance_ids = parsing.handleShowCfmSlaTestList(resp)
			logging.info(str(b) + ': ' + ','.join(instance_ids))

			#get bandwidth usages
			logging.info('show statis policer *')
			conn.execute('cpe ' + str(b) + ' show statistics policer *')
			
			resp = conn.response.split('\n')
			bwm = parsing.handleShowStatsPolicerAll(resp)
			logging.info(bwm)
			conn.execute('cpe ' + str(b) + ' show policerMapping *')
			resp = conn.response.split('\n')
			pm = parsing.handleShowPolicerMappingAll(resp)
			logging.info(pm)

			#get detailed measurements
			for id in instance_ids:
                                logging.info('show cfmSlaTest ID')
				cmd = 'cpe ' + str(b) + ' show cfmSlaTest ' + id 
				logging.info(cmd)
				conn.execute(cmd)
				
				resp = conn.response.split('\n')
				#logging.info(resp)
				measurements.update(parsing.get_test_instance_detail(resp))
				logging.info(measurements)
				logging.info('show pmstats cfmSlaTest ID')
				cmd = 'cpe ' + str(b) + ' show pmstats cfmSlaTest ' + id + ' startInterval current'
				logging.info(cmd)
				conn.execute(cmd)
				
				resp = conn.response.split('\n')
				#logging.info(resp)
				measurements.update(parsing.handleShowStatsCfmSlaTest(resp))
				
				measurements['ip'] = host
				measurements['type'] = 4000
				measurements['cpe'] = str(b)
				logging.info(measurements)
				#test_io.createReports(self.io, measurements)
				self.io.createReports(**measurements)
				#logging.info(self.io.rootDir)

		conn.send('logout force')
		conn.close()

	def parallelExec(self):
		start(self.accounts, self.hosts, self.command_loop, max_threads = 5)


