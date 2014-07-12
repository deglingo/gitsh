#!/usr/bin/python3

import os, readline, subprocess, pwd, socket, shlex
from subprocess import PIPE as CMDPIPE

CONFIG_DIR = os.path.join(os.environ['HOME'], '.gitsh')
HISTORY_FILE = os.path.join(CONFIG_DIR, 'history')
HISTORY_LENGTH = 1000

GIT_COMMAND_CHAR = '!'

def quote_cmd (cmd) :
    # unsafe! only used for logging
    return ' '.join('"%a"' % a if (' ' in a) else a
                    for a in cmd)
        
# cmdexec
def cmdexec (cmd, wait=False, dotrace=True, **kwargs) :
    if dotrace :
        print('> %s' % quote_cmd(cmd))
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
    KEYBOARD_INTERRUPT = 2
    EMPTY = 3
    GITCMD = 4

# GitSHApp
class GitSHApp :

    # main
    @classmethod
    def main (cls) :
        app = cls()
        app.run()

    # run
    def run (self) :
        # create config dir
        if not os.path.isdir(CONFIG_DIR) :
            os.mkdir(CONFIG_DIR)
        # load history
        if os.path.exists(HISTORY_FILE) :
            readline.read_history_file(HISTORY_FILE)
        readline.set_history_length(HISTORY_LENGTH)
        # main loop
        try:
            self._print_log()
            while True :
                self._print_status()
                ltype, line = self._readline()
                if ltype == LineType.COMMIT :
                    self._do_commit(line)
                elif ltype == LineType.EMPTY :
                    print()
                    self._print_log()
                elif ltype == LineType.GITCMD :
                    self._do_gitcmd(line)
                elif ltype == LineType.KEYBOARD_INTERRUPT :
                    print()
                    continue
                else :
                    assert 0, (ltype, line)
        finally:
            readline.write_history_file(HISTORY_FILE)

    # _readline
    def _readline (self) :
        prompt = self._get_prompt()
        try:
            line = input(prompt)
        except KeyboardInterrupt:
            return LineType.KEYBOARD_INTERRUPT, ''
        except:
            raise
        line = line.strip()
        if line == '' :
            return LineType.EMPTY, ''
        elif line[0] == GIT_COMMAND_CHAR :
            line = line[1:].strip()
            return LineType.GITCMD, line
        else :
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

    # _do_gitcmd
    def _do_gitcmd (self, line) :
        cmd = ['git'] + shlex.split(line)
        cmdexec(cmd, wait=True)

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
                    stdout=CMDPIPE, universal_newlines=True, dotrace=False)
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
                    stdout=CMDPIPE, universal_newlines=True, dotrace=False)
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

