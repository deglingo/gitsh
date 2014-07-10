#!/usr/bin/python3

import os, readline, subprocess, pwd, socket
from subprocess import PIPE as CMDPIPE

# cmdexec
def cmdexec (cmd, wait=False, **kwargs) :
	proc = subprocess.Popen(cmd, **kwargs)
	if wait :
		r = proc.wait()
		assert r == 0, r # [todo]
		return r
	else :
		return proc

# LineType
class LineType :

	COMMIT = 1

# GitSHApp
class GitSHApp :

	# main
	@classmethod
	def main (cls) :
		app = cls()
		app.run()

	# run
	def run (self) :
		self._print_log()
		while True :
			self._print_status()
			ltype, line = self._readline()
			if ltype == LineType.COMMIT :
				self._do_commit(line)
			else :
				assert 0, (ltype, line)

	# _readline
	def _readline (self) :
		prompt = self._get_prompt()
		line = input(prompt)
		return LineType.COMMIT, line

	# _get_prompt
	def _get_prompt (self) :
		user = pwd.getpwuid(os.getuid()).pw_name
		host = socket.gethostname()
		cwd = os.getcwd()
		isgit = True # [todo]
		mark = '$' if isgit else '?'
		prompt = '%s@%s:%s%s ' % (user, host, cwd, mark)
		return prompt

	# _do_commit:
	def _do_commit (self, msg) :
		cmdexec(['git', 'commit', '-a', '-m', msg], wait=True)

	# _print_log
	def _print_log (self) :
		logs = self._get_log()
		sep = ' +' + ('-' * 75) + '+'
		last_date = ''
		print(sep)
		for hash, date, hour, tz, msg in logs :
			print(' | %-10s %s | %s | %-41s |' %
				  ((date if date != last_date else ''),
				   hour, hash[:7], msg[:41]))
			last_date = date
		print(sep)

	# _get_log
	def _get_log (self) :
		logs = []
		p = cmdexec(['git', 'log', '-n', '20', '--format=format:%H %ci %s'],
					stdout=CMDPIPE, universal_newlines=True)
		for line in p.stdout :
			logs.append(line.strip().split(None, 4))
		r = p.wait()
		assert r == 0, r
		return logs

	# _print_status
	def _print_status (self) :
		branch, flist = self._get_status()
		print()
		print(' ## %s' % branch)
		print()
		if flist :
			for stat, fname in flist :
				print(' %s %s' % (stat, fname))
			print()
			
	# _get_status
	def _get_status (self) :
		p = cmdexec(['git', 'status', '--branch', '--porcelain', '--untracked=all'],
					stdout=CMDPIPE, universal_newlines=True)
		branch = p.stdout.readline().strip()
		assert branch[:3] == '## ', branch
		branch = branch.split(None, 1)[1]
		flist = []
		for line in p.stdout :
			flist.append(line.strip().split(None, 1))
		return branch, flist

# exec
if __name__ == '__main__' :
	GitSHApp.main()

