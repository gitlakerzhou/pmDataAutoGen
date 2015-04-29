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

class Sessions(object):
	def __init__(self, rootDir):
		self.hosts = []
		self.accounts = []
		self.hosts = get_hosts_from_file(rootDir + "/" + "hosts")
		logging.info("read in hosts"+rootDir + "/" + "hosts")
		if not self.hosts:
			logging.info("EMPTY HOST FILE, exit ...")
			exit(1)
		for h in self.hosts:
			logging.info("host:" + h.get_address())

		self.accounts = get_accounts_from_file(rootDir + "/" + "accounts")
		logging.info("read in accounts"+rootDir + "/" + "accounts")
		if not self.accounts:
			logging.info("EMPTY ACCOUNT FILE, exit ...")
			exit(1)
		for a in self.accounts:
			logging.info("account:" + a.get_name())

	def command_loop(self, job, host, conn):
		conn.autoinit()
		#conn.execute('show config run')
		host = conn.get_host()
		if not conn.is_app_authenticated() or not conn.is_app_authorized():
			logging.info("authentication failed on " + host)
		#resp = conn.response
		#logging.info(resp)

		conn.send('logout force')
		conn.close()

	def parallelExec(self):
		start(self.accounts, self.hosts, self.command_loop, max_threads = 5)

"""
test = Sessions('/var/log/AutoCfmTestReport/')
test.parallelExec()
"""
