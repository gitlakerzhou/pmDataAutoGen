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

class Sessions(object):
	def __init__(self, rootDir):
		#self.rootDir = '/var/log/AutoCfmTestReport/'
		self.hosts = get_hosts_from_file(rootDir + "hosts")
		self.accounts = get_accounts_from_file(rootDir + "accounts")

	def command_loop(self, job, host, conn):
		conn.autoinit()
		conn.execute('show config run')
		print conn.response

		conn.send('logout force')
		conn.close()

	def parallelExec(self):
		start(self.accounts, self.hosts, self.command_loop, max_threads = 5)

"""
test = Sessions('/var/log/AutoCfmTestReport/')
test.parallelExec()
"""
